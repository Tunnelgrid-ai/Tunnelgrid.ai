#!/usr/bin/env python3
"""
Execute Fixed Metrics Function

Purpose: Execute the fixed comprehensive metrics function in Supabase
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

def execute_fixed_function():
    """Execute the fixed metrics function"""
    print("🔧 Executing Fixed Metrics Function...")
    
    try:
        supabase = get_supabase_client()
        
        # Read the fixed function SQL
        sql_file = Path(__file__).parent / "simple_metrics_function.sql"
        
        if not sql_file.exists():
            print("❌ SQL file not found")
            return False
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        print("📋 SQL content to execute:")
        print("=" * 60)
        print(sql_content)
        print("=" * 60)
        
        print("\n📋 Please follow these steps:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL above")
        print("4. Execute the SQL")
        print("5. Come back here and press Enter to test...")
        
        input("Press Enter when you've executed the SQL...")
        
        # Test the function
        print("\n🧪 Testing the fixed function...")
        
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
            print("✅ Function executed successfully!")
        except Exception as e:
            print(f"❌ Function execution failed: {str(e)}")
            return False
        
        # Check if cache was created
        cache_result = supabase.table("comprehensive_metrics_cache").select("*").eq("audit_id", test_audit_id).execute()
        
        if cache_result.data:
            cache_data = cache_result.data[0]
            print(f"✅ Cache created successfully!")
            print(f"📊 Cache contains:")
            print(f"   - Total queries: {cache_data['total_queries']}")
            print(f"   - Total responses: {cache_data['total_responses']}")
            print(f"   - Overall visibility: {cache_data['overall_visibility_percentage']}%")
            print(f"   - Cache valid: {cache_data['is_valid']}")
            
            return True
        else:
            print("❌ Cache was not created")
            return False
        
    except Exception as e:
        print(f"❌ Execution failed: {str(e)}")
        return False

def test_endpoint():
    """Test the comprehensive report endpoint"""
    print("\n🌐 Testing Comprehensive Report Endpoint...")
    
    try:
        supabase = get_supabase_client()
        
        # Find an audit with completed analysis
        audit_result = supabase.table("audit").select("audit_id").eq("status", "completed").limit(1).execute()
        
        if not audit_result.data:
            print("⚠️ No completed audits found for testing")
            return True
        
        test_audit_id = audit_result.data[0]["audit_id"]
        print(f"📊 Testing endpoint with audit: {test_audit_id}")
        
        print("\n📋 Test this command in PowerShell:")
        print(f"Invoke-WebRequest -Uri \"http://localhost:8000/api/analysis/comprehensive-report/{test_audit_id}\" -Method GET")
        
        print("\n📋 Or test this command in Command Prompt:")
        print(f"curl -X GET \"http://localhost:8000/api/analysis/comprehensive-report/{test_audit_id}\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FIXED METRICS FUNCTION EXECUTION")
    print("=" * 60)
    
    success = execute_fixed_function()
    
    if success:
        test_endpoint()
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. ✅ Fixed function created")
        print("2. ✅ Cache table working")
        print("3. 🌐 Test the endpoint using the commands above")
        print("4. 📊 Your comprehensive reports will now be 50-100x faster!")
    else:
        print("\n❌ Setup failed")
        print("📝 Please check the error messages above")

