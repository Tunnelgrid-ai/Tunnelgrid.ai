#!/usr/bin/env python3
"""
Script to check database schema and verify if processing_time_ms column exists
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from backend .env file
load_dotenv("backend/.env")

def check_database_schema():
    """Check the current database schema"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in environment variables")
        return
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔍 Checking database schema...")
        print("=" * 50)
        
        # Check if responses table exists
        try:
            result = supabase.table("responses").select("*").limit(1).execute()
            print("✅ Responses table exists")
        except Exception as e:
            print(f"❌ Responses table does not exist: {e}")
            return
        
        # Check table structure using PostgreSQL information_schema
        try:
            # Query to get column information for responses table
            query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'responses' 
            ORDER BY ordinal_position;
            """
            
            result = supabase.rpc('exec_sql', {'sql': query}).execute()
            
            if result.data:
                print("\n📋 Responses table columns:")
                print("-" * 30)
                for column in result.data:
                    print(f"  {column['column_name']:<20} {column['data_type']:<15} {'NULL' if column['is_nullable'] == 'YES' else 'NOT NULL'}")
                
                # Check specifically for processing_time_ms
                columns = [col['column_name'] for col in result.data]
                if 'processing_time_ms' in columns:
                    print("\n✅ processing_time_ms column exists")
                else:
                    print("\n❌ processing_time_ms column is MISSING!")
                    print("   This is causing the database error.")
            else:
                print("❌ Could not retrieve column information")
                
        except Exception as e:
            print(f"❌ Error checking table structure: {e}")
            
        # Check if other analysis tables exist
        tables_to_check = ['analysis_jobs', 'citations', 'brand_mentions']
        
        print(f"\n🔍 Checking other analysis tables:")
        for table in tables_to_check:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"  ✅ {table} table exists")
            except Exception as e:
                print(f"  ❌ {table} table missing: {e}")
        
        # Check recent migrations
        print(f"\n📋 Checking recent database changes:")
        try:
            # Try to get recent data from responses table
            result = supabase.table("responses").select("response_id, created_at").limit(5).execute()
            if result.data:
                print(f"  ✅ Responses table has {len(result.data)} recent records")
            else:
                print("  ℹ️  Responses table is empty")
        except Exception as e:
            print(f"  ❌ Error checking responses data: {e}")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")

def suggest_fix():
    """Suggest how to fix the schema issue"""
    print("\n" + "=" * 50)
    print("🔧 SUGGESTED FIXES:")
    print("=" * 50)
    
    print("\n1. **Run the migration manually:**")
    print("   - Connect to your Supabase database")
    print("   - Execute the SQL from: backend/migrations/phase5_analysis_tables.sql")
    
    print("\n2. **Add the missing column:**")
    print("   ALTER TABLE responses ADD COLUMN processing_time_ms INTEGER;")
    print("   ALTER TABLE responses ADD CONSTRAINT valid_processing_time CHECK (processing_time_ms >= 0);")
    
    print("\n3. **Check migration status:**")
    print("   - Verify all migrations have been applied")
    print("   - Check if there are any pending migrations")
    
    print("\n4. **Alternative: Remove the column from code:**")
    print("   - If you don't need processing time tracking")
    print("   - Remove processing_time_ms from all database operations")

if __name__ == "__main__":
    check_database_schema()
    suggest_fix() 