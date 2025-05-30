#!/usr/bin/env python3
"""
Test script to debug Groq API issues
"""

import os
import httpx
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_groq_api():
    """Test Groq API directly"""
    
    print("🧪 Testing Groq API Configuration...")
    
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    print(f"API Key found: {'✅ Yes' if api_key else '❌ No'}")
    if api_key:
        print(f"API Key (first 10 chars): {api_key[:10]}...")
        # Remove quotes if present
        api_key = api_key.strip('"').strip("'")
        print(f"API Key after cleaning: {api_key[:10]}...")
    
    if not api_key:
        print("❌ No GROQ_API_KEY found in environment")
        return
    
    # Test API call
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # Simple test payload
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user", 
                "content": "Generate exactly 3 topics about Apple products in JSON format with 'name' and 'description' fields."
            }
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    print("\n📡 Testing Groq API call...")
    print(f"URL: {url}")
    print(f"Model: {payload['model']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.is_success:
            data = response.json()
            print("✅ API call successful!")
            print(f"Token usage: {data.get('usage', {})}")
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"Response content: {content[:200]}...")
            
        else:
            print(f"❌ API call failed!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to parse error
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
                
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq_api()) 