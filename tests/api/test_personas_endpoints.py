#!/usr/bin/env python3
"""
Test script to verify personas endpoints are working
"""

import requests
import json
import time

def test_personas_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Personas Endpoints")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Services: {', '.join([k for k, v in health_data.items() if v == 'Available'])}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Check available endpoints
    print("\n2. Testing OpenAPI schema...")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = list(openapi_data.get('paths', {}).keys())
            personas_endpoints = [p for p in paths if '/personas' in p]
            
            print(f"✅ OpenAPI: {response.status_code}")
            print(f"   Total endpoints: {len(paths)}")
            print(f"   Personas endpoints found: {len(personas_endpoints)}")
            
            if personas_endpoints:
                print("   Personas endpoints:")
                for endpoint in personas_endpoints:
                    print(f"     - {endpoint}")
            else:
                print("   ❌ No personas endpoints found!")
                return False
                
    except Exception as e:
        print(f"❌ OpenAPI check failed: {e}")
    
    # Test 3: Test personas endpoints
    print("\n3. Testing personas endpoints...")
    
    # Test fallback endpoint
    try:
        response = requests.get(f"{base_url}/api/personas/fallback", timeout=5)
        print(f"✅ Personas fallback: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
    except Exception as e:
        print(f"❌ Personas fallback failed: {e}")
    
    # Test store endpoint (should return 405 Method Not Allowed for GET, not 404)
    try:
        response = requests.get(f"{base_url}/api/personas/store", timeout=5)
        print(f"✅ Personas store (GET): {response.status_code}")
        if response.status_code == 405:
            print("   ✅ Correct! GET not allowed (should use POST)")
        elif response.status_code == 404:
            print("   ❌ Still getting 404 - endpoint not found")
        else:
            print(f"   Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Personas store test failed: {e}")
    
    # Test with POST (should return 422 Unprocessable Entity due to missing data, not 404)
    try:
        response = requests.post(f"{base_url}/api/personas/store", json={}, timeout=5)
        print(f"✅ Personas store (POST empty): {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Correct! Validation error (endpoint exists)")
        elif response.status_code == 404:
            print("   ❌ Still getting 404 - endpoint not found")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Personas store POST test failed: {e}")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    test_personas_endpoints() 