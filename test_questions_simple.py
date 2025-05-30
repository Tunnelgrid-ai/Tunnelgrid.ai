#!/usr/bin/env python3
"""
Simple Questions Generation Test
"""

import requests
import json

def test_questions_simple():
    print("❓ Testing Questions Generation API...")
    
    # Use the exact same structure that worked for topics/personas
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
            }
        ],
        "personas": [
            {
                "id": "persona-1",
                "name": "Daily Commuter",
                "description": "Regular travelers who rely on GO Transit",
                "demographics": {
                    "ageRange": "25-45",
                    "location": "Greater Toronto Area"
                },
                "painPoints": ["Delays", "Crowding"],
                "motivators": ["Reliability", "Convenience"]
            }
        ]
    }
    
    try:
        print("📤 Making request to questions/generate...")
        response = requests.post(
            'http://127.0.0.1:8000/api/questions/generate',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
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
            print(f"\n❓ First 3 Questions:")
            for i, question in enumerate(questions[:3]):
                print(f"  {i+1}. {question.get('text', 'No text')}")
                print(f"     Persona: {question.get('personaId', 'No persona')}")
                print(f"     Topic: {question.get('topicName', 'No topic')}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_questions_simple() 