-- =============================================================================
-- Migration: Remove source_url constraint from brand_extractions table
-- =============================================================================
-- Purpose: Allow NULL or empty source_url values while keeping source_domain
-- This provides more flexibility since domain info is often available without full URL
-- =============================================================================

-- Remove the check constraint that requires non-empty source_url
ALTER TABLE IF EXISTS brand_extractions 
DROP CONSTRAINT IF EXISTS non_empty_source_url;

-- Verify the constraint is removed
-- You can check by running: 
-- SELECT conname, contype FROM pg_constraint WHERE conrelid = 'brand_extractions'::regclass;

-- Optional: Add comment to document the change
COMMENT ON COLUMN brand_extractions.source_url IS 'Full article URL - can be NULL if only domain is available';
COMMENT ON COLUMN brand_extractions.source_domain IS 'Source domain name - primary source identifier';
