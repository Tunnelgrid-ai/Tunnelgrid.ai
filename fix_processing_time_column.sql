
-- Fix for missing processing_time_ms column in responses table
-- Run this in your Supabase SQL Editor

-- Add the missing column
ALTER TABLE responses ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;

-- Add the constraint
ALTER TABLE responses ADD CONSTRAINT IF NOT EXISTS valid_processing_time CHECK (processing_time_ms >= 0);

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'responses' AND column_name = 'processing_time_ms';
