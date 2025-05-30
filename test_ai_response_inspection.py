#!/usr/bin/env python3
"""
Test to inspect the actual AI response for large payloads
"""

import requests
import json

def test_ai_response_inspection():
    """Inspect what the AI actually returns for large payloads"""
    
    print("🔍 Inspecting AI Response for Large Payload...")
    
    # Test with medium payload that fails
    payload = {
        "auditId": "ai-response-test",
        "brandName": "TestBrand",
        "brandDescription": "A test brand for AI response analysis",
        "brandDomain": "testbrand.com",
        "productName": "Test Product",
        "topics": [
            {"id": f"topic-{i}", "name": f"Topic {i}", "description": f"Description for topic {i}"}
            for i in range(1, 6)  # 5 topics
        ],
        "personas": [
            {
                "id": f"persona-{i}",
                "name": f"Persona {i}",
                "description": f"Description for persona {i}",
                "painPoints": [f"Pain point {i}.1", f"Pain point {i}.2"],
                "motivators": [f"Motivator {i}.1", f"Motivator {i}.2"],
                "demographics": {
                    "ageRange": "25-45",
                    "gender": "Mixed",
                    "location": "Urban",
                    "goals": [f"Goal {i}.1", f"Goal {i}.2"]
                }
            }
            for i in range(1, 5)  # 4 personas (this should trigger fallback)
        ]
    }
    
    print(f"📊 Testing payload: {len(payload['personas'])} personas, {len(payload['topics'])} topics")
    print(f"Expected questions: {len(payload['personas']) * 10} = {len(payload['personas'])} × 10")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/questions/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            source = data.get('source')
            questions_count = len(data.get('questions', []))
            processing_time = data.get('processingTime', 0)
            
            print(f"✅ Success: {data.get('success')}")
            print(f"📊 Source: {source}")
            print(f"📊 Questions: {questions_count}")
            print(f"⏱️ Processing Time: {processing_time}s")
            
            if source == 'fallback':
                print(f"⚠️ FALLBACK REASON: {data.get('reason')}")
                print("\n🧐 This means the AI response failed to parse properly.")
                print("🧐 The AI likely generated questions but they were malformed or truncated.")
                
            elif source == 'ai':
                print(f"🎉 AI Success! Token usage: {data.get('tokenUsage', 'unknown')}")
                
                # Show sample questions
                questions = data.get('questions', [])[:5]
                for i, q in enumerate(questions, 1):
                    print(f"  {i}. {q.get('text', 'No text')[:60]}...")
                    print(f"     Persona: {q.get('personaId')} | Topic: {q.get('topicName')}")
                    
            # Check for any additional debug info
            if 'debug' in data:
                print(f"\n🐛 Debug info: {data['debug']}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_ai_response_inspection() 