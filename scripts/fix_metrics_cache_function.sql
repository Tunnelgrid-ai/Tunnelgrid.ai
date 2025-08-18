-- Fix for the calculate_comprehensive_metrics function
-- The issue is with UUID/text type conversion in the function

-- Drop and recreate the function with proper type handling
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
    
    -- Calculate sentiment distribution
    SELECT jsonb_build_object(
        'positive', COUNT(CASE WHEN sentiment_label = 'positive' THEN 1 END),
        'negative', COUNT(CASE WHEN sentiment_label = 'negative' THEN 1 END),
        'neutral', COUNT(CASE WHEN sentiment_label = 'neutral' THEN 1 END)
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
    
    -- Calculate persona visibility (simplified to avoid UUID issues)
    SELECT jsonb_object_agg(
        p.persona_type,
        jsonb_build_object(
            'total_queries', COALESCE(persona_stats.total_queries, 0),
            'total_responses', COALESCE(persona_stats.total_responses, 0),
            'brand_mentions', COALESCE(persona_stats.brand_mentions, 0),
            'visibility_percentage', COALESCE(persona_stats.visibility_percentage, 0)
        )
    )
    INTO v_persona_visibility
    FROM personas p
    LEFT JOIN (
        SELECT 
            q.persona::text as persona_id,
            COUNT(DISTINCT q.query_id) as total_queries,
            COUNT(DISTINCT r.response_id) as total_responses,
            COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END) as brand_mentions,
            CASE 
                WHEN COUNT(DISTINCT r.response_id) > 0 THEN 
                    ROUND((COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END)::DECIMAL / COUNT(DISTINCT r.response_id) * 100), 2)
                ELSE 0 
            END as visibility_percentage
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        LEFT JOIN responses r ON q.query_id = r.query_id
        LEFT JOIN brand_extractions be ON r.response_id = be.response_id
        WHERE a.audit_id = p_audit_id
        GROUP BY q.persona
    ) persona_stats ON p.persona_id::text = persona_stats.persona_id
    WHERE p.audit_id = p_audit_id;
    
    -- Calculate topic visibility (simplified)
    SELECT jsonb_object_agg(
        t.topic_name,
        jsonb_build_object(
            'total_queries', COALESCE(topic_stats.total_queries, 0),
            'total_responses', COALESCE(topic_stats.total_responses, 0),
            'brand_mentions', COALESCE(topic_stats.brand_mentions, 0),
            'visibility_percentage', COALESCE(topic_stats.visibility_percentage, 0)
        )
    )
    INTO v_topic_visibility
    FROM topics t
    LEFT JOIN (
        SELECT 
            q.topic_name,
            COUNT(DISTINCT q.query_id) as total_queries,
            COUNT(DISTINCT r.response_id) as total_responses,
            COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END) as brand_mentions,
            CASE 
                WHEN COUNT(DISTINCT r.response_id) > 0 THEN 
                    ROUND((COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END)::DECIMAL / COUNT(DISTINCT r.response_id) * 100), 2)
                ELSE 0 
            END as visibility_percentage
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        LEFT JOIN responses r ON q.query_id = r.query_id
        LEFT JOIN brand_extractions be ON r.response_id = be.response_id
        WHERE a.audit_id = p_audit_id
        GROUP BY q.topic_name
    ) topic_stats ON t.topic_name = topic_stats.topic_name
    WHERE t.audit_id = p_audit_id;
    
    -- Calculate persona-topic matrix (simplified)
    SELECT jsonb_agg(
        jsonb_build_object(
            'persona', p.persona_type,
            'topic', t.topic_name,
            'score', COALESCE(matrix_stats.score, 0),
            'total_queries', COALESCE(matrix_stats.total_queries, 0),
            'total_responses', COALESCE(matrix_stats.total_responses, 0),
            'brand_mentions', COALESCE(matrix_stats.brand_mentions, 0)
        )
    )
    INTO v_persona_topic_matrix
    FROM personas p
    CROSS JOIN topics t
    LEFT JOIN (
        SELECT 
            q.persona::text as persona_id,
            q.topic_name,
            COUNT(DISTINCT q.query_id) as total_queries,
            COUNT(DISTINCT r.response_id) as total_responses,
            COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END) as brand_mentions,
            CASE 
                WHEN COUNT(DISTINCT r.response_id) > 0 THEN 
                    ROUND((COUNT(DISTINCT CASE WHEN be.is_target_brand THEN be.extraction_id END)::DECIMAL / COUNT(DISTINCT r.response_id) * 100), 2)
                ELSE 0 
            END as score
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        LEFT JOIN responses r ON q.query_id = r.query_id
        LEFT JOIN brand_extractions be ON r.response_id = be.response_id
        WHERE a.audit_id = p_audit_id
        GROUP BY q.persona, q.topic_name
    ) matrix_stats ON p.persona_id::text = matrix_stats.persona_id AND t.topic_name = matrix_stats.topic_name
    WHERE p.audit_id = p_audit_id AND t.audit_id = p_audit_id;
    
    -- Calculate model performance
    SELECT jsonb_object_agg(
        r.model,
        jsonb_build_object(
            'total_responses', COALESCE(model_stats.total_responses, 0),
            'total_brand_extractions', COALESCE(model_stats.total_brand_extractions, 0),
            'success_rate', COALESCE(model_stats.success_rate, 0)
        )
    )
    INTO v_model_performance
    FROM (
        SELECT DISTINCT r.model
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        JOIN responses r ON q.query_id = r.query_id
        WHERE a.audit_id = p_audit_id
    ) models
    LEFT JOIN (
        SELECT 
            r.model,
            COUNT(DISTINCT r.response_id) as total_responses,
            COUNT(DISTINCT be.extraction_id) as total_brand_extractions,
            CASE 
                WHEN COUNT(DISTINCT r.response_id) > 0 THEN 
                    ROUND((COUNT(DISTINCT be.extraction_id)::DECIMAL / COUNT(DISTINCT r.response_id) * 100), 2)
                ELSE 0 
            END as success_rate
        FROM audit a
        JOIN queries q ON a.audit_id = q.audit_id
        JOIN responses r ON q.query_id = r.query_id
        LEFT JOIN brand_extractions be ON r.response_id = be.response_id
        WHERE a.audit_id = p_audit_id
        GROUP BY r.model
    ) model_stats ON models.model = model_stats.model;
    
    -- Calculate opportunity gaps (simplified)
    SELECT jsonb_agg(
        jsonb_build_object(
            'persona', matrix_item->>'persona',
            'topic', matrix_item->>'topic',
            'current_score', COALESCE((matrix_item->>'score')::DECIMAL, 0),
            'potential_score', LEAST(85, COALESCE((matrix_item->>'score')::DECIMAL, 0) + 30),
            'total_queries', COALESCE((matrix_item->>'total_queries')::INTEGER, 0),
            'priority', CASE 
                WHEN COALESCE((matrix_item->>'total_queries')::INTEGER, 0) >= 3 THEN 'high'
                ELSE 'medium'
            END
        )
    )
    INTO v_opportunity_gaps
    FROM jsonb_array_elements(COALESCE(v_persona_topic_matrix, '[]'::jsonb)) matrix_item
    WHERE COALESCE((matrix_item->>'score')::DECIMAL, 0) < 30 
        AND COALESCE((matrix_item->>'total_queries')::INTEGER, 0) > 0;
    
    -- Calculate content strategy insights (simplified)
    SELECT jsonb_agg(
        jsonb_build_object(
            'topic', topic_name,
            'current_visibility', COALESCE((topic_data->>'visibility_percentage')::DECIMAL, 0),
            'recommended_action', 'Increase content focus',
            'target_visibility', LEAST(85, COALESCE((topic_data->>'visibility_percentage')::DECIMAL, 0) + 25)
        )
    )
    INTO v_content_strategy
    FROM jsonb_each(COALESCE(v_topic_visibility, '{}'::jsonb)) topic_data
    WHERE COALESCE((topic_data.value->>'visibility_percentage')::DECIMAL, 0) < 50;
    
    -- Calculate competitive insights (simplified)
    SELECT jsonb_agg(
        jsonb_build_object(
            'competitor', competitor->>'brand_name',
            'mention_count', COALESCE((competitor->>'mentions')::INTEGER, 0),
            'top_sentiment', (
                SELECT sentiment 
                FROM jsonb_each(competitor->'sentiment_distribution') sentiment_data
                ORDER BY (sentiment_data.value)::INTEGER DESC
                LIMIT 1
            )
        )
    )
    INTO v_competitive_insights
    FROM jsonb_array_elements(COALESCE(v_competitor_analysis, '[]'::jsonb)) competitor
    WHERE COALESCE((competitor->>'mentions')::INTEGER, 0) >= 2;
    
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
        COALESCE(v_persona_topic_matrix, '[]'::jsonb),
        COALESCE(v_model_performance, '{}'::jsonb),
        COALESCE(v_opportunity_gaps, '[]'::jsonb),
        COALESCE(v_content_strategy, '[]'::jsonb),
        COALESCE(v_competitive_insights, '[]'::jsonb),
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

