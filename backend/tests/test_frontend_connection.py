#!/usr/bin/env python3
"""
Test frontend-backend connection
"""

import requests
import json

def test_frontend_connection():
    print("🧪 Testing Frontend-Backend Connection...")
    
    try:
        # Test 1: Health check
        print("\n📋 Testing health endpoint...")
        response = requests.get("http://127.0.0.1:8000/api/topics/health")
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy: {data['status']}")
            print(f"✅ GroqAPI: {data['services']['groqapi']}")
        
        # Test 2: Generate topics (same as frontend would call)
        print("\n📋 Testing generate endpoint...")
        payload = {
            "brandName": "Apple",
            "brandDomain": "apple.com", 
            "productName": "iPhone"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/topics/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Generate Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['success']}")
            print(f"✅ Source: {data['source']}")
            print(f"✅ Topics count: {len(data['topics'])}")
            print(f"✅ First topic: {data['topics'][0]['name']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_frontend_connection() 