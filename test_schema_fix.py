#!/usr/bin/env python3
"""
Script to test if processing_time_ms column exists and fix the schema issue
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

# Load environment variables from backend .env file
load_dotenv("backend/.env")

def test_processing_time_column():
    """Test if processing_time_ms column exists by attempting an insert"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🧪 Testing processing_time_ms column...")
        print("=" * 50)
        
        # First, let's check if we have any queries to work with
        try:
            queries_result = supabase.table("queries").select("query_id").limit(1).execute()
            if not queries_result.data:
                print("❌ No queries found in database. Need at least one query to test.")
                return
            
            test_query_id = queries_result.data[0]["query_id"]
            print(f"✅ Found test query: {test_query_id}")
            
        except Exception as e:
            print(f"❌ Error accessing queries table: {e}")
            return
        
        # Test 1: Try to insert with processing_time_ms
        print("\n1. Testing insert WITH processing_time_ms...")
        test_response_id = str(uuid.uuid4())
        
        try:
            test_data = {
                "response_id": test_response_id,
                "query_id": test_query_id,
                "model": "gpt-4-test",
                "response_text": "Test response for schema validation",
                "processing_time_ms": 1500
            }
            
            result = supabase.table("responses").insert(test_data).execute()
            print("✅ SUCCESS: processing_time_ms column exists!")
            
            # Clean up test data
            supabase.table("responses").delete().eq("response_id", test_response_id).execute()
            print("🧹 Cleaned up test data")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            
            # Test 2: Try to insert WITHOUT processing_time_ms
            print("\n2. Testing insert WITHOUT processing_time_ms...")
            test_response_id_2 = str(uuid.uuid4())
            
            try:
                test_data_2 = {
                    "response_id": test_response_id_2,
                    "query_id": test_query_id,
                    "model": "gpt-4-test",
                    "response_text": "Test response without processing time"
                }
                
                result = supabase.table("responses").insert(test_data_2).execute()
                print("✅ SUCCESS: Can insert without processing_time_ms")
                
                # Clean up test data
                supabase.table("responses").delete().eq("response_id", test_response_id_2).execute()
                print("🧹 Cleaned up test data")
                
                # The column is missing - suggest fix
                suggest_column_fix()
                
            except Exception as e2:
                print(f"❌ FAILED even without processing_time_ms: {e2}")
                print("   This suggests a deeper schema issue.")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")

def suggest_column_fix():
    """Suggest how to add the missing column"""
    print("\n" + "=" * 50)
    print("🔧 FIXING THE MISSING COLUMN:")
    print("=" * 50)
    
    print("\nThe processing_time_ms column is missing from the responses table.")
    print("Here are the steps to fix it:")
    
    print("\n1. **Connect to your Supabase database dashboard**")
    print("2. **Go to the SQL Editor**")
    print("3. **Run this SQL command:**")
    print("""
    ALTER TABLE responses ADD COLUMN processing_time_ms INTEGER;
    ALTER TABLE responses ADD CONSTRAINT valid_processing_time CHECK (processing_time_ms >= 0);
    """)
    
    print("\n4. **Or run the complete migration:**")
    print("   - Copy the content from: backend/migrations/phase5_analysis_tables.sql")
    print("   - Execute it in your Supabase SQL Editor")
    
    print("\n5. **Alternative: Remove processing_time_ms from code**")
    print("   - If you don't need processing time tracking")
    print("   - Remove all references to processing_time_ms in the codebase")

def create_fix_sql():
    """Create a SQL file to fix the schema"""
    fix_sql = """
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
"""
    
    with open("fix_processing_time_column.sql", "w") as f:
        f.write(fix_sql)
    
    print("\n📝 Created fix_processing_time_column.sql")
    print("   Run this SQL in your Supabase dashboard to fix the issue.")

if __name__ == "__main__":
    test_processing_time_column()
    create_fix_sql() 