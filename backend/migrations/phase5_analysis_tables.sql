-- =============================================================================
-- PHASE 5: AI ANALYSIS DATABASE TABLES
-- =============================================================================
-- Purpose: Create comprehensive database schema for AI brand analysis
-- Tables: analysis_jobs, responses, citations, brand_mentions
-- Features: Proper indexing, constraints, and relationships
-- =============================================================================

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS brand_mentions CASCADE;
DROP TABLE IF EXISTS citations CASCADE;
DROP TABLE IF EXISTS responses CASCADE;
DROP TABLE IF EXISTS analysis_jobs CASCADE;

-- 1. ANALYSIS JOBS TABLE
-- Tracks overall analysis job status and progress
-- =============================================================================
CREATE TABLE analysis_jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    audit_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_queries INTEGER NOT NULL DEFAULT 0,
    completed_queries INTEGER NOT NULL DEFAULT 0,
    failed_queries INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'partial_failure')),
    CONSTRAINT valid_counts CHECK (
        completed_queries >= 0 AND 
        failed_queries >= 0 AND 
        total_queries >= 0 AND
        (completed_queries + failed_queries) <= total_queries
    ),
    
    -- Foreign key to audit table
    CONSTRAINT fk_analysis_jobs_audit FOREIGN KEY (audit_id) REFERENCES audit(audit_id) ON DELETE CASCADE
);

-- 2. RESPONSES TABLE  
-- Stores individual AI model responses for each query
-- =============================================================================
CREATE TABLE responses (
    response_id VARCHAR(255) PRIMARY KEY,
    query_id VARCHAR(255) NOT NULL,
    model VARCHAR(100) NOT NULL,
    response_text TEXT NOT NULL,
    processing_time_ms INTEGER,
    token_usage JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_processing_time CHECK (processing_time_ms >= 0),
    CONSTRAINT non_empty_response CHECK (LENGTH(TRIM(response_text)) > 0),
    
    -- Foreign key to queries table
    CONSTRAINT fk_responses_query FOREIGN KEY (query_id) REFERENCES queries(query_id) ON DELETE CASCADE
);

-- 3. CITATIONS TABLE
-- Stores citations and references extracted from AI responses
-- =============================================================================
CREATE TABLE citations (
    citation_id VARCHAR(255) PRIMARY KEY,
    response_id VARCHAR(255) NOT NULL,
    citation_text TEXT NOT NULL,
    source_url TEXT,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT non_empty_citation CHECK (LENGTH(TRIM(citation_text)) > 0),
    CONSTRAINT valid_url CHECK (
        source_url IS NULL OR 
        source_url ~ '^https?://[^\s<>"{}|\\^`[\]]+(\.[^\s<>"{}|\\^`[\]]+)*$'
    ),
    
    -- Foreign key to responses table
    CONSTRAINT fk_citations_response FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
);

-- 4. BRAND MENTIONS TABLE
-- Stores brand mentions extracted from AI responses with sentiment analysis
-- =============================================================================
CREATE TABLE brand_mentions (
    mention_id VARCHAR(255) PRIMARY KEY,
    response_id VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    mention_context TEXT NOT NULL,
    sentiment_score DECIMAL(3,2),
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT non_empty_brand CHECK (LENGTH(TRIM(brand_name)) > 0),
    CONSTRAINT non_empty_context CHECK (LENGTH(TRIM(mention_context)) > 0),
    CONSTRAINT valid_sentiment CHECK (sentiment_score IS NULL OR (sentiment_score >= -1.0 AND sentiment_score <= 1.0)),
    
    -- Foreign key to responses table
    CONSTRAINT fk_brand_mentions_response FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================================================

-- Analysis Jobs Indexes
CREATE INDEX idx_analysis_jobs_audit_id ON analysis_jobs(audit_id);
CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);
CREATE INDEX idx_analysis_jobs_created_at ON analysis_jobs(created_at);

-- Responses Indexes  
CREATE INDEX idx_responses_query_id ON responses(query_id);
CREATE INDEX idx_responses_model ON responses(model);
CREATE INDEX idx_responses_created_at ON responses(created_at);

-- Citations Indexes
CREATE INDEX idx_citations_response_id ON citations(response_id);
CREATE INDEX idx_citations_extracted_at ON citations(extracted_at);

-- Brand Mentions Indexes
CREATE INDEX idx_brand_mentions_response_id ON brand_mentions(response_id);
CREATE INDEX idx_brand_mentions_brand_name ON brand_mentions(brand_name);
CREATE INDEX idx_brand_mentions_sentiment ON brand_mentions(sentiment_score);
CREATE INDEX idx_brand_mentions_extracted_at ON brand_mentions(extracted_at);

-- Composite indexes for common queries
CREATE INDEX idx_brand_mentions_brand_sentiment ON brand_mentions(brand_name, sentiment_score);
CREATE INDEX idx_responses_query_model ON responses(query_id, model);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE analysis_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_mentions ENABLE ROW LEVEL SECURITY;

-- Policy for analysis_jobs: Users can only access their own audit data
CREATE POLICY analysis_jobs_policy ON analysis_jobs
    FOR ALL USING (
        audit_id IN (
            SELECT audit_id FROM audit 
            WHERE user_id = auth.uid()::text
        )
    );

-- Policy for responses: Users can only access responses for their queries
CREATE POLICY responses_policy ON responses
    FOR ALL USING (
        query_id IN (
            SELECT q.query_id FROM queries q
            JOIN audit a ON q.audit_id = a.audit_id
            WHERE a.user_id = auth.uid()::text
        )
    );

-- Policy for citations: Users can only access citations for their responses
CREATE POLICY citations_policy ON citations
    FOR ALL USING (
        response_id IN (
            SELECT r.response_id FROM responses r
            JOIN queries q ON r.query_id = q.query_id
            JOIN audit a ON q.audit_id = a.audit_id
            WHERE a.user_id = auth.uid()::text
        )
    );

-- Policy for brand_mentions: Users can only access mentions for their responses
CREATE POLICY brand_mentions_policy ON brand_mentions
    FOR ALL USING (
        response_id IN (
            SELECT r.response_id FROM responses r
            JOIN queries q ON r.query_id = q.query_id
            JOIN audit a ON q.audit_id = a.audit_id
            WHERE a.user_id = auth.uid()::text
        )
    );

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function to get analysis progress for an audit
CREATE OR REPLACE FUNCTION get_analysis_progress(audit_id_param TEXT)
RETURNS TABLE (
    total_queries INTEGER,
    completed_queries INTEGER,
    failed_queries INTEGER,
    progress_percentage DECIMAL(5,2),
    total_responses INTEGER,
    total_citations INTEGER,
    total_brand_mentions INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        aj.total_queries,
        aj.completed_queries,
        aj.failed_queries,
        CASE 
            WHEN aj.total_queries > 0 THEN 
                ROUND((aj.completed_queries::DECIMAL / aj.total_queries::DECIMAL) * 100, 2)
            ELSE 0.00
        END as progress_percentage,
        COUNT(DISTINCT r.response_id)::INTEGER as total_responses,
        COUNT(DISTINCT c.citation_id)::INTEGER as total_citations,
        COUNT(DISTINCT bm.mention_id)::INTEGER as total_brand_mentions
    FROM analysis_jobs aj
    LEFT JOIN queries q ON q.audit_id = aj.audit_id
    LEFT JOIN responses r ON r.query_id = q.query_id
    LEFT JOIN citations c ON c.response_id = r.response_id
    LEFT JOIN brand_mentions bm ON bm.response_id = r.response_id
    WHERE aj.audit_id = audit_id_param
    GROUP BY aj.total_queries, aj.completed_queries, aj.failed_queries;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get top brands mentioned for an audit
CREATE OR REPLACE FUNCTION get_top_brands_for_audit(audit_id_param TEXT, limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    brand_name TEXT,
    mention_count INTEGER,
    avg_sentiment DECIMAL(3,2),
    positive_mentions INTEGER,
    negative_mentions INTEGER,
    neutral_mentions INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bm.brand_name::TEXT,
        COUNT(bm.mention_id)::INTEGER as mention_count,
        ROUND(AVG(bm.sentiment_score), 2) as avg_sentiment,
        COUNT(CASE WHEN bm.sentiment_score > 0.1 THEN 1 END)::INTEGER as positive_mentions,
        COUNT(CASE WHEN bm.sentiment_score < -0.1 THEN 1 END)::INTEGER as negative_mentions,
        COUNT(CASE WHEN bm.sentiment_score BETWEEN -0.1 AND 0.1 OR bm.sentiment_score IS NULL THEN 1 END)::INTEGER as neutral_mentions
    FROM brand_mentions bm
    JOIN responses r ON bm.response_id = r.response_id
    JOIN queries q ON r.query_id = q.query_id
    WHERE q.audit_id = audit_id_param
    GROUP BY bm.brand_name
    ORDER BY mention_count DESC, avg_sentiment DESC NULLS LAST
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- SAMPLE DATA QUERIES FOR TESTING
-- =============================================================================

-- Insert sample analysis job (commented out for production)
/*
INSERT INTO analysis_jobs (job_id, audit_id, status, total_queries, completed_queries)
VALUES ('sample-job-123', 'test-audit-456', 'completed', 5, 5);

INSERT INTO responses (response_id, query_id, model, response_text, processing_time_ms)
VALUES ('sample-response-123', 'test-query-789', 'openai-4o', 'Apple makes great phones but Samsung is also competitive.', 1500);

INSERT INTO citations (citation_id, response_id, citation_text, source_url)
VALUES ('sample-citation-123', 'sample-response-123', 'According to TechCrunch', 'https://techcrunch.com');

INSERT INTO brand_mentions (mention_id, response_id, brand_name, mention_context, sentiment_score)
VALUES 
    ('sample-mention-1', 'sample-response-123', 'Apple', 'Apple makes great phones', 0.8),
    ('sample-mention-2', 'sample-response-123', 'Samsung', 'Samsung is also competitive', 0.6);
*/

-- =============================================================================
-- CLEANUP COMMANDS (for development)
-- =============================================================================

-- To drop all analysis tables:
-- DROP TABLE IF EXISTS brand_mentions, citations, responses, analysis_jobs CASCADE;

COMMIT; 