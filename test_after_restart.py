#!/usr/bin/env python3
"""
Test script to run after server restart
"""

import requests
import time

def test_all_apis():
    print("🧪 Testing all APIs after server restart...")
    print("="*60)
    
    # Test health check first
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get('http://127.0.0.1:8000/api/questions/health', timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health: {result.get('status')}")
            print(f"✅ Services: {result.get('services')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return
    
    # Test topics
    print("\n2️⃣ Testing topics generation...")
    topics_data = {
        "brandName": "Metrolinx",
        "brandDomain": "metrolinx.com", 
        "productName": "GO Transit Services"
    }
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/topics/generate', 
                               json=topics_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Topics Source: {result.get('source')}")
            print(f"✅ Topics Count: {len(result.get('topics', []))}")
        else:
            print(f"❌ Topics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Topics error: {e}")
    
    # Test personas
    print("\n3️⃣ Testing personas generation...")
    personas_data = {
        "brandName": "Metrolinx",
        "brandDescription": "Provincial transit agency",
        "brandDomain": "metrolinx.com",
        "productName": "GO Transit Services",
        "brandId": "brand-123",
        "productId": "product-123",
        "topics": ["Service Reliability", "Customer Experience"]
    }
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/personas/generate',
                               json=personas_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Personas Source: {result.get('source')}")
            print(f"✅ Personas Count: {len(result.get('personas', []))}")
        else:
            print(f"❌ Personas failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Personas error: {e}")
    
    # Test questions
    print("\n4️⃣ Testing questions generation...")
    questions_data = {
        "auditId": "test-audit-123",
        "brandName": "Metrolinx",
        "brandDescription": "Provincial transit agency",
        "brandDomain": "metrolinx.com",
        "productName": "GO Transit Services",
        "topics": [
            {
                "id": "topic-1",
                "name": "Service Reliability",
                "description": "Punctuality and consistency"
            }
        ],
        "personas": [
            {
                "id": "persona-1",
                "name": "Daily Commuter",
                "description": "Regular travelers",
                "demographics": {"ageRange": "25-45"},
                "painPoints": ["Delays"],
                "motivators": ["Reliability"]
            }
        ]
    }
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/questions/generate',
                               json=questions_data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print(f"🎯 Questions Source: {result.get('source')}")
            print(f"🎯 Questions Count: {len(result.get('questions', []))}")
            print(f"🎯 Reason: {result.get('reason', 'N/A')}")
            
            if result.get('source') == 'ai':
                print("🎉 SUCCESS! Questions are now using AI!")
            else:
                print("⚠️ Questions still using fallback")
                
        else:
            print(f"❌ Questions failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Questions error: {e}")
    
    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    test_all_apis() 