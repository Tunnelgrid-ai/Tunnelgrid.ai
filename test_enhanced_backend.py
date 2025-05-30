#!/usr/bin/env python3
"""
Test the enhanced backend with intelligent chunking and improved parsing
"""

import requests
import json

def test_enhanced_backend():
    """Test the enhanced backend with various payload sizes"""
    
    print("🔧 Testing Enhanced Backend with Intelligent Chunking...")
    
    test_cases = [
        {
            "name": "Small Request (2 personas, 3 topics) - Should use single request",
            "personas": 2,
            "topics": 3,
            "expected_strategy": "single"
        },
        {
            "name": "Medium Request (4 personas, 5 topics) - Should use single request", 
            "personas": 4,
            "topics": 5,
            "expected_strategy": "single"
        },
        {
            "name": "Large Request (6 personas, 8 topics) - Should use chunking",
            "personas": 6,
            "topics": 8,
            "expected_strategy": "chunked"
        },
        {
            "name": "Very Large Request (7 personas, 10 topics) - Should use chunking",
            "personas": 7,
            "topics": 10,
            "expected_strategy": "chunked"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print("="*60)
        
        # Generate test payload
        payload = {
            "auditId": f"test-enhanced-{test_case['personas']}-{test_case['topics']}",
            "brandName": "TestBrand Enhanced",
            "brandDescription": "A test brand for enhanced backend testing",
            "brandDomain": "testbrand.com",
            "productName": "Test Product Enhanced",
            "topics": [
                {
                    "id": f"topic-{i}",
                    "name": f"Topic {i}",
                    "description": f"Description for topic {i}"
                }
                for i in range(1, test_case["topics"] + 1)
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
                for i in range(1, test_case["personas"] + 1)
            ]
        }
        
        expected_questions = test_case["personas"] * 10
        print(f"📊 Payload: {test_case['personas']} personas, {test_case['topics']} topics")
        print(f"📊 Expected questions: {expected_questions}")
        print(f"📊 Expected strategy: {test_case['expected_strategy']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/questions/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # Longer timeout for chunked requests
            )
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get('success', False)
                source = data.get('source', 'unknown')
                questions_count = len(data.get('questions', []))
                processing_time = data.get('processingTime', 0)
                token_usage = data.get('tokenUsage')
                reason = data.get('reason')
                
                print(f"✅ Status: {response.status_code}")
                print(f"✅ Success: {success}")
                print(f"📊 Source: {source}")
                print(f"📊 Questions: {questions_count}")
                print(f"⏱️ Processing Time: {processing_time}ms")
                
                if token_usage:
                    print(f"🎯 Token Usage: {token_usage}")
                
                if reason:
                    print(f"ℹ️ Reason: {reason}")
                
                # Analyze result
                if source in ['ai', 'ai_chunked']:
                    print(f"🎉 AI Generation Successful!")
                    
                    if test_case['expected_strategy'] == 'chunked' and source == 'ai_chunked':
                        print(f"✅ Correctly used chunked strategy")
                    elif test_case['expected_strategy'] == 'single' and source == 'ai':
                        print(f"✅ Correctly used single request strategy")
                    else:
                        print(f"⚠️ Strategy mismatch: expected {test_case['expected_strategy']}, got {source}")
                    
                    # Check question distribution
                    personas_found = set()
                    for question in data.get('questions', []):
                        personas_found.add(question.get('personaId'))
                    
                    print(f"📊 Unique personas in questions: {len(personas_found)}")
                    print(f"📊 Expected personas: {test_case['personas']}")
                    
                    if len(personas_found) == test_case['personas']:
                        print(f"✅ All personas have questions")
                    else:
                        print(f"⚠️ Missing personas: {test_case['personas'] - len(personas_found)}")
                
                elif source == 'fallback':
                    print(f"⚠️ Used fallback questions (AI failed)")
                    if reason:
                        print(f"   Reason: {reason}")
                
                else:
                    print(f"❌ Unexpected source: {source}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n🎯 Enhanced Backend Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    test_enhanced_backend() 