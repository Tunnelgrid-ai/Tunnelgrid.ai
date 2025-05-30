#!/usr/bin/env python3
"""
Test if backend can read API key correctly
"""

import requests

def test_api_key():
    print("🔑 Testing API key accessibility in backend...")
    
    try:
        # Test questions health endpoint
        response = requests.get('http://127.0.0.1:8000/api/questions/health')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Questions Health Check:")
            print(f"   Status: {result.get('status')}")
            print(f"   Services: {result.get('services')}")
            print()
        
        # Test topics health endpoint
        response = requests.get('http://127.0.0.1:8000/api/topics/health')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Topics Health Check:")
            print(f"   Status: {result.get('status')}")
            print(f"   Services: {result.get('services')}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_key() 