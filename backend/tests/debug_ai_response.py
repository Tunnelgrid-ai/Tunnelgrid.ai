#!/usr/bin/env python3
"""
Debug script to see exactly what the AI returns
"""

import os
import httpx
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_ai_response():
    """Test the exact AI response for topics generation"""
    
    print("🔍 Testing AI Topics Generation Response...")
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    # Clean API key
    api_key = api_key.strip('"').strip("'")
    
    # Create the same prompt as the API uses
    prompt = """Generate exactly 10 consumer perception research topics for analyzing "iPhone" by Apple (apple.com).

Context:
- Brand: Apple
- Product/Service: iPhone
- Domain: apple.com

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

Generate topics specifically relevant to iPhone by Apple:"""
    
    # Test with current settings
    request_body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert market researcher specializing in consumer perception analysis. Generate relevant, specific topics for consumer research studies."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    print("🔥 Testing with json_object format...")
    await test_request(api_key, request_body)
    
    # Test without response_format
    print("\n" + "="*50)
    print("🔥 Testing without response_format...")
    
    request_body_no_format = request_body.copy()
    del request_body_no_format["response_format"]
    
    await test_request(api_key, request_body_no_format)

async def test_request(api_key, request_body):
    """Test a specific request configuration"""
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json=request_body
            )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.is_success:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"✅ Success!")
            print(f"💬 Raw content (first 200 chars):")
            print(f"'{content[:200]}...'")
            print(f"\n💬 Full content:")
            print(f"'{content}'")
            
            # Test parsing
            print(f"\n🔍 Testing parsing...")
            parsed = test_parsing(content)
            if parsed:
                print(f"✅ Parsing successful! Found {len(parsed)} topics")
                for i, topic in enumerate(parsed[:3], 1):
                    print(f"  {i}. {topic['name']}")
            else:
                print("❌ Parsing failed")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_parsing(response_text: str):
    """Test the parsing function"""
    try:
        # Clean the response text (same logic as in API)
        clean_text = response_text.strip()
        print(f"🧹 Before cleaning: '{clean_text[:100]}...'")
        
        if clean_text.startswith('```json'):
            clean_text = clean_text.replace('```json\n', '').replace('```json', '').replace('```', '')
        elif clean_text.startswith('```'):
            clean_text = clean_text.replace('```\n', '').replace('```', '')
        
        print(f"🧹 After cleaning: '{clean_text[:100]}...'")
        
        # Parse JSON
        parsed = json.loads(clean_text)
        print(f"📋 Parsed type: {type(parsed)}")
        
        # Validate structure
        if not isinstance(parsed, list):
            print(f"❌ Response is not an array, it's a {type(parsed)}")
            if isinstance(parsed, dict):
                print(f"🔍 Dict keys: {list(parsed.keys())}")
            return None
        
        # Transform and validate topics
        topics = []
        for index, item in enumerate(parsed[:10]):
            if isinstance(item, dict) and 'name' in item and 'description' in item:
                topics.append({
                    "id": f"ai-topic-{index + 1}",
                    "name": str(item['name']).strip(),
                    "description": str(item['description']).strip()
                })
        
        return topics if len(topics) > 0 else None
        
    except Exception as error:
        print(f"❌ Parsing error: {error}")
        return None

if __name__ == "__main__":
    asyncio.run(debug_ai_response()) 