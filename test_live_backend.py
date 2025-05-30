#!/usr/bin/env python3
"""
Test Live Backend - Debug the exact parsing issue
"""

import requests
import json

def test_backend_with_debug():
    print("🧪 Testing Live Backend Question Generation...")
    
    # Use the same test data as our test_api.json
    test_data = {
        "auditId": "test-audit-123",
        "brandName": "Metrolinx",
        "brandDescription": "Provincial transit agency providing GO Transit and UP Express services",
        "brandDomain": "metrolinx.com",
        "productName": "GO Transit Services",
        "topics": [
            {
                "id": "topic-1",
                "name": "Service Reliability",
                "description": "Punctuality and consistency of transit services"
            },
            {
                "id": "topic-2", 
                "name": "Customer Experience",
                "description": "Overall passenger satisfaction and service quality"
            }
        ],
        "personas": [
            {
                "id": "persona-1",
                "name": "Daily Commuter",
                "description": "Regular commuters who rely on GO Transit for their daily work travel",
                "painPoints": ["Long wait times", "Service delays", "Overcrowding"],
                "motivators": ["Reliable schedule", "Cost savings", "Convenience"],
                "demographics": {
                    "ageRange": "25-45",
                    "gender": "Mixed",
                    "location": "GTA",
                    "goals": ["Get to work on time", "Save money", "Reduce stress"]
                }
            },
            {
                "id": "persona-2",
                "name": "Family Traveler",
                "description": "Families using GO Transit for weekend trips and leisure travel",
                "painPoints": ["Complex ticketing", "Limited weekend service", "Lack of family amenities"],
                "motivators": ["Family activities", "Cost-effective travel", "Avoiding traffic"],
                "demographics": {
                    "ageRange": "30-50",
                    "gender": "Mixed",
                    "location": "GTA suburbs",
                    "goals": ["Family bonding", "Explore new places", "Budget-friendly outings"]
                }
            }
        ]
    }
    
    try:
        print("📤 Making request to backend...")
        response = requests.post(
            'http://127.0.0.1:8000/api/questions/generate',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"📊 Source: {result.get('source')}")
            print(f"📊 Questions Count: {len(result.get('questions', []))}")
            print(f"⏱️ Processing Time: {result.get('processingTime')}ms")
            
            if result.get('reason'):
                print(f"ℹ️ Reason: {result.get('reason')}")
                
            # Show first few questions
            questions = result.get('questions', [])
            print(f"\n📝 First 3 Questions:")
            for i, q in enumerate(questions[:3]):
                print(f"  {i+1}. {q.get('text', 'No text')}")
                print(f"     Persona: {q.get('personaId', 'No persona')}")
                print(f"     Topic: {q.get('topicName', 'No topic')}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_backend_with_debug() 