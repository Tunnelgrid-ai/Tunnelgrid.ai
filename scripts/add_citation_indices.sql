-- Migration: Add index range and title to citations table
-- Run this SQL against your Supabase/Postgres database

ALTER TABLE IF EXISTS citations
ADD COLUMN IF NOT EXISTS start_index INTEGER CHECK (start_index IS NULL OR start_index >= 0),
ADD COLUMN IF NOT EXISTS end_index INTEGER CHECK (end_index IS NULL OR end_index >= 0),
ADD COLUMN IF NOT EXISTS title TEXT;

-- Optional helpful indexes
CREATE INDEX IF NOT EXISTS idx_citations_start_index ON citations(start_index);
CREATE INDEX IF NOT EXISTS idx_citations_end_index ON citations(end_index);

