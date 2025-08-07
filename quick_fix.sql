-- QUICK FIX - Add Missing token_usage Column
-- Run this in your Supabase SQL Editor

-- Add the missing token_usage column to responses table
ALTER TABLE responses ADD COLUMN IF NOT EXISTS token_usage JSONB;

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'responses' AND column_name = 'token_usage'; 