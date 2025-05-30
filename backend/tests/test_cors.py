#!/usr/bin/env python3
"""
Test CORS and frontend-like requests
"""

import requests
import json

def test_cors_request():
    print("🧪 Testing CORS and Frontend-like Requests...")
    
    # Simulate a request from frontend running on localhost:8080
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:8080",  # Frontend origin
        "Referer": "http://localhost:8080/",
        "User-Agent": "Mozilla/5.0 (Frontend Test)"
    }
    
    try:
        # Test 1: CORS preflight (OPTIONS request)
        print("\n📋 Testing CORS preflight...")
        response = requests.options(
            "http://127.0.0.1:8000/api/topics/generate",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print(f"Preflight Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        # Test 2: Actual POST request with frontend headers
        print("\n📋 Testing POST with frontend-like headers...")
        payload = {
            "brandName": "Apple",
            "brandDomain": "apple.com", 
            "productName": "iPhone"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/topics/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"POST Status: {response.status_code}")
        print(f"CORS Headers in Response: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['success']}")
            print(f"✅ Topics: {len(data['topics'])}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")

if __name__ == "__main__":
    test_cors_request() 