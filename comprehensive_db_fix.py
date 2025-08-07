#!/usr/bin/env python3
"""
Comprehensive Database Schema Analysis and Fix Script
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

# Load environment variables from backend .env file
load_dotenv("backend/.env")

def analyze_database_schema():
    """Comprehensive analysis of database schema issues"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔍 COMPREHENSIVE DATABASE SCHEMA ANALYSIS")
        print("=" * 60)
        
        # Test all required columns for responses table
        test_responses_schema(supabase)
        
        # Test other analysis tables
        test_analysis_tables(supabase)
        
        # Generate comprehensive fix
        generate_comprehensive_fix()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")

def test_responses_schema(supabase):
    """Test the responses table schema"""
    print("\n📋 TESTING RESPONSES TABLE SCHEMA")
    print("-" * 40)
    
    # Get a test query ID
    try:
        queries_result = supabase.table("queries").select("query_id").limit(1).execute()
        if not queries_result.data:
            print("❌ No queries found in database. Cannot test responses table.")
            return
        
        test_query_id = queries_result.data[0]["query_id"]
        print(f"✅ Found test query: {test_query_id}")
        
    except Exception as e:
        print(f"❌ Error accessing queries table: {e}")
        return
    
    # Test each column individually
    columns_to_test = [
        ("response_id", "VARCHAR(255)"),
        ("query_id", "VARCHAR(255)"),
        ("model", "VARCHAR(100)"),
        ("response_text", "TEXT"),
        ("processing_time_ms", "INTEGER"),
        ("token_usage", "JSONB"),
        ("created_at", "TIMESTAMP")
    ]
    
    missing_columns = []
    
    for column_name, expected_type in columns_to_test:
        print(f"\n🔍 Testing column: {column_name}")
        
        if column_name == "response_id":
            # Test primary key
            test_data = {
                "response_id": str(uuid.uuid4()),
                "query_id": test_query_id,
                "model": "test-model",
                "response_text": "Test response"
            }
        elif column_name == "processing_time_ms":
            # Test processing_time_ms
            test_data = {
                "response_id": str(uuid.uuid4()),
                "query_id": test_query_id,
                "model": "test-model",
                "response_text": "Test response",
                "processing_time_ms": 1500
            }
        elif column_name == "token_usage":
            # Test token_usage
            test_data = {
                "response_id": str(uuid.uuid4()),
                "query_id": test_query_id,
                "model": "test-model",
                "response_text": "Test response",
                "token_usage": {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}
            }
        else:
            # Skip other columns for now
            continue
        
        try:
            result = supabase.table("responses").insert(test_data).execute()
            print(f"  ✅ {column_name} column exists and works")
            
            # Clean up test data
            supabase.table("responses").delete().eq("response_id", test_data["response_id"]).execute()
            
        except Exception as e:
            error_msg = str(e)
            if "Could not find" in error_msg and column_name in error_msg:
                print(f"  ❌ {column_name} column is MISSING!")
                missing_columns.append(column_name)
            else:
                print(f"  ⚠️  {column_name} column exists but has issues: {e}")
    
    return missing_columns

def test_analysis_tables(supabase):
    """Test other analysis tables"""
    print("\n📋 TESTING OTHER ANALYSIS TABLES")
    print("-" * 40)
    
    tables_to_check = [
        'analysis_jobs',
        'citations', 
        'brand_mentions'
    ]
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"  ✅ {table} table exists")
        except Exception as e:
            print(f"  ❌ {table} table missing: {e}")

def generate_comprehensive_fix():
    """Generate comprehensive SQL fix"""
    print("\n" + "=" * 60)
    print("🔧 COMPREHENSIVE DATABASE FIX")
    print("=" * 60)
    
    comprehensive_sql = """
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
        source_url ~ '^https?://[^\s<>"{}|\\^`[\]]+(\.[^\s<>"{}|\\^`[\]]+)*$'
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
"""
    
    with open("comprehensive_db_fix.sql", "w") as f:
        f.write(comprehensive_sql)
    
    print("\n📝 Created comprehensive_db_fix.sql")
    print("   This file contains ALL the SQL needed to fix your database schema.")
    print("   Run this in your Supabase SQL Editor to fix all issues at once.")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Go to your Supabase dashboard")
    print("2. Open the SQL Editor")
    print("3. Copy and paste the content from comprehensive_db_fix.sql")
    print("4. Run the SQL")
    print("5. Test the application again")

if __name__ == "__main__":
    analyze_database_schema() 