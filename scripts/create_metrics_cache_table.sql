-- =============================================================================
-- COMPREHENSIVE METRICS CACHE TABLE
-- =============================================================================
-- Purpose: Store pre-calculated comprehensive report metrics
-- Benefits: Eliminate runtime joins, instant report access, better performance
-- =============================================================================

-- Drop existing table if it exists
DROP TABLE IF EXISTS comprehensive_metrics_cache CASCADE;

-- Create the comprehensive metrics cache table
CREATE TABLE comprehensive_metrics_cache (
    -- Primary identification
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id UUID NOT NULL UNIQUE,
    
    -- Cache metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cache_version VARCHAR(10) DEFAULT '1.0',
    
    -- Analysis completion tracking
    analysis_completed_at TIMESTAMP WITH TIME ZONE,
    total_queries INTEGER NOT NULL DEFAULT 0,
    total_responses INTEGER NOT NULL DEFAULT 0,
    total_brand_extractions INTEGER NOT NULL DEFAULT 0,
    
    -- Brand Visibility Metrics
    overall_visibility_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
    target_brand_mentions INTEGER NOT NULL DEFAULT 0,
    competitor_mentions INTEGER NOT NULL DEFAULT 0,
    
    -- Sentiment Distribution (JSONB for flexibility)
    sentiment_distribution JSONB NOT NULL DEFAULT '{"positive": 0, "negative": 0, "neutral": 0}',
    
    -- Platform Rankings (Top 10 domains with counts)
    platform_rankings JSONB NOT NULL DEFAULT '[]',
    
    -- Competitor Analysis (Top 5 competitors with details)
    competitor_analysis JSONB NOT NULL DEFAULT '[]',
    
    -- Brand Reach Metrics
    persona_visibility JSONB NOT NULL DEFAULT '{}',
    topic_visibility JSONB NOT NULL DEFAULT '{}',
    
    -- Persona-Topic Matrix (Heatmap data)
    persona_topic_matrix JSONB NOT NULL DEFAULT '[]',
    
    -- Model Performance
    model_performance JSONB NOT NULL DEFAULT '{}',
    
    -- Strategic Insights
    opportunity_gaps JSONB NOT NULL DEFAULT '[]',
    content_strategy JSONB NOT NULL DEFAULT '[]',
    competitive_insights JSONB NOT NULL DEFAULT '[]',
    
    -- Cache status
    is_valid BOOLEAN DEFAULT TRUE,
    last_calculation_error TEXT,
    
    -- Constraints
    CONSTRAINT valid_percentage CHECK (overall_visibility_percentage >= 0 AND overall_visibility_percentage <= 100),
    CONSTRAINT valid_counts CHECK (
        total_queries >= 0 AND 
        total_responses >= 0 AND 
        total_brand_extractions >= 0 AND
        target_brand_mentions >= 0 AND
        competitor_mentions >= 0
    ),
    
    -- Foreign key to audit table
    CONSTRAINT fk_metrics_cache_audit FOREIGN KEY (audit_id) REFERENCES audit(audit_id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_metrics_cache_audit_id ON comprehensive_metrics_cache(audit_id);
CREATE INDEX idx_metrics_cache_created_at ON comprehensive_metrics_cache(created_at DESC);
CREATE INDEX idx_metrics_cache_updated_at ON comprehensive_metrics_cache(updated_at DESC);
CREATE INDEX idx_metrics_cache_valid ON comprehensive_metrics_cache(is_valid) WHERE is_valid = TRUE;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_metrics_cache_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_update_metrics_cache_updated_at
    BEFORE UPDATE ON comprehensive_metrics_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_metrics_cache_updated_at();

-- Create a function to invalidate cache when analysis data changes
CREATE OR REPLACE FUNCTION invalidate_metrics_cache()
RETURNS TRIGGER AS $$
BEGIN
    -- Invalidate cache for the affected audit
    UPDATE comprehensive_metrics_cache 
    SET is_valid = FALSE, 
        last_calculation_error = 'Cache invalidated due to data changes'
    WHERE audit_id = COALESCE(NEW.audit_id, OLD.audit_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create triggers to invalidate cache when relevant data changes
CREATE TRIGGER trigger_invalidate_cache_responses
    AFTER INSERT OR UPDATE OR DELETE ON responses
    FOR EACH ROW
    EXECUTE FUNCTION invalidate_metrics_cache();

CREATE TRIGGER trigger_invalidate_cache_brand_extractions
    AFTER INSERT OR UPDATE OR DELETE ON brand_extractions
    FOR EACH ROW
    EXECUTE FUNCTION invalidate_metrics_cache();

CREATE TRIGGER trigger_invalidate_cache_queries
    AFTER INSERT OR UPDATE OR DELETE ON queries
    FOR EACH ROW
    EXECUTE FUNCTION invalidate_metrics_cache();

-- Create a function to calculate and store comprehensive metrics
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
    
    -- Calculate persona visibility
    SELECT jsonb_object_agg(
        p.persona_type,
        jsonb_build_object(
            'total_queries', persona_stats.total_queries,
            'total_responses', persona_stats.total_responses,
            'brand_mentions', persona_stats.brand_mentions,
            'visibility_percentage', persona_stats.visibility_percentage
        )
    )
    INTO v_persona_visibility
    FROM personas p
    LEFT JOIN (
        SELECT 
            q.persona as persona_id,
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
    ) persona_stats ON p.persona_id = persona_stats.persona_id
    WHERE p.audit_id = p_audit_id;
    
    -- Calculate topic visibility
    SELECT jsonb_object_agg(
        t.topic_name,
        jsonb_build_object(
            'total_queries', topic_stats.total_queries,
            'total_responses', topic_stats.total_responses,
            'brand_mentions', topic_stats.brand_mentions,
            'visibility_percentage', topic_stats.visibility_percentage
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
    
    -- Calculate persona-topic matrix
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
            q.persona as persona_id,
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
    ) matrix_stats ON p.persona_id = matrix_stats.persona_id AND t.topic_name = matrix_stats.topic_name
    WHERE p.audit_id = p_audit_id AND t.audit_id = p_audit_id;
    
    -- Calculate model performance
    SELECT jsonb_object_agg(
        r.model,
        jsonb_build_object(
            'total_responses', model_stats.total_responses,
            'total_brand_extractions', model_stats.total_brand_extractions,
            'success_rate', model_stats.success_rate
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
    
    -- Calculate opportunity gaps (low-performing persona-topic combinations)
    SELECT jsonb_agg(
        jsonb_build_object(
            'persona', matrix_item->>'persona',
            'topic', matrix_item->>'topic',
            'current_score', (matrix_item->>'score')::DECIMAL,
            'potential_score', LEAST(85, (matrix_item->>'score')::DECIMAL + 30),
            'total_queries', (matrix_item->>'total_queries')::INTEGER,
            'priority', CASE 
                WHEN (matrix_item->>'total_queries')::INTEGER >= 3 THEN 'high'
                ELSE 'medium'
            END
        )
    )
    INTO v_opportunity_gaps
    FROM jsonb_array_elements(v_persona_topic_matrix) matrix_item
    WHERE (matrix_item->>'score')::DECIMAL < 30 
        AND (matrix_item->>'total_queries')::INTEGER > 0;
    
    -- Calculate content strategy insights
    SELECT jsonb_agg(
        jsonb_build_object(
            'topic', topic_name,
            'current_visibility', (topic_data->>'visibility_percentage')::DECIMAL,
            'recommended_action', 'Increase content focus',
            'target_visibility', LEAST(85, (topic_data->>'visibility_percentage')::DECIMAL + 25)
        )
    )
    INTO v_content_strategy
    FROM jsonb_each(v_topic_visibility) topic_data
    WHERE (topic_data.value->>'visibility_percentage')::DECIMAL < 50;
    
    -- Calculate competitive insights
    SELECT jsonb_agg(
        jsonb_build_object(
            'competitor', competitor->>'brand_name',
            'mention_count', (competitor->>'mentions')::INTEGER,
            'top_sentiment', (
                SELECT sentiment 
                FROM jsonb_each(competitor->'sentiment_distribution') sentiment_data
                ORDER BY (sentiment_data.value)::INTEGER DESC
                LIMIT 1
            )
        )
    )
    INTO v_competitive_insights
    FROM jsonb_array_elements(v_competitor_analysis) competitor
    WHERE (competitor->>'mentions')::INTEGER >= 2;
    
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
        v_sentiment_distribution,
        v_platform_rankings,
        v_competitor_analysis,
        v_persona_visibility,
        v_topic_visibility,
        v_persona_topic_matrix,
        v_model_performance,
        v_opportunity_gaps,
        v_content_strategy,
        v_competitive_insights,
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

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE ON comprehensive_metrics_cache TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_comprehensive_metrics(UUID) TO authenticated;

-- Add comment
COMMENT ON TABLE comprehensive_metrics_cache IS 'Pre-calculated comprehensive report metrics to avoid runtime joins';
COMMENT ON FUNCTION calculate_comprehensive_metrics(UUID) IS 'Calculate and cache comprehensive metrics for an audit';

