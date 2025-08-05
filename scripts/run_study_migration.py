#!/usr/bin/env python3
"""
STUDY MANAGEMENT MIGRATION SCRIPT

PURPOSE: Run the database migration for study management tables
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import get_supabase_client

def run_migration():
    """Run the study management migration"""
    print("🚀 Starting Study Management Migration...")
    
    # Read the migration SQL file
    migration_file = backend_dir / "migrations" / "phase6_study_management.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("📖 Migration SQL loaded successfully")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Execute the migration
        print("🗄️ Executing migration...")
        result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"❌ Migration failed: {result.error}")
            return False
        
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        print("🔍 Verifying tables...")
        verify_result = supabase.rpc('exec_sql', {
            'sql': """
            SELECT 
                table_name, 
                column_count,
                index_count
            FROM (
                SELECT 
                    'user_studies' as table_name,
                    COUNT(*) as column_count,
                    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'user_studies') as index_count
                FROM information_schema.columns 
                WHERE table_name = 'user_studies'
                UNION ALL
                SELECT 
                    'study_progress_snapshots' as table_name,
                    COUNT(*) as column_count,
                    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'study_progress_snapshots') as index_count
                FROM information_schema.columns 
                WHERE table_name = 'study_progress_snapshots'
                UNION ALL
                SELECT 
                    'study_shares' as table_name,
                    COUNT(*) as column_count,
                    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'study_shares') as index_count
                FROM information_schema.columns 
                WHERE table_name = 'study_shares'
                UNION ALL
                SELECT 
                    'study_templates' as table_name,
                    COUNT(*) as column_count,
                    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'study_templates') as index_count
                FROM information_schema.columns 
                WHERE table_name = 'study_templates'
            ) as table_info
            ORDER BY table_name;
            """
        }).execute()
        
        if hasattr(verify_result, 'data'):
            print("📊 Tables created:")
            for table in verify_result.data:
                print(f"  - {table['table_name']}: {table['column_count']} columns, {table['index_count']} indexes")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        return False

def test_study_api():
    """Test the study API endpoints"""
    print("\n🧪 Testing Study API endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health check
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test studies endpoint
        response = requests.get(f"{base_url}/api/studies")
        if response.status_code in [200, 401]:  # 401 is expected if not authenticated
            print("✅ Studies endpoint accessible")
        else:
            print(f"❌ Studies endpoint failed: {response.status_code}")
            return False
        
        print("✅ Study API tests passed")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("STUDY MANAGEMENT MIGRATION")
    print("=" * 60)
    
    # Run migration
    migration_success = run_migration()
    
    if migration_success:
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        # Test API
        api_success = test_study_api()
        
        if api_success:
            print("\n🎉 All tests passed! Study management is ready to use.")
        else:
            print("\n⚠️ Migration completed but API tests failed.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1) 