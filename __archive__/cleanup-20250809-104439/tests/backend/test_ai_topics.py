#!/usr/bin/env python3
"""
Test Direct AI Topics Generation
"""

import os
import requests
import json

def test_direct_ai_topics():
    print("🎯 Testing Direct AI Topics Generation...")
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No GROQ_API_KEY found in environment")
        return
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Create the prompt
    prompt = """Generate exactly 10 consumer perception research topics for analyzing "GO Transit Services" by Metrolinx (metrolinx.com).

Context:
- Brand: Metrolinx
- Product/Service: GO Transit Services
- Domain: metrolinx.com

Requirements:
1. Generate exactly 10 distinct topics
2. Each topic should focus on consumer perception, opinion, or experience
3. Topics should be specific to this brand/product combination
4. Cover diverse aspects: quality, pricing, experience, trust, innovation, etc.
5. Each topic needs a clear, descriptive name (2-6 words)
6. Each topic needs a brief description explaining what it covers

Respond with a JSON array containing exactly 10 objects, each with:
- "name": string (topic name, 2-6 words)
- "description": string (brief explanation of what this topic covers)

Example format:
[
  {
    "name": "Product Quality Assessment",
    "description": "Consumer opinions on build quality, durability, and performance of the product"
  }
]

Generate topics specifically relevant to GO Transit Services by Metrolinx:"""
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert consumer research analyst. Generate specific, actionable research topics for brand analysis. Always respond with valid JSON."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2048,
        "temperature": 0.7
    }
    
    try:
        print("📤 Making direct GroqCloud API call...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GroqCloud API Success!")
            print(f"📊 Response keys: {list(result.keys())}")
            
            if 'choices' in result and len(result['choices']) > 0:
                ai_content = result['choices'][0]['message']['content']
                print(f"📏 Content length: {len(ai_content)}")
                print(f"🔍 Raw AI Content:")
                print("=" * 50)
                print(ai_content)
                print("=" * 50)
                
                # Try to parse it
                try:
                    # Clean response text
                    cleaned = ai_content.strip()
                    
                    # Remove markdown if present
                    if cleaned.startswith('```json'):
                        cleaned = cleaned.replace('```json\n', '').replace('```json', '').replace('```', '')
                    elif cleaned.startswith('```'):
                        cleaned = cleaned.replace('```\n', '').replace('```', '')
                    
                    # Extract JSON if mixed with text
                    if '[' in cleaned:
                        start = cleaned.find('[')
                        bracket_count = 0
                        end = -1
                        for i in range(start, len(cleaned)):
                            if cleaned[i] == '[':
                                bracket_count += 1
                            elif cleaned[i] == ']':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    end = i + 1
                                    break
                        if end > start:
                            cleaned = cleaned[start:end]
                    
                    parsed = json.loads(cleaned)
                    print(f"✅ JSON Parse Success! Found {len(parsed)} topics")
                    
                    for i, topic in enumerate(parsed[:3]):
                        print(f"  {i+1}. {topic.get('name', 'No name')}")
                        print(f"     {topic.get('description', 'No description')}")
                        
                except Exception as parse_error:
                    print(f"❌ Parse Error: {parse_error}")
                    print(f"🔍 Trying to parse: '{cleaned[:100]}...'")
            else:
                print("❌ No choices in response")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_direct_ai_topics() 