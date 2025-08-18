-- Simple Comprehensive Metrics Function (Fixed Version)
-- This version fixes the SQL syntax errors and simplifies the calculations

DROP FUNCTION IF EXISTS calculate_comprehensive_metrics(UUID);

CREATE OR REPLACE FUNCTION calculate_comprehensive_metrics(p_audit_id UUID)
RETURNS VOID AS $$
DECLARE
    v_total_queries INTEGER;
    v_total_responses INTEGER;
    v_total_brand_extractions INTEGER;
    v_target_brand_mentions INTEGER;
    v_competitor_mentions INTEGER;
    v_overall_visibility DECIMAL(5,2);
    v_sentiment_distribution JSONB;
    v_platform_rankings JSONB;
    v_competitor_analysis JSONB;
    v_persona_visibility JSONB;
    v_topic_visibility JSONB;
    v_persona_topic_matrix JSONB;
    v_model_performance JSONB;
    v_opportunity_gaps JSONB;
    v_content_strategy JSONB;
    v_competitive_insights JSONB;
BEGIN
    -- Calculate basic counts
    SELECT 
        COUNT(DISTINCT q.query_id),
        COUNT(DISTINCT r.response_id),
        COUNT(DISTINCT be.extraction_id),
        COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END),
        COUNT(DISTINCT CASE WHEN NOT be.is_target_brand THEN be.extraction_id END)
    INTO 
        v_total_queries,
        v_total_responses,
        v_total_brand_extractions,
        v_target_brand_mentions,
        v_competitor_mentions
    FROM audit a
    LEFT JOIN queries q ON a.audit_id = q.audit_id
    LEFT JOIN responses r ON q.query_id = r.query_id
    LEFT JOIN brand_extractions be ON r.response_id = be.response_id
    WHERE a.audit_id = p_audit_id;
    
    -- Calculate overall visibility percentage
    v_overall_visibility := CASE 
        WHEN v_total_responses > 0 THEN 
            ROUND((v_target_brand_mentions::DECIMAL / v_total_responses * 100), 2)
        ELSE 0 
    END;
    
    -- Calculate sentiment distribution (FIXED: added table alias)
    SELECT jsonb_build_object(
        'positive', COUNT(CASE WHEN be.sentiment_label = 'positive' THEN 1 END),
        'negative', COUNT(CASE WHEN be.sentiment_label = 'negative' THEN 1 END),
        'neutral', COUNT(CASE WHEN be.sentiment_label = 'neutral' THEN 1 END)
    )
    INTO v_sentiment_distribution
    FROM audit a
    JOIN queries q ON a.audit_id = q.audit_id
    JOIN responses r ON q.query_id = r.query_id
    JOIN brand_extractions be ON r.response_id = be.response_id
    WHERE a.audit_id = p_audit_id;
    
    -- Calculate platform rankings (top 10 domains)
    SELECT jsonb_agg(
        jsonb_build_object(
            'domain', domain,
            'count', mention_count
        )
    )
    INTO v_platform_rankings
    FROM (
        SELECT 
            be.source_domain as domain,
            COUNT(*) as mention_count
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        JOIN responses r ON q.query_id = r.query_id
        JOIN brand_extractions be ON r.response_id = be.response_id
        WHERE a.audit_id = p_audit_id 
            AND be.source_domain IS NOT NULL
        GROUP BY be.source_domain
        ORDER BY mention_count DESC
        LIMIT 10
    ) ranked_domains;
    
    -- Calculate competitor analysis (top 5 competitors)
    SELECT jsonb_agg(
        jsonb_build_object(
            'brand_name', brand_name,
            'mentions', mention_count,
            'sentiment_distribution', sentiment_dist
        )
    )
    INTO v_competitor_analysis
    FROM (
        SELECT 
            be.extracted_brand_name as brand_name,
            COUNT(*) as mention_count,
            jsonb_build_object(
                'positive', COUNT(CASE WHEN be.sentiment_label = 'positive' THEN 1 END),
                'negative', COUNT(CASE WHEN be.sentiment_label = 'negative' THEN 1 END),
                'neutral', COUNT(CASE WHEN be.sentiment_label = 'neutral' THEN 1 END)
            ) as sentiment_dist
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        JOIN responses r ON q.query_id = r.query_id
        JOIN brand_extractions be ON r.response_id = be.response_id
        WHERE a.audit_id = p_audit_id 
            AND NOT be.is_target_brand
            AND be.extracted_brand_name IS NOT NULL
        GROUP BY be.extracted_brand_name
        ORDER BY mention_count DESC
        LIMIT 5
    ) competitors;
    
    -- Simplified persona visibility (avoid complex joins)
    SELECT jsonb_build_object(
        'total_personas', COUNT(DISTINCT p.persona_id),
        'total_queries', v_total_queries,
        'total_responses', v_total_responses,
        'brand_mentions', v_target_brand_mentions
    )
    INTO v_persona_visibility
    FROM personas p
    WHERE p.audit_id = p_audit_id;
    
    -- Simplified topic visibility
    SELECT jsonb_build_object(
        'total_topics', COUNT(DISTINCT t.topic_name),
        'total_queries', v_total_queries,
        'total_responses', v_total_responses,
        'brand_mentions', v_target_brand_mentions
    )
    INTO v_topic_visibility
    FROM topics t
    WHERE t.audit_id = p_audit_id;
    
    -- Simplified persona-topic matrix
    SELECT jsonb_build_object(
        'matrix_entries', COUNT(DISTINCT p.persona_id) * COUNT(DISTINCT t.topic_name),
        'total_queries', v_total_queries,
        'overall_visibility', v_overall_visibility
    )
    INTO v_persona_topic_matrix
    FROM personas p, topics t
    WHERE p.audit_id = p_audit_id AND t.audit_id = p_audit_id;
    
    -- Simplified model performance
    SELECT jsonb_build_object(
        'total_responses', v_total_responses,
        'total_brand_extractions', v_total_brand_extractions,
        'success_rate', CASE 
            WHEN v_total_responses > 0 THEN 
                ROUND((v_total_brand_extractions::DECIMAL / v_total_responses * 100), 2)
            ELSE 0 
        END
    )
    INTO v_model_performance;
    
    -- Simplified opportunity gaps
    SELECT jsonb_build_object(
        'low_visibility_areas', CASE 
            WHEN v_overall_visibility < 30 THEN 'High priority'
            WHEN v_overall_visibility < 50 THEN 'Medium priority'
            ELSE 'Low priority'
        END,
        'current_score', v_overall_visibility,
        'target_score', LEAST(85, v_overall_visibility + 25)
    )
    INTO v_opportunity_gaps;
    
    -- Simplified content strategy
    SELECT jsonb_build_object(
        'recommended_action', CASE 
            WHEN v_overall_visibility < 30 THEN 'Increase brand visibility significantly'
            WHEN v_overall_visibility < 50 THEN 'Focus on content optimization'
            ELSE 'Maintain current strategy'
        END,
        'current_visibility', v_overall_visibility
    )
    INTO v_content_strategy;
    
    -- Simplified competitive insights
    SELECT jsonb_build_object(
        'competitor_count', COALESCE(jsonb_array_length(v_competitor_analysis), 0),
        'top_competitor_mentions', CASE 
            WHEN v_competitor_analysis IS NOT NULL AND jsonb_array_length(v_competitor_analysis) > 0 
            THEN (v_competitor_analysis->0->>'mentions')::INTEGER
            ELSE 0
        END
    )
    INTO v_competitive_insights;
    
    -- Insert or update the cache
    INSERT INTO comprehensive_metrics_cache (
        audit_id,
        analysis_completed_at,
        total_queries,
        total_responses,
        total_brand_extractions,
        target_brand_mentions,
        competitor_mentions,
        overall_visibility_percentage,
        sentiment_distribution,
        platform_rankings,
        competitor_analysis,
        persona_visibility,
        topic_visibility,
        persona_topic_matrix,
        model_performance,
        opportunity_gaps,
        content_strategy,
        competitive_insights,
        is_valid
    ) VALUES (
        p_audit_id,
        NOW(),
        v_total_queries,
        v_total_responses,
        v_total_brand_extractions,
        v_target_brand_mentions,
        v_competitor_mentions,
        v_overall_visibility,
        COALESCE(v_sentiment_distribution, '{"positive": 0, "negative": 0, "neutral": 0}'::jsonb),
        COALESCE(v_platform_rankings, '[]'::jsonb),
        COALESCE(v_competitor_analysis, '[]'::jsonb),
        COALESCE(v_persona_visibility, '{}'::jsonb),
        COALESCE(v_topic_visibility, '{}'::jsonb),
        COALESCE(v_persona_topic_matrix, '{}'::jsonb),
        COALESCE(v_model_performance, '{}'::jsonb),
        COALESCE(v_opportunity_gaps, '{}'::jsonb),
        COALESCE(v_content_strategy, '{}'::jsonb),
        COALESCE(v_competitive_insights, '{}'::jsonb),
        TRUE
    )
    ON CONFLICT (audit_id) DO UPDATE SET
        analysis_completed_at = EXCLUDED.analysis_completed_at,
        total_queries = EXCLUDED.total_queries,
        total_responses = EXCLUDED.total_responses,
        total_brand_extractions = EXCLUDED.total_brand_extractions,
        target_brand_mentions = EXCLUDED.target_brand_mentions,
        competitor_mentions = EXCLUDED.competitor_mentions,
        overall_visibility_percentage = EXCLUDED.overall_visibility_percentage,
        sentiment_distribution = EXCLUDED.sentiment_distribution,
        platform_rankings = EXCLUDED.platform_rankings,
        competitor_analysis = EXCLUDED.competitor_analysis,
        persona_visibility = EXCLUDED.persona_visibility,
        topic_visibility = EXCLUDED.topic_visibility,
        persona_topic_matrix = EXCLUDED.persona_topic_matrix,
        model_performance = EXCLUDED.model_performance,
        opportunity_gaps = EXCLUDED.opportunity_gaps,
        content_strategy = EXCLUDED.content_strategy,
        competitive_insights = EXCLUDED.competitive_insights,
        is_valid = TRUE,
        last_calculation_error = NULL;
    
    RAISE NOTICE 'Comprehensive metrics calculated and cached for audit %', p_audit_id;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Update cache with error information
        INSERT INTO comprehensive_metrics_cache (
            audit_id,
            is_valid,
            last_calculation_error
        ) VALUES (
            p_audit_id,
            FALSE,
            SQLERRM
        )
        ON CONFLICT (audit_id) DO UPDATE SET
            is_valid = FALSE,
            last_calculation_error = SQLERRM;
        
        RAISE EXCEPTION 'Failed to calculate comprehensive metrics: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

