#!/usr/bin/env python3
"""
Test to verify the frontend fix is working correctly
"""

import requests
import json

def test_frontend_fix_verification():
    """Test that the API response matches the fixed frontend types"""
    
    print("🔧 Testing Frontend Fix Verification...")
    
    # Use the same test data from your Postman request
    test_data = {
        "auditId": "test-audit-123",
        "brandName": "TTC",
        "brandDescription": "Provincial transit agency providing GO Transit and UP Express services across the Greater Toronto and Hamilton Area",
        "brandDomain": "TTC.com",
        "productName": "TTC - Toronto transit corporation",
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
            },
            {
                "id": "topic-3",
                "name": "Accessibility",
                "description": "Services for passengers with disabilities"
            }
        ],
        "personas": [
            {
                "id": "persona-1",
                "name": "Daily Commuter",
                "description": "Regular commuters who rely on GO Transit for their daily work travel",
                "painPoints": ["Long wait times", "Service delays", "Crowded trains"],
                "motivators": ["Reliable schedule", "Comfortable journey", "Cost effectiveness"],
                "demographics": {
                    "ageRange": "25-45",
                    "gender": "Mixed",
                    "location": "GTA suburbs",
                    "goals": ["Get to work on time", "Avoid traffic stress"]
                }
            },
            {
                "id": "persona-2",
                "name": "Family Traveler",
                "description": "Families using GO Transit for weekend trips and special events",
                "painPoints": ["Complex ticketing", "Limited family amenities", "Safety concerns"],
                "motivators": ["Family-friendly service", "Convenience", "Safety"],
                "demographics": {
                    "ageRange": "30-50",
                    "gender": "Mixed",
                    "location": "GTA and surrounding areas",
                    "goals": ["Safe family travel", "Affordable outings"]
                }
            }
        ]
    }
    
    try:
        print("📤 Sending request to backend...")
        response = requests.post(
            "http://localhost:8000/api/questions/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', [])
            
            print(f"✅ Success: {data['success']}")
            print(f"📊 Questions Count: {len(questions)}")
            print(f"📊 Source: {data['source']}")
            
            # Validate that all questions have required fields for frontend
            print("\n🔍 VALIDATING FRONTEND TYPE COMPATIBILITY:")
            
            valid_questions = 0
            invalid_questions = 0
            
            for i, question in enumerate(questions):
                has_required_fields = (
                    'id' in question and question['id'] and
                    'text' in question and question['text'] and  
                    'personaId' in question and question['personaId']
                )
                
                if has_required_fields:
                    valid_questions += 1
                    if i < 3:  # Show first 3 for verification
                        print(f"  ✅ Question {i+1}: id='{question['id'][:8]}...', text='{question['text'][:40]}...', personaId='{question['personaId']}'")
                else:
                    invalid_questions += 1
                    print(f"  ❌ Question {i+1} MISSING REQUIRED FIELDS: {question}")
            
            print(f"\n📊 VALIDATION RESULTS:")
            print(f"  Valid questions: {valid_questions}")
            print(f"  Invalid questions: {invalid_questions}")
            
            # Test frontend filtering logic simulation
            print(f"\n🎯 SIMULATING FRONTEND FILTERING:")
            
            personas = test_data['personas']
            questionsByPersona = {}
            
            for persona in personas:
                persona_questions = [q for q in questions if q.get('personaId') == persona['id']]
                questionsByPersona[persona['id']] = persona_questions[:10]
                
                print(f"  📋 {persona['name']} ({persona['id']}): {len(persona_questions)} questions")
                if persona_questions:
                    print(f"    First: '{persona_questions[0]['text'][:50]}...'")
            
            # Final validation
            total_grouped = sum(len(qs) for qs in questionsByPersona.values())
            
            if valid_questions == len(questions) and invalid_questions == 0:
                print(f"\n✅ ALL FRONTEND TYPE VALIDATION PASSED!")
                print(f"   - All {len(questions)} questions have required fields")
                print(f"   - All {total_grouped} questions successfully grouped by persona")
                print(f"   - Frontend should now display questions correctly")
                return True
            else:
                print(f"\n❌ FRONTEND TYPE VALIDATION FAILED!")
                print(f"   - {invalid_questions} questions missing required fields")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_fix_verification()
    if success:
        print("\n🎉 Frontend fix verification PASSED! The frontend should now work correctly.")
    else:
        print("\n💥 Frontend fix verification FAILED! Additional debugging needed.") 