import requests
import json

# Test data that mimics what the frontend would send
test_data = {
    "auditId": "test-audit-123",
    "brandName": "TestBrand",
    "brandDescription": "A test brand for demonstration",
    "brandDomain": "testbrand.com",
    "productName": "Test Product",
    "topics": [
        {
            "id": "topic-1",
            "name": "User Experience",
            "description": "How users interact with our product"
        },
        {
            "id": "topic-2", 
            "name": "Pricing",
            "description": "Pricing strategy and value perception"
        }
    ],
    "personas": [
        {
            "id": "persona-1",
            "name": "Tech Professional",
            "description": "Technology professionals seeking advanced solutions",
            "painPoints": ["Limited time", "Complex requirements"],
            "motivators": ["Productivity", "Time savings"],
            "demographics": {
                "ageRange": "25-40",
                "gender": "Mixed",
                "location": "Urban",
                "goals": ["Career advancement", "Efficiency"]
            }
        },
        {
            "id": "persona-2",
            "name": "Small Business Owner",
            "description": "Entrepreneurs seeking cost-effective solutions",
            "painPoints": ["Budget constraints", "Limited technical knowledge"],
            "motivators": ["Cost savings", "Easy implementation"],
            "demographics": {
                "ageRange": "30-50",
                "gender": "Mixed", 
                "location": "Suburban",
                "goals": ["Business growth", "Profitability"]
            }
        }
    ]
}

def test_questions_api():
    print("🧪 Testing Questions API...")
    
    try:
        # Test health endpoint first
        health_response = requests.get("http://localhost:8000/api/questions/health")
        print(f"Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health data: {health_response.json()}")
        
        # Test questions generation
        print("\n🚀 Testing question generation...")
        response = requests.post(
            "http://localhost:8000/api/questions/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Generated {len(data['questions'])} questions")
            print(f"Source: {data['source']}")
            if data.get('reason'):
                print(f"Reason: {data['reason']}")
            
            # Group by persona to check distribution
            by_persona = {}
            for q in data['questions']:
                persona_id = q['personaId']
                if persona_id not in by_persona:
                    by_persona[persona_id] = []
                by_persona[persona_id].append(q['text'])
            
            print("\n📊 Questions by persona:")
            for persona_id, questions in by_persona.items():
                persona_name = next((p['name'] for p in test_data['personas'] if p['id'] == persona_id), 'Unknown')
                print(f"\n{persona_name} ({persona_id}): {len(questions)} questions")
                for i, q in enumerate(questions[:3], 1):  # Show first 3
                    print(f"  {i}. {q}")
                if len(questions) > 3:
                    print(f"  ... and {len(questions) - 3} more")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_questions_api() 