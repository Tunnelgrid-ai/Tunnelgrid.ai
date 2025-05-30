#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_questions_direct():
    """Test GroqCloud API directly with questions payload"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No GROQ_API_KEY found in environment")
        return
    
    # Create the same prompt that questions route would create
    prompt = """Generate exactly 10 consumer perception research questions for analyzing "TestProduct" by TestBrand (testbrand.com).

Context:
- Brand: TestBrand
- Product/Service: TestProduct
- Domain: testbrand.com
- Brand Description: A test brand for testing

Topics to focus on:
1. Quality - Product quality

Target Personas:
1. Test User - A test persona

Requirements:
1. Generate exactly 10 distinct questions
2. Each question should be specific to consumer perception/opinion research
3. Questions should be actionable and suitable for surveys or interviews
4. Cover diverse aspects: quality, pricing, experience, trust, innovation, etc.
5. Each question should be 8-20 words long
6. Questions should be relevant to TestProduct by TestBrand

Respond with a JSON array containing exactly 10 objects, each with:
- "personaId": string (persona identifier from the list above)
- "text": string (the actual question)
- "queryType": string (always "brand_analysis")
- "topicName": string (topic name from the list above)

Example format:
[
  {
    "personaId": "Test User",
    "text": "How would you rate the overall quality of TestProduct?",
    "queryType": "brand_analysis",
    "topicName": "Quality"
  }
]

Generate questions specifically for TestProduct by TestBrand:"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert consumer research analyst. Generate specific, actionable questions for brand analysis. Always respond with valid JSON."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }

    try:
        print("🧪 Testing GroqCloud API directly with questions payload...")
        print(f"🔑 Using API key: {api_key[:10]}...")
        print(f"🤖 Model: {payload['model']}")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            token_usage = data.get("usage", {}).get("total_tokens", 0)
            
            print(f"✅ Success!")
            print(f"🎯 Token Usage: {token_usage}")
            print(f"📝 Content Length: {len(content)} characters")
            print(f"📄 FULL RESPONSE:")
            print("="*50)
            print(content)
            print("="*50)
            
            # Try to parse as JSON
            try:
                questions = json.loads(content)
                print(f"✅ JSON Parse Success: {len(questions)} questions")
                if questions:
                    print(f"📋 First question: {questions[0]}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Failed: {e}")
                print(f"❌ Failed at position: {e.pos}")
                
                # Try to extract JSON from the response
                print("\n🔧 Attempting to fix the response...")
                
                # Remove text before first [
                json_start = content.find('[')
                if json_start > 0:
                    print(f"🔧 Found JSON start at position {json_start}")
                    extracted = content[json_start:]
                    
                    # Remove text after last ]
                    json_end = extracted.rfind(']')
                    if json_end > 0:
                        extracted = extracted[:json_end + 1]
                        
                        print(f"🔧 Extracted JSON: {extracted[:200]}...")
                        
                        try:
                            questions = json.loads(extracted)
                            print(f"✅ Extracted JSON Parse Success: {len(questions)} questions")
                            if questions:
                                print(f"📋 First question: {questions[0]}")
                        except json.JSONDecodeError as e2:
                            print(f"❌ Extracted JSON Parse Still Failed: {e2}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_groq_questions_direct() 