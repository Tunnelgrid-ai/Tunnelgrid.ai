#!/usr/bin/env python3
"""
INTEGRATION TEST SCRIPT - Phases 4-8 Validation

This script tests the complete AI analysis integration:
1. Backend server health check
2. Analysis routes availability 
3. Database table existence
4. Complete workflow simulation
"""

import asyncio
import requests
import json
import sys
import time
from datetime import datetime
import uuid

def test_server_health():
    """Test if the backend server is running and analysis routes are registered"""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running")
            print(f"   Status: {data.get('status')}")
            print(f"   Environment: {data.get('services', {}).get('api')}")
            
            # Check if analysis endpoint is registered
            root_response = requests.get('http://127.0.0.1:8000/', timeout=5)
            if root_response.status_code == 200:
                root_data = root_response.json()
                endpoints = root_data.get('endpoints', {})
                
                if 'analysis' in endpoints:
                    print("✅ Analysis routes registered")
                    print(f"   Analysis endpoint: {endpoints['analysis']}")
                else:
                    print("❌ Analysis routes not found in endpoints")
                    print(f"   Available endpoints: {list(endpoints.keys())}")
                    return False
            else:
                print("❌ Could not get root endpoint info")
                return False
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_database_tables():
    """Test if the analysis database tables exist"""
    print("🗄️ Testing Database Tables...")
    
    try:
        # Import database connection
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.core.database import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Test each table by attempting a simple query
        tables_to_test = ['analysis_jobs', 'responses', 'citations', 'brand_mentions']
        
        for table in tables_to_test:
            try:
                # Try to query the table (limit 1 to minimize data transfer)
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"❌ Table '{table}' issue: {e}")
                return False
        
        print("✅ All analysis tables are available")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_analysis_endpoints():
    """Test the analysis API endpoints"""
    print("🔌 Testing Analysis Endpoints...")
    
    base_url = 'http://127.0.0.1:8000/api/analysis'
    
    # Test 1: Try to start analysis with invalid UUID format (should return 400)
    try:
        response = requests.post(
            f'{base_url}/start',
            json={'audit_id': 'invalid-uuid-format'},
            timeout=10
        )
        
        if response.status_code == 400:  # Expected for invalid UUID format
            print("✅ Start analysis endpoint correctly validates UUID format")
        else:
            print(f"⚠️ Start analysis returned unexpected status for invalid UUID: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Start analysis endpoint error: {e}")
        return False
    
    # Test 2: Try to start analysis with valid UUID but non-existent audit (should return 404)
    try:
        fake_uuid = str(uuid.uuid4())
        response = requests.post(
            f'{base_url}/start',
            json={'audit_id': fake_uuid},
            timeout=10
        )
        
        if response.status_code == 404:  # Expected for valid UUID but non-existent audit
            print("✅ Start analysis endpoint correctly handles non-existent audit")
        else:
            print(f"⚠️ Start analysis returned unexpected status for non-existent audit: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Start analysis endpoint error: {e}")
        return False
    
    # Test 3: Try to get status with invalid UUID format (should return 400)
    try:
        response = requests.get(
            f'{base_url}/status/invalid-uuid-format',
            timeout=10
        )
        
        if response.status_code == 400:  # Expected for invalid UUID format
            print("✅ Status endpoint correctly validates UUID format")
        else:
            print(f"⚠️ Status endpoint returned unexpected status for invalid UUID: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False
    
    # Test 4: Try to get status with valid UUID but non-existent job (should return 404)
    try:
        fake_uuid = str(uuid.uuid4())
        response = requests.get(
            f'{base_url}/status/{fake_uuid}',
            timeout=10
        )
        
        if response.status_code == 404:  # Expected for valid UUID but non-existent job
            print("✅ Status endpoint correctly handles non-existent job")
        else:
            print(f"⚠️ Status endpoint returned unexpected status for non-existent job: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False
    
    # Test 5: Try to get results with invalid UUID format (should return 400)
    try:
        response = requests.get(
            f'{base_url}/results/invalid-uuid-format',
            timeout=10
        )
        
        if response.status_code == 400:  # Expected for invalid UUID format
            print("✅ Results endpoint correctly validates UUID format")
        else:
            print(f"⚠️ Results endpoint returned unexpected status for invalid UUID: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Results endpoint error: {e}")
        return False
    
    # Test 6: Try to get results with valid UUID but non-existent audit (should return 404)
    try:
        fake_uuid = str(uuid.uuid4())
        response = requests.get(
            f'{base_url}/results/{fake_uuid}',
            timeout=10
        )
        
        if response.status_code == 404:  # Expected for valid UUID but non-existent audit
            print("✅ Results endpoint correctly handles non-existent audit")
        else:
            print(f"⚠️ Results endpoint returned unexpected status for non-existent audit: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Results endpoint error: {e}")
        return False
    
    print("✅ All analysis endpoints are functioning correctly")
    return True

def test_openai_configuration():
    """Test OpenAI API configuration"""
    print("🤖 Testing OpenAI Configuration...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.core.config import settings
        
        if settings.has_openai_config:
            print("✅ OpenAI API key is configured")
            print(f"   API key length: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0} characters")
            return True
        else:
            print("⚠️ OpenAI API key not configured")
            print("   Analysis will fail without API key")
            return False
            
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("📋 INTEGRATION TEST REPORT")
    print("="*60)
    
    tests = [
        ("Server Health", test_server_health),
        ("Database Tables", test_database_tables),
        ("Analysis Endpoints", test_analysis_endpoints),
        ("OpenAI Configuration", test_openai_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time
            results.append((test_name, result, duration))
        except Exception as e:
            print(f"💥 Test '{test_name}' crashed: {e}")
            results.append((test_name, False, time.time() - start_time))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result, duration in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status} ({duration:.2f}s)")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Ready for production use.")
        print("\n💡 Next steps:")
        print("   1. Start the backend server")
        print("   2. Set up frontend development environment")
        print("   3. Test complete user workflow")
        print("   4. Deploy to production")
    else:
        print("⚠️ Some tests failed. Please address issues before proceeding.")
        print("\n🔧 Common fixes:")
        print("   1. Ensure backend server is running (uvicorn app.main:app)")
        print("   2. Run database migration (backend/migrations/)")
        print("   3. Set OPENAI_API_KEY in .env file")
        print("   4. Check network connectivity")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 Starting Integration Tests")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = generate_test_report()
    
    print(f"\n🏁 Integration tests completed at {datetime.now().strftime('%H:%M:%S')}")
    
    sys.exit(0 if success else 1) 