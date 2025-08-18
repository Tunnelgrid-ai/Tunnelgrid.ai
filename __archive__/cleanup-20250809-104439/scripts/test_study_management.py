#!/usr/bin/env python3
"""
STUDY MANAGEMENT COMPREHENSIVE TEST

PURPOSE: Test the complete study management functionality
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test backend health"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_study_api_endpoints():
    """Test study API endpoints"""
    print("\n🧪 Testing Study API endpoints...")
    
    endpoints = [
        "/api/studies",
        "/api/studies/stats/overview",
        "/api/studies/templates"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 401]:  # 401 is expected if not authenticated
                print(f"✅ {endpoint} - accessible")
            else:
                print(f"❌ {endpoint} - failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - error: {e}")

def test_frontend_components():
    """Test frontend components"""
    print("\n🎨 Testing Frontend Components...")
    
    frontend_files = [
        "frontend/src/services/studyService.ts",
        "frontend/src/pages/MyReportsPage.tsx",
        "frontend/src/components/setup/hooks/useWizardState.ts",
        "frontend/src/components/setup/BrandSetupWizard.tsx"
    ]
    
    for file_path in frontend_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            print(f"✅ {file_path} - exists")
        else:
            print(f"❌ {file_path} - missing")

def test_database_tables():
    """Test database tables"""
    print("\n🗄️ Testing Database Tables...")
    
    try:
        from app.core.database import get_supabase_client
        
        supabase = get_supabase_client()
        
        tables = [
            "user_studies",
            "study_progress_snapshots", 
            "study_shares",
            "study_templates"
        ]
        
        for table in tables:
            try:
                # Try to query the table
                result = supabase.table(table).select("count", count="exact").limit(1).execute()
                print(f"✅ {table} - accessible")
            except Exception as e:
                print(f"❌ {table} - error: {e}")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")

def test_routing():
    """Test routing configuration"""
    print("\n🛣️ Testing Routing Configuration...")
    
    routing_files = [
        "frontend/src/App.tsx",
        "frontend/src/pages/BrandSetupPage.tsx"
    ]
    
    for file_path in routing_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
                if 'setup/:studyId' in content:
                    print(f"✅ {file_path} - study routing configured")
                else:
                    print(f"⚠️ {file_path} - study routing not found")
        else:
            print(f"❌ {file_path} - missing")

def test_backend_routes():
    """Test backend route registration"""
    print("\n🔗 Testing Backend Route Registration...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            if 'studies' in data.get('endpoints', {}):
                print("✅ Studies endpoint registered in main app")
            else:
                print("❌ Studies endpoint not registered in main app")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend route test error: {e}")

def test_migration_files():
    """Test migration files"""
    print("\n📋 Testing Migration Files...")
    
    migration_files = [
        "backend/migrations/phase6_study_management.sql",
        "scripts/run_study_migration.py"
    ]
    
    for file_path in migration_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            print(f"✅ {file_path} - exists")
        else:
            print(f"❌ {file_path} - missing")

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("=" * 70)
    print("STUDY MANAGEMENT COMPREHENSIVE TEST")
    print("=" * 70)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Study API Endpoints", test_study_api_endpoints),
        ("Frontend Components", test_frontend_components),
        ("Database Tables", test_database_tables),
        ("Routing Configuration", test_routing),
        ("Backend Routes", test_backend_routes),
        ("Migration Files", test_migration_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Study management is fully functional.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 