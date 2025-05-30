#!/usr/bin/env python3
"""
Test to verify persona ID handling between frontend and backend
"""

import requests
import json

def test_persona_id_mismatch():
    """Test the actual persona ID values being sent and returned"""
    
    print("🔍 Testing Persona ID Mismatch...")
    
    # Test data that mimics what frontend sends
    test_data = {
        "auditId": "test-audit-123",
        "brandName": "TestBrand",
        "brandDescription": "A test brand",
        "brandDomain": "testbrand.com",
        "productName": "TestProduct",
        "topics": [
            {
                "id": "topic-1",
                "name": "Quality",
                "description": "Product quality"
            }
        ],
        "personas": [
            {
                "id": "persona-1",
                "name": "Test User",
                "description": "A test persona",
                "painPoints": ["price", "reliability"],
                "motivators": ["quality", "value"],
                "demographics": {
                    "ageRange": "25-35",
                    "gender": "Any",
                    "location": "Urban",
                    "goals": ["efficiency"]
                }
            }
        ]
    }
    
    print("📤 Sending personas with IDs:")
    for persona in test_data["personas"]:
        print(f"  - {persona['name']}: {persona['id']}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/questions/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data['success']}")
            print(f"📊 Questions Count: {len(data['questions'])}")
            print(f"📊 Source: {data['source']}")
            
            print("\n📥 Received questions with persona IDs:")
            persona_id_counts = {}
            for i, question in enumerate(data['questions'][:5]):  # Show first 5
                persona_id = question.get('personaId')
                persona_id_counts[persona_id] = persona_id_counts.get(persona_id, 0) + 1
                print(f"  Question {i+1}: personaId='{persona_id}' | text='{question['text'][:50]}...'")
            
            print(f"\n📊 Persona ID distribution:")
            for persona_id, count in persona_id_counts.items():
                print(f"  - '{persona_id}': {count} questions")
            
            # Check if persona IDs match what we sent
            sent_persona_ids = {p['id'] for p in test_data['personas']}
            received_persona_ids = {q.get('personaId') for q in data['questions']}
            
            print(f"\n🔍 ID Comparison:")
            print(f"  Sent persona IDs: {sent_persona_ids}")
            print(f"  Received persona IDs: {received_persona_ids}")
            
            if sent_persona_ids == received_persona_ids:
                print("✅ Persona IDs match perfectly!")
            else:
                print("❌ Persona ID mismatch detected!")
                missing = sent_persona_ids - received_persona_ids
                extra = received_persona_ids - sent_persona_ids
                if missing:
                    print(f"  Missing: {missing}")
                if extra:
                    print(f"  Extra: {extra}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_persona_id_mismatch() 