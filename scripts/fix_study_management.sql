-- =============================================================================
-- FIX STUDY MANAGEMENT - USE EXISTING AUDIT TABLE
-- =============================================================================
-- 
-- PURPOSE: Add missing columns to existing audit table for study management
-- 
-- RUN THIS IN SUPABASE SQL EDITOR
-- =============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. ADD MISSING COLUMNS TO AUDIT TABLE (IF NEEDED)
-- =============================================================================

-- Add study_name column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'study_name') THEN
        ALTER TABLE audit ADD COLUMN study_name VARCHAR(255);
    END IF;
END $$;

-- Add study_description column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'study_description') THEN
        ALTER TABLE audit ADD COLUMN study_description TEXT;
    END IF;
END $$;

-- Add progress_data column if it doesn't exist (for storing step data)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'progress_data') THEN
        ALTER TABLE audit ADD COLUMN progress_data JSONB DEFAULT '{}';
    END IF;
END $$;

-- Add current_step column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'current_step') THEN
        ALTER TABLE audit ADD COLUMN current_step VARCHAR(50) DEFAULT 'brand_info';
    END IF;
END $$;

-- Add progress_percentage column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'progress_percentage') THEN
        ALTER TABLE audit ADD COLUMN progress_percentage INTEGER DEFAULT 0;
    END IF;
END $$;

-- Add updated_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'updated_at') THEN
        ALTER TABLE audit ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- Add last_accessed_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'audit' AND column_name = 'last_accessed_at') THEN
        ALTER TABLE audit ADD COLUMN last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- =============================================================================
-- 2. CREATE INDEXES FOR PERFORMANCE (IF NOT EXISTS)
-- =============================================================================

-- Index for user_id lookups
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit(user_id);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_audit_status ON audit(status);

-- Index for created_timestamp ordering
CREATE INDEX IF NOT EXISTS idx_audit_created_timestamp ON audit(created_timestamp);

-- Composite index for user + status queries
CREATE INDEX IF NOT EXISTS idx_audit_user_status ON audit(user_id, status);

-- =============================================================================
-- 3. INSERT SAMPLE DATA FOR TESTING (IF NEEDED)
-- =============================================================================

-- Insert a sample brand (if not exists)
INSERT INTO brand (brand_id, brand_name, brand_description, domain) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'Test Brand', 'A test brand for development', 'testbrand.com')
ON CONFLICT (brand_id) DO NOTHING;

-- Insert a sample product (if not exists)
INSERT INTO product (product_id, brand_id, product_name, product_description) VALUES 
('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Test Product', 'A test product for development')
ON CONFLICT (product_id) DO NOTHING;

-- Insert a sample audit/study for testing (if not exists)
INSERT INTO audit (audit_id, user_id, brand_id, product_id, status, study_name, study_description, current_step, progress_percentage) VALUES 
('550e8400-e29b-41d4-a716-446655440002', '72f7b6f6-ce78-41dd-a691-44d1ff8f7a01', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001', 'draft', 'Sample Brand Analysis', 'A sample study for testing', 'brand_info', 0)
ON CONFLICT (audit_id) DO NOTHING;

-- =============================================================================
-- 4. VERIFICATION QUERY
-- =============================================================================

-- Check audit table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'audit' 
ORDER BY ordinal_position;

-- Check indexes on audit table
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'audit';

-- =============================================================================
-- MIGRATION COMPLETE
-- ============================================================================= 