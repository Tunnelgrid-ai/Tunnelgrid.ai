#!/usr/bin/env python3
"""
Test using the exact payload the frontend sent to see backend response
"""

import requests
import json

def test_exact_frontend_payload():
    """Test with the exact payload the frontend sent"""
    
    print("🔍 Testing with EXACT frontend payload...")
    
    # This is the exact payload from the debug proxy output
    payload = {
        "auditId": "32e70d47-d373-4775-9ab3-16a97307d590",
        "brandName": "Lovable",
        "brandDescription": "AI-powered web development platform that allows users to create full-stack applications through natural language prompts and visual editing",
        "brandDomain": "lovable.dev",
        "productName": "Web Development",
        "topics": [
            {
                "id": "53039244-50d1-42c2-8137-a04b126e0808",
                "name": "Development Quality Perception",
                "description": "Consumer opinions on the quality, reliability, and functionality of websites developed by Lovable"
            },
            {
                "id": "f54a758d-33a4-41ae-a0a6-10aeedbad786",
                "name": "Pricing Competitiveness Analysis",
                "description": "Consumer perceptions of Lovable's web development pricing in comparison to industry standards and competitors"
            },
            {
                "id": "b1f7cb2b-f2e2-4c59-8dac-a7eef950618a",
                "name": "Customer Support Experience",
                "description": "Consumer experiences and satisfaction with Lovable's customer support during and after web development projects"
            }
        ],
        "personas": [
            {
                "id": "1b5a734e-d809-499e-af9c-ab8a04a7e329",
                "name": "Tech Savvy Entrepreneur",
                "description": "Ambitious entrepreneurs who need high-quality web development services to launch and grow their online businesses, with a focus on innovation, scalability, and user experience",
                "painPoints": [
                    "Difficulty finding reliable developers",
                    "Limited budget for development",
                    "Need for fast time-to-market"
                ],
                "motivators": [
                    "Innovative solutions",
                    "Competitive pricing",
                    "Quick project turnaround"
                ],
                "demographics": {
                    "ageRange": "25-40",
                    "gender": "All genders",
                    "location": "Urban areas",
                    "goals": [
                        "Launch online business",
                        "Increase revenue streams"
                    ]
                }
            },
            {
                "id": "8dc2381f-f9e2-4483-abd1-3e61792e9263",
                "name": "Design-Conscious Business",
                "description": "Established businesses that prioritize design and user experience in their web development projects, seeking to enhance their brand image and customer engagement",
                "painPoints": [
                    "Poor design quality from previous developers",
                    "Difficulty communicating design vision",
                    "Need for consistent brand identity"
                ],
                "motivators": [
                    "High-quality design",
                    "Effective communication",
                    "Attention to detail"
                ],
                "demographics": {
                    "ageRange": "30-50",
                    "gender": "All genders",
                    "location": "Suburban areas",
                    "goals": [
                        "Improve brand image",
                        "Enhance customer experience"
                    ]
                }
            }
        ]
    }
    
    print(f"📋 Payload Summary:")
    print(f"  - Audit ID: {payload['auditId']}")
    print(f"  - Brand: {payload['brandName']}")
    print(f"  - Product: {payload['productName']}")
    print(f"  - Topics: {len(payload['topics'])}")
    print(f"  - Personas: {len(payload['personas'])}")
    
    try:
        print("\n📤 Sending request to backend...")
        response = requests.post(
            "http://localhost:8000/api/questions/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"📊 Questions Count: {len(data.get('questions', []))}")
            print(f"📊 Source: {data.get('source')}")
            print(f"📊 Processing Time: {data.get('processingTime')}s")
            
            if data.get('source') == 'fallback':
                print(f"⚠️ FALLBACK REASON: {data.get('reason')}")
            elif data.get('source') == 'ai':
                print("🎉 AI QUESTIONS GENERATED SUCCESSFULLY!")
                
                # Show first few questions
                questions = data.get('questions', [])[:3]
                for i, q in enumerate(questions, 1):
                    print(f"  {i}. {q.get('text', 'No text')[:60]}...")
                    print(f"     Persona: {q.get('personaId')} | Topic: {q.get('topicName')}")
            
            # Show token usage if available
            if data.get('tokenUsage'):
                print(f"💰 Token Usage: {data.get('tokenUsage')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_exact_frontend_payload() 