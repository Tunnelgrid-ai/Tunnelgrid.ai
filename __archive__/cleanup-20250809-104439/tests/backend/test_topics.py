#!/usr/bin/env python3
"""
Test Topics Generation Backend
"""

import requests
import json

def test_topics_generation():
    print("🎯 Testing Topics Generation API...")
    
    test_data = {
        "brandName": "Metrolinx",
        "brandDomain": "metrolinx.com",
        "productName": "GO Transit Services"
    }
    
    try:
        print("📤 Making request to topics/generate...")
        response = requests.post(
            'http://127.0.0.1:8000/api/topics/generate',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"📊 Source: {result.get('source')}")
            print(f"📊 Topics Count: {len(result.get('topics', []))}")
            print(f"⏱️ Processing Time: {result.get('processingTime')}ms")
            
            if result.get('reason'):
                print(f"ℹ️ Reason: {result.get('reason')}")
                
            # Show first few topics
            topics = result.get('topics', [])
            print(f"\n📝 First 3 Topics:")
            for i, topic in enumerate(topics[:3]):
                print(f"  {i+1}. {topic.get('name', 'No name')}")
                print(f"     Description: {topic.get('description', 'No description')}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_topics_generation() 