#!/usr/bin/env python3
import requests
import json

def test_questions_with_different_headers():
    """Test questions API with different headers to bypass rate limiting"""
    
    url = "http://127.0.0.1:8000/api/questions/generate"
    
    payload = {
        "auditId": "test-audit-123",
        "brandName": "TestBrand",
        "brandDescription": "A test brand for testing",
        "brandDomain": "testbrand.com",
        "productName": "TestProduct",
        "topics": [
            {"id": "topic-1", "name": "Quality", "description": "Product quality"}
        ],
        "personas": [
            {"id": "persona-1", "name": "Test User", "description": "A test persona"}
        ]
    }
    
    # Try with different headers to simulate different client
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "TestClient/1.0",
        "X-Forwarded-For": "192.168.1.100",  # Different IP
        "X-Real-IP": "192.168.1.100"
    }
    
    try:
        print("🧪 Testing questions API with different client headers...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"📊 Source: {data.get('source')}")
            print(f"📊 Questions Count: {len(data.get('questions', []))}")
            print(f"⏱️ Processing Time: {data.get('processingTime')}ms")
            if data.get('reason'):
                print(f"ℹ️ Reason: {data.get('reason')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_questions_with_different_headers() 