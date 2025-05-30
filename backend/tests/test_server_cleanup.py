#!/usr/bin/env python3
"""
Quick test script to check if the personas endpoints are working
"""

import requests
import time
import json

def test_server():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing AI Brand Analysis Backend...")
    
    # Test 1: Health check
    try:
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"Health data: {json.dumps(health_data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test 2: Root endpoint to see available endpoints
    try:
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            root_data = response.json()
            print(f"Available endpoints: {json.dumps(root_data.get('endpoints', {}), indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Root endpoint failed: {e}")
    
    # Test 3: Personas fallback endpoint
    try:
        print("\n3. Testing personas fallback endpoint...")
        response = requests.get(f"{base_url}/api/personas/fallback", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            personas_data = response.json()
            print(f"Personas count: {len(personas_data.get('personas', []))}")
            print("✅ Personas endpoint working!")
        else:
            print(f"❌ Personas endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Personas endpoint failed: {e}")
    
    # Test 4: Check OpenAPI docs to see all endpoints
    try:
        print("\n4. Testing OpenAPI schema...")
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            openapi_data = response.json()
            paths = list(openapi_data.get('paths', {}).keys())
            print(f"All available paths: {paths}")
            
            # Check if personas paths exist
            personas_paths = [path for path in paths if '/personas' in path]
            print(f"Personas paths: {personas_paths}")
            
            if personas_paths:
                print("✅ Personas routes are registered!")
            else:
                print("❌ Personas routes are NOT registered!")
        else:
            print(f"OpenAPI schema failed: {response.text}")
    except Exception as e:
        print(f"OpenAPI schema failed: {e}")

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(3)
    test_server() 