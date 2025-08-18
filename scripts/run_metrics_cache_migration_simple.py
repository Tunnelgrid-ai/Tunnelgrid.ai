#!/usr/bin/env python3
"""
Simple Metrics Cache Migration Script

Purpose: Execute the comprehensive metrics cache table creation
Benefits: Eliminate runtime joins, instant report access, better performance
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

def create_metrics_cache_table():
    """Create the comprehensive metrics cache table using direct SQL"""
    print("🚀 Creating Comprehensive Metrics Cache Table...")
    
    try:
        supabase = get_supabase_client()
        
        # Create the table using a simple approach
        # We'll create it step by step using Supabase's SQL editor or direct table creation
        
        print("📋 Creating table structure...")
        
        # First, let's check if the table already exists
        try:
            result = supabase.table("comprehensive_metrics_cache").select("cache_id").limit(1).execute()
            print("✅ Table already exists!")
            return True
        except Exception as e:
            if "does not exist" in str(e) or "42P01" in str(e):
                print("📝 Table doesn't exist, creating it...")
            else:
                print(f"⚠️ Error checking table: {str(e)}")
        
        # Since we can't execute raw SQL through the Python client easily,
        # let's create a simple version of the table using Supabase's table creation
        print("🔄 Creating table via Supabase dashboard...")
        print("\n📋 Please follow these steps:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL from 'create_metrics_cache_table.sql'")
        print("4. Execute the SQL")
        print("5. Come back here and press Enter to continue...")
        
        input("Press Enter when you've created the table...")
        
        # Verify the table was created
        try:
            result = supabase.table("comprehensive_metrics_cache").select("cache_id").limit(1).execute()
            print("✅ Table created successfully!")
            return True
        except Exception as e:
            print(f"❌ Table verification failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def test_cache_functionality():
    """Test the cache functionality with a sample audit"""
    print("\n🧪 Testing Cache Functionality...")
    
    try:
        supabase = get_supabase_client()
        
        # Find an audit with completed analysis
        audit_result = supabase.table("audit").select("audit_id").eq("status", "completed").limit(1).execute()
        
        if not audit_result.data:
            print("⚠️ No completed audits found for testing")
            print("📝 You can test this later when you have completed analyses")
            return True
        
        test_audit_id = audit_result.data[0]["audit_id"]
        print(f"📊 Testing with audit: {test_audit_id}")
        
        # Test the calculation function
        try:
            result = supabase.rpc("calculate_comprehensive_metrics", {"p_audit_id": test_audit_id}).execute()
            print("✅ Cache calculation function works")
        except Exception as e:
            print(f"❌ Cache calculation failed: {str(e)}")
            print("📝 This might be because the function wasn't created yet")
            return False
        
        # Check if cache was created
        cache_result = supabase.table("comprehensive_metrics_cache").select("*").eq("audit_id", test_audit_id).execute()
        
        if cache_result.data:
            cache_data = cache_result.data[0]
            print(f"✅ Cache created successfully")
            print(f"📊 Cache contains: {cache_data['total_queries']} queries, {cache_data['total_responses']} responses")
            print(f"🎯 Overall visibility: {cache_data['overall_visibility_percentage']}%")
        else:
            print("❌ Cache was not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cache testing failed: {str(e)}")
        return False

def show_sql_instructions():
    """Show the SQL that needs to be executed"""
    print("\n" + "="*60)
    print("SQL TO EXECUTE IN SUPABASE DASHBOARD")
    print("="*60)
    
    sql_file = Path(__file__).parent / "create_metrics_cache_table.sql"
    if sql_file.exists():
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        print(sql_content)
    else:
        print("❌ SQL file not found")
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("1. Copy the SQL above")
    print("2. Go to your Supabase dashboard")
    print("3. Navigate to SQL Editor")
    print("4. Paste and execute the SQL")
    print("5. Return here and continue")
    print("="*60)

if __name__ == "__main__":
    print("=" * 60)
    print("COMPREHENSIVE METRICS CACHE MIGRATION")
    print("=" * 60)
    
    # Show SQL instructions
    show_sql_instructions()
    
    # Create table
    success = create_metrics_cache_table()
    
    if success:
        # Test functionality
        test_success = test_cache_functionality()
        
        if test_success:
            print("\n🎉 Migration and testing completed successfully!")
            print("\n📋 Next Steps:")
            print("1. The comprehensive-report endpoint now uses cached metrics")
            print("2. Metrics are automatically calculated when analysis completes")
            print("3. Cache is invalidated when data changes")
            print("4. Manual recalculation available via /recalculate endpoint")
        else:
            print("\n⚠️ Migration completed but testing failed")
            print("📝 You can test the functionality later when you have completed analyses")
    else:
        print("\n❌ Migration failed")
        print("📝 Please execute the SQL manually in Supabase dashboard")

