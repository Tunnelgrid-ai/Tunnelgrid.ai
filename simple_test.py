#!/usr/bin/env python3
"""
Simple test script to check if personas endpoints are working
"""

import requests
import json
import time
import sys

def test_personas():
    base_url = "http://127.0.0.1:8000"
    
    print("=== TESTING PERSONAS ENDPOINTS ===")
    print("Testing server availability...")
    
    # First, test if server is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Server is running - Status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Services: {health_data}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running or not responding: {e}")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
        return False
    
    # Test OpenAPI schema to see what endpoints are available
    print("\nChecking available endpoints...")
    try:
        openapi_response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            paths = list(openapi_data.get("paths", {}).keys())
            print(f"Available endpoints: {paths}")
            
            # Check if personas endpoints are in the list
            personas_endpoints = [path for path in paths if "/api/personas" in path]
            if personas_endpoints:
                print(f"✅ Personas endpoints found: {personas_endpoints}")
            else:
                print("❌ No personas endpoints found in OpenAPI schema")
                return False
        else:
            print(f"❌ Could not get OpenAPI schema: {openapi_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting OpenAPI schema: {e}")
    
    # Test each personas endpoint
    endpoints_to_test = [
        ("GET", "/api/personas/fallback", "Should return fallback personas"),
        ("GET", "/api/personas/by-audit/test-id", "Should return 404 (expected for invalid ID)"),
        ("POST", "/api/personas/generate", "Should return 422 (missing body)"),
        ("POST", "/api/personas/store", "Should return 422 (missing body)")
    ]
    
    print("\nTesting personas endpoints...")
    
    for method, endpoint, description in endpoints_to_test:
        try:
            print(f"\nTesting {method} {endpoint}")
            print(f"Expected: {description}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:  # POST
                response = requests.post(f"{base_url}{endpoint}", 
                                       json={}, 
                                       headers={"Content-Type": "application/json"},
                                       timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 404:
                print("❌ ENDPOINT NOT FOUND - This is the problem!")
            elif response.status_code in [200, 422]:  # 422 is expected for POST without proper body
                print("✅ Endpoint is working")
            else:
                print(f"⚠️  Unexpected status code")
                
            # Print first 200 chars of response
            try:
                response_text = response.text[:200]
                print(f"Response: {response_text}...")
            except:
                pass
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    return True

if __name__ == "__main__":
    success = test_personas()
    if not success:
        sys.exit(1)
    print("\n=== TEST COMPLETE ===") 