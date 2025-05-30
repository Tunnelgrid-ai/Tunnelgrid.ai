#!/usr/bin/env python3
"""
Test Personas Generation Backend
"""

import requests
import json

def test_personas_generation():
    print("👥 Testing Personas Generation API...")
    
    test_data = {
        "brandName": "Metrolinx",
        "brandDescription": "Provincial transit agency providing GO Transit and UP Express services",
        "brandDomain": "metrolinx.com",
        "productName": "GO Transit Services",
        "brandId": "brand-123",
        "productId": "product-123",
        "topics": ["Service Reliability", "Customer Experience"]
    }
    
    try:
        print("📤 Making request to personas/generate...")
        response = requests.post(
            'http://127.0.0.1:8000/api/personas/generate',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"📊 Source: {result.get('source')}")
            print(f"📊 Personas Count: {len(result.get('personas', []))}")
            print(f"⏱️ Processing Time: {result.get('processingTime')}ms")
            
            if result.get('reason'):
                print(f"ℹ️ Reason: {result.get('reason')}")
                
            # Show first few personas
            personas = result.get('personas', [])
            print(f"\n👥 First 3 Personas:")
            for i, persona in enumerate(personas[:3]):
                print(f"  {i+1}. {persona.get('name', 'No name')}")
                print(f"     Description: {persona.get('description', 'No description')}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_personas_generation() 