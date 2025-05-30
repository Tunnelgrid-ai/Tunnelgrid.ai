#!/usr/bin/env python3
"""
HTTP test for Topics API endpoints
"""

import requests
import json
import time

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return False

def test_topics_health():
    """Test topics health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/topics/health", timeout=5)
        print(f"✅ Topics health: {response.status_code}")
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Services: {data['services']}")
        return True
    except Exception as e:
        print(f"❌ Topics health failed: {e}")
        return False

def test_fallback_topics():
    """Test fallback topics endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/topics/fallback", timeout=5)
        print(f"✅ Fallback topics: {response.status_code}")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Source: {data['source']}")
        print(f"Number of topics: {len(data['topics'])}")
        
        for i, topic in enumerate(data['topics'][:3], 1):  # Show first 3
            print(f"  {i}. {topic['name']}")
        
        return len(data['topics']) == 10
    except Exception as e:
        print(f"❌ Fallback topics failed: {e}")
        return False

def test_generate_topics():
    """Test generate topics endpoint"""
    try:
        payload = {
            "brandName": "Apple",
            "brandDomain": "apple.com", 
            "productName": "iPhone",
            "industry": "Technology",
            "additionalContext": "Smartphone analysis"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/topics/generate",
            json=payload,
            timeout=30
        )
        
        print(f"✅ Generate topics: {response.status_code}")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Source: {data['source']}")
        print(f"Number of topics: {len(data['topics'])}")
        
        if 'reason' in data:
            print(f"Reason: {data['reason']}")
        
        for i, topic in enumerate(data['topics'][:3], 1):  # Show first 3
            print(f"  {i}. {topic['name']}")
        
        return len(data['topics']) == 10
    except Exception as e:
        print(f"❌ Generate topics failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 HTTP Topics API Test\n")
    
    # Test server
    server_ok = test_server_health()
    if not server_ok:
        print("\n❌ Server is not running. Please start the server first:")
        print("   cd backend")
        print("   ..\.venv\Scripts\Activate.ps1")
        print("   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        return
    
    print()
    
    # Test topics endpoints
    health_ok = test_topics_health()
    print()
    
    fallback_ok = test_fallback_topics()
    print()
    
    generate_ok = test_generate_topics()
    
    print(f"\n📊 Test Results:")
    print(f"   Server: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"   Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Fallback: {'✅ PASS' if fallback_ok else '❌ FAIL'}")
    print(f"   Generate: {'✅ PASS' if generate_ok else '❌ FAIL'}")
    
    if fallback_ok or generate_ok:
        print("\n🎉 The topics API is working and returns 10 topics!")
    else:
        print("\n⚠️ The topics API has issues.")

if __name__ == "__main__":
    main() 