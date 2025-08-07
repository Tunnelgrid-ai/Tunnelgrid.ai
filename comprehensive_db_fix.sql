
-- COMPREHENSIVE DATABASE SCHEMA FIX
-- Run this in your Supabase SQL Editor to fix all missing columns and tables

-- =============================================================================
-- 1. FIX RESPONSES TABLE
-- =============================================================================

-- Add missing processing_time_ms column
ALTER TABLE responses ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;

-- Add missing token_usage column  
ALTER TABLE responses ADD COLUMN IF NOT EXISTS token_usage JSONB;

-- Add constraints
DO $$
BEGIN
    -- Add processing_time constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'valid_processing_time'
    ) THEN
        ALTER TABLE responses ADD CONSTRAINT valid_processing_time CHECK (processing_time_ms >= 0);
    END IF;
    
    -- Add non_empty_response constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'non_empty_response'
    ) THEN
        ALTER TABLE responses ADD CONSTRAINT non_empty_response CHECK (LENGTH(TRIM(response_text)) > 0);
    END IF;
END $$;

-- =============================================================================
-- 2. CREATE MISSING ANALYSIS TABLES (if they don't exist)
-- =============================================================================

-- Analysis Jobs Table
CREATE TABLE IF NOT EXISTS analysis_jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    audit_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_queries INTEGER DEFAULT 0,
    completed_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    
    -- Constraints
    CONSTRAINT valid_progress CHECK (progress_percentage >= 0.00 AND progress_percentage <= 100.00),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_query_counts CHECK (total_queries >= 0 AND completed_queries >= 0 AND failed_queries >= 0)
);

-- Citations Table
CREATE TABLE IF NOT EXISTS citations (
    citation_id VARCHAR(255) PRIMARY KEY,
    response_id VARCHAR(255) NOT NULL,
    citation_text TEXT NOT NULL,
    source_url TEXT,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT non_empty_citation CHECK (LENGTH(TRIM(citation_text)) > 0),
    CONSTRAINT valid_url CHECK (
        source_url IS NULL OR 
        source_url ~ '^https?://[^\s<>"{}|\^`[\]]+(\.[^\s<>"{}|\^`[\]]+)*$'
    )
);

-- Brand Mentions Table
CREATE TABLE IF NOT EXISTS brand_mentions (
    mention_id VARCHAR(255) PRIMARY KEY,
    response_id VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    mention_context TEXT NOT NULL,
    sentiment_score DECIMAL(3,2),
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT non_empty_brand CHECK (LENGTH(TRIM(brand_name)) > 0),
    CONSTRAINT non_empty_context CHECK (LENGTH(TRIM(mention_context)) > 0),
    CONSTRAINT valid_sentiment CHECK (sentiment_score IS NULL OR (sentiment_score >= -1.0 AND sentiment_score <= 1.0))
);

-- =============================================================================
-- 3. ADD FOREIGN KEY CONSTRAINTS (if they don't exist)
-- =============================================================================

DO $$
BEGIN
    -- Add foreign key from responses to queries if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_responses_query'
    ) THEN
        ALTER TABLE responses ADD CONSTRAINT fk_responses_query 
        FOREIGN KEY (query_id) REFERENCES queries(query_id) ON DELETE CASCADE;
    END IF;
    
    -- Add foreign key from citations to responses if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_citations_response'
    ) THEN
        ALTER TABLE citations ADD CONSTRAINT fk_citations_response 
        FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE;
    END IF;
    
    -- Add foreign key from brand_mentions to responses if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_brand_mentions_response'
    ) THEN
        ALTER TABLE brand_mentions ADD CONSTRAINT fk_brand_mentions_response 
        FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE;
    END IF;
END $$;

-- =============================================================================
-- 4. CREATE INDEXES (if they don't exist)
-- =============================================================================

-- Analysis Jobs Indexes
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_audit_id ON analysis_jobs(audit_id);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status ON analysis_jobs(status);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_created_at ON analysis_jobs(started_at);

-- Responses Indexes  
CREATE INDEX IF NOT EXISTS idx_responses_query_id ON responses(query_id);
CREATE INDEX IF NOT EXISTS idx_responses_model ON responses(model);
CREATE INDEX IF NOT EXISTS idx_responses_created_at ON responses(created_at);

-- Citations Indexes
CREATE INDEX IF NOT EXISTS idx_citations_response_id ON citations(response_id);
CREATE INDEX IF NOT EXISTS idx_citations_extracted_at ON citations(extracted_at);

-- Brand Mentions Indexes
CREATE INDEX IF NOT EXISTS idx_brand_mentions_response_id ON brand_mentions(response_id);
CREATE INDEX IF NOT EXISTS idx_brand_mentions_brand_name ON brand_mentions(brand_name);
CREATE INDEX IF NOT EXISTS idx_brand_mentions_sentiment ON brand_mentions(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_brand_mentions_extracted_at ON brand_mentions(extracted_at);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_brand_mentions_brand_sentiment ON brand_mentions(brand_name, sentiment_score);
CREATE INDEX IF NOT EXISTS idx_responses_query_model ON responses(query_id, model);

-- =============================================================================
-- 5. ENABLE ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE analysis_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_mentions ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- 6. VERIFICATION QUERIES
-- =============================================================================

-- Verify responses table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'responses' 
ORDER BY ordinal_position;

-- Verify all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('responses', 'analysis_jobs', 'citations', 'brand_mentions')
ORDER BY table_name;
