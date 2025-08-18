#!/usr/bin/env python3
"""
Run Metrics Cache Migration Script

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

def run_migration():
    """Run the metrics cache table migration"""
    print("🚀 Running Comprehensive Metrics Cache Migration...")
    
    try:
        # Read the SQL migration file
        migration_file = Path(__file__).parent / "create_metrics_cache_table.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            sql_commands = f.read()
        
        print("📋 Migration SQL loaded successfully")
        
        # Execute the migration
        supabase = get_supabase_client()
        
        # Split SQL into individual commands and execute
        commands = sql_commands.split(';')
        
        for i, command in enumerate(commands):
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    print(f"🔄 Executing command {i+1}/{len(commands)}...")
                    result = supabase.rpc('exec_sql', {'sql': command}).execute()
                    print(f"✅ Command {i+1} executed successfully")
                except Exception as e:
                    if "already exists" in str(e) or "does not exist" in str(e):
                        print(f"⚠️ Command {i+1} skipped (expected): {str(e)[:50]}...")
                    else:
                        print(f"❌ Command {i+1} failed: {str(e)}")
                        return False
        
        print("✅ Migration completed successfully!")
        
        # Verify the table was created
        try:
            result = supabase.table("comprehensive_metrics_cache").select("cache_id").limit(1).execute()
            print("✅ Metrics cache table verified successfully")
        except Exception as e:
            print(f"❌ Table verification failed: {str(e)}")
            return False
        
        return True
        
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
            return True
        
        test_audit_id = audit_result.data[0]["audit_id"]
        print(f"📊 Testing with audit: {test_audit_id}")
        
        # Test the calculation function
        try:
            result = supabase.rpc("calculate_comprehensive_metrics", {"p_audit_id": test_audit_id}).execute()
            print("✅ Cache calculation function works")
        except Exception as e:
            print(f"❌ Cache calculation failed: {str(e)}")
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

if __name__ == "__main__":
    print("=" * 60)
    print("COMPREHENSIVE METRICS CACHE MIGRATION")
    print("=" * 60)
    
    # Run migration
    success = run_migration()
    
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
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)

