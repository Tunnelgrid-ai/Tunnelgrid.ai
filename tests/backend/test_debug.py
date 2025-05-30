#!/usr/bin/env python3
"""
Backend Debug Test - Check what's happening in the parsing
"""

import httpx
import json
import asyncio

async def test_backend():
    print("🧪 Testing Backend Question Generation...")
    
    # Test data
    test_data = {
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
                "description": "Regular commuters",
                "painPoints": ["Long wait times"],
                "motivators": ["Reliable schedule"],
                "demographics": {
                    "ageRange": "25-45",
                    "gender": "Mixed",
                    "location": "GTA",
                    "goals": ["Get to work on time"]
                }
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/api/questions/generate",
            json=test_data,
            timeout=60.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Success: {result.get('success')}")
            print(f"📍 Source: {result.get('source')}")
            print(f"📝 Reason: {result.get('reason')}")
            print(f"📈 Question count: {len(result.get('questions', []))}")
            print(f"⏱️ Processing time: {result.get('processingTime')}ms")
            
            # Show first few questions
            questions = result.get('questions', [])
            for i, q in enumerate(questions[:3]):
                print(f"🔍 Q{i+1}: {q.get('text', '')[:100]}...")
                print(f"    PersonaId: {q.get('personaId')}")
                print(f"    ID: {q.get('id')}")
            
            # Check if these look like fallback questions
            if questions:
                first_text = questions[0].get('text', '').lower()
                if 'specific features' in first_text or 'pricing compared to functionality' in first_text:
                    print("❌ These appear to be FALLBACK questions!")
                else:
                    print("✅ These appear to be AI-generated questions!")
                    
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_backend()) 