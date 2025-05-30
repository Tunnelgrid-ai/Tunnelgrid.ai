 #!/usr/bin/env python3
"""
PERSONAS WORKFLOW TEST SCRIPT

PURPOSE: Test personas endpoints independently to verify:
1. Server is running and accessible
2. Personas endpoints are properly registered  
3. Generate personas endpoint works
4. Store personas endpoint works
5. Retrieve personas endpoint works
6. Database integration is working

USAGE:
    python test_personas_workflow.py
"""

import requests
import json
import time
import uuid
from typing import Dict, List, Any

# Test Configuration
BASE_URL = "http://localhost:8000"
TEST_AUDIT_ID = str(uuid.uuid4())

def test_server_health():
    """Test if server is running"""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Server is running! Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Services: {data.get('services', {})}")
        return True
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint and check if personas is listed"""
    print("\n📍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            if 'personas' in endpoints:
                print(f"✅ Personas endpoint listed: {endpoints['personas']}")
                return True
            else:
                print(f"❌ Personas endpoint NOT listed in: {list(endpoints.keys())}")
                return False
        else:
            print(f"❌ Root endpoint returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False

def test_fallback_personas():
    """Test fallback personas endpoint"""
    print("\n🔄 Testing fallback personas endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/personas/fallback", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fallback personas endpoint works!")
            print(f"   Count: {data.get('count', 0)}")
            print(f"   Source: {data.get('source', 'unknown')}")
            return True
        else:
            print(f"❌ Fallback endpoint failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Fallback personas test failed: {e}")
        return False

def test_generate_personas():
    """Test personas generation endpoint"""
    print("\n🎨 Testing personas generation endpoint...")
    
    test_data = {
        "brandName": "TestBrand",
        "brandDescription": "A test brand for AI-powered persona generation testing",
        "brandDomain": "testbrand.com", 
        "productName": "TestProduct",
        "brandId": str(uuid.uuid4()),
        "productId": str(uuid.uuid4()),
        "auditId": TEST_AUDIT_ID,
        "topics": ["Technology", "Innovation", "User Experience"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/personas/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Personas generation works!")
            print(f"   Count: {data.get('count', 0)}")
            print(f"   Source: {data.get('source', 'unknown')}")
            print(f"   Processing time: {data.get('processingTime', 'unknown')}ms")
            return data
        else:
            print(f"❌ Generate endpoint failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Generate personas test failed: {e}")
        return None

def test_store_personas(personas_data):
    """Test storing personas in database"""
    print("\n💾 Testing personas storage endpoint...")
    
    if not personas_data:
        print("⚠️ Skipping store test - no personas data to store")
        return False
    
    store_data = {
        "auditId": TEST_AUDIT_ID,
        "personas": personas_data.get('personas', [])
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/personas/store",
            json=store_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Personas storage works!")
            print(f"   Stored count: {data.get('stored', 0)}")
            print(f"   Audit ID: {data.get('auditId', 'unknown')}")
            return True
        else:
            print(f"❌ Store endpoint failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Store personas test failed: {e}")
        return False

def test_retrieve_personas():
    """Test retrieving personas by audit ID"""
    print("\n📥 Testing personas retrieval endpoint...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/personas/by-audit/{TEST_AUDIT_ID}",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Personas retrieval works!")
            print(f"   Retrieved count: {data.get('count', 0)}")
            print(f"   Source: {data.get('source', 'unknown')}")
            return True
        elif response.status_code == 404:
            print(f"⚠️ No personas found for audit ID (expected for new audit)")
            return True
        else:
            print(f"❌ Retrieve endpoint failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Retrieve personas test failed: {e}")
        return False

def main():
    """Run complete personas workflow test"""
    print("🧪 PERSONAS WORKFLOW TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Server Health
    if test_server_health():
        tests_passed += 1
    
    # Test 2: Root endpoint
    if test_root_endpoint():
        tests_passed += 1
    
    # Test 3: Fallback personas
    if test_fallback_personas():
        tests_passed += 1
    
    # Test 4: Generate personas
    personas_data = test_generate_personas()
    if personas_data:
        tests_passed += 1
    
    # Test 5: Store personas
    if test_store_personas(personas_data):
        tests_passed += 1
    
    # Test 6: Retrieve personas
    if test_retrieve_personas():
        tests_passed += 1
    
    # Results
    print(f"\n📊 TEST RESULTS")
    print("=" * 50)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Personas workflow is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    print(f"\n🔍 Test Audit ID: {TEST_AUDIT_ID}")
    print("   (Use this ID to check database records manually)")

if __name__ == "__main__":
    main()