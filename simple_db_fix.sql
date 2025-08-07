-- SIMPLE DATABASE FIX - Add Missing Columns Only
-- Run this in your Supabase SQL Editor

-- =============================================================================
-- 1. FIX RESPONSES TABLE - Add Missing Columns
-- =============================================================================

-- Add missing processing_time_ms column (if not already added)
ALTER TABLE responses ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;

-- Add missing token_usage column  
ALTER TABLE responses ADD COLUMN IF NOT EXISTS token_usage JSONB;

-- Add constraints safely
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
-- 2. FIX ANALYSIS_JOBS TABLE - Add Missing Columns
-- =============================================================================

-- Add missing columns to analysis_jobs table
ALTER TABLE analysis_jobs ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE analysis_jobs ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE analysis_jobs ADD COLUMN IF NOT EXISTS error_message TEXT;

-- =============================================================================
-- 3. VERIFICATION QUERIES
-- =============================================================================

-- Verify responses table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'responses' 
ORDER BY ordinal_position;

-- Verify analysis_jobs table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'analysis_jobs' 
ORDER BY ordinal_position; 