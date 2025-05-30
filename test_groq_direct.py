#!/usr/bin/env python3
"""
Direct GroqCloud API Test Script
Tests the exact same API call we're making in the backend
"""

import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GroqCloud Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"
GROQ_MAX_TOKENS = 4000
GROQ_TEMPERATURE = 0.7

def create_test_prompt():
    """Create the same prompt we use in the backend"""
    
    brand_name = "Metrolinx"
    brand_description = "Provincial transit agency providing GO Transit and UP Express services"
    brand_domain = "metrolinx.com"
    product_name = "GO Transit Services"
    
    topics = [
        {"name": "Service Reliability", "description": "Punctuality and consistency of transit services"},
        {"name": "Customer Experience", "description": "Overall passenger satisfaction and service quality"}
    ]
    
    personas = [
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
    
    # Build topics context
    topics_context = "\n".join([
        f"- {topic['name']}: {topic['description']}"
        for topic in topics
    ])
    
    # Build personas context
    personas_context = ""
    for persona in personas:
        persona_info = f"\n{persona['name']}:\n"
        persona_info += f"  Description: {persona['description']}\n"
        
        if persona.get('painPoints'):
            persona_info += f"  Pain Points: {', '.join(persona['painPoints'])}\n"
        
        if persona.get('motivators'):
            persona_info += f"  Motivators: {', '.join(persona['motivators'])}\n"
        
        if persona.get('demographics'):
            demo = persona['demographics']
            persona_info += f"  Demographics: "
            demo_parts = []
            if demo.get('ageRange'): demo_parts.append(f"Age: {demo['ageRange']}")
            if demo.get('gender'): demo_parts.append(f"Gender: {demo['gender']}")
            if demo.get('location'): demo_parts.append(f"Location: {demo['location']}")
            if demo.get('goals'): demo_parts.append(f"Goals: {', '.join(demo['goals'])}")
            persona_info += "; ".join(demo_parts) + "\n"
        
        personas_context += persona_info
    
    prompt = f"""You are an expert market researcher generating customer questions for brand analysis research.

BRAND CONTEXT:
- Brand: {brand_name} ({brand_domain}) - {brand_description}
- Product/Service: {product_name}

TOPICS TO ANALYZE:
{topics_context}

CUSTOMER PERSONAS:
{personas_context}

TASK: Generate exactly 10 insightful customer questions for EACH persona that would help understand how that specific persona perceives the brand and product. Each question should:

1. Be written from the persona's perspective and reflect their specific characteristics, pain points, and motivators
2. Focus on brand perception, product evaluation, and decision-making factors
3. Be specific to the brand and product context
4. Help understand potential concerns, preferences, and decision drivers for that persona type
5. Be actionable for market research purposes

IMPORTANT: 
- Generate exactly 10 questions per persona
- Make questions persona-specific (reflect their pain points, motivators, demographics)
- Questions should sound natural as if the persona is asking them
- Focus on brand/product evaluation, not general advice

OUTPUT FORMAT (JSON only, no additional text):
{{
  "questions": [
    {{
      "text": "question text here",
      "personaId": "persona_id_here",
      "topicName": "most_relevant_topic_name",
      "queryType": "brand_analysis"
    }},
    ...
  ]
}}

Generate the questions now:"""
    
    return prompt

async def test_groq_api():
    """Test GroqCloud API directly"""
    
    print("🚀 Testing GroqCloud API directly...")
    print(f"🔑 API Key present: {'Yes' if GROQ_API_KEY else 'No'}")
    print(f"🎯 Model: {GROQ_MODEL}")
    print("-" * 60)
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in environment variables!")
        print("💡 Make sure you have GROQ_API_KEY in your .env file")
        return
    
    # Create prompt
    prompt = create_test_prompt()
    print(f"📝 Prompt length: {len(prompt)} characters")
    print("📝 Prompt preview (first 200 chars):")
    print(prompt[:200] + "...")
    print("-" * 60)
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": GROQ_MAX_TOKENS,
        "temperature": GROQ_TEMPERATURE
    }
    
    try:
        print("🌐 Making API call to GroqCloud...")
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(GROQ_BASE_URL, headers=headers, json=payload)
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                api_response = response.json()
                
                print("✅ API Call Successful!")
                print(f"📋 Response Keys: {list(api_response.keys())}")
                
                if 'choices' in api_response and len(api_response['choices']) > 0:
                    content = api_response['choices'][0]['message']['content']
                    print(f"📏 Content Length: {len(content)} characters")
                    print("-" * 60)
                    print("📥 RAW RESPONSE:")
                    print(content)
                    print("-" * 60)
                    
                    # Try to parse as JSON
                    try:
                        # Clean the response with enhanced logic
                        cleaned_content = content.strip()
                        
                        # Remove common prefixes that GroqCloud includes
                        prefixes_to_remove = [
                            "Here are the generated customer questions",
                            "Here are the questions", 
                            "Here is the JSON",
                            "**",
                            "```json",
                            "```"
                        ]
                        
                        for prefix in prefixes_to_remove:
                            if cleaned_content.startswith(prefix):
                                print(f"🔧 Removing prefix: '{prefix}'")
                                cleaned_content = cleaned_content[len(prefix):].strip()
                        
                        # Remove everything before the first '{' character
                        json_start = cleaned_content.find('{')
                        if json_start > 0:
                            print(f"🔧 Found JSON start at position {json_start}, removing prefix text")
                            cleaned_content = cleaned_content[json_start:]
                        
                        # Handle multiple JSON objects by combining them
                        import re
                        json_objects = []
                        
                        # Find all JSON objects in the response
                        brace_count = 0
                        start_pos = 0
                        current_json = ""
                        
                        for i, char in enumerate(cleaned_content):
                            if char == '{':
                                if brace_count == 0:
                                    start_pos = i
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    # Found complete JSON object
                                    json_obj_str = cleaned_content[start_pos:i+1]
                                    try:
                                        json_obj = json.loads(json_obj_str)
                                        if 'questions' in json_obj:
                                            json_objects.append(json_obj)
                                            print(f"🔍 Found JSON object with {len(json_obj['questions'])} questions")
                                    except:
                                        pass
                        
                        if json_objects:
                            # Combine all questions from multiple JSON objects
                            all_questions = []
                            for json_obj in json_objects:
                                all_questions.extend(json_obj['questions'])
                            
                            parsed_json = {"questions": all_questions}
                            print("✅ Combined JSON Parsing Successful!")
                        else:
                            # Fallback to original parsing
                            # Remove everything after the last '}' character  
                            json_end = cleaned_content.rfind('}')
                            if json_end > 0 and json_end < len(cleaned_content) - 1:
                                print(f"🔧 Found JSON end at position {json_end}, removing suffix text")
                                cleaned_content = cleaned_content[:json_end + 1]
                            
                            parsed_json = json.loads(cleaned_content)
                        
                        print(f"📊 Parsed Keys: {list(parsed_json.keys())}")
                        
                        if 'questions' in parsed_json:
                            questions = parsed_json['questions']
                            print(f"📈 Number of Questions: {len(questions)}")
                            
                            # Show first few questions
                            for i, q in enumerate(questions[:3]):
                                print(f"🔍 Question {i+1}: {q}")
                        else:
                            print("❌ No 'questions' key in parsed JSON")
                            print(f"📋 Available keys: {list(parsed_json.keys())}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Parsing Failed: {e}")
                        print(f"❌ Error at line {e.lineno}, column {e.colno}")
                        print(f"❌ Error message: {e.msg}")
                        print("🧹 Cleaned content preview:")
                        print(cleaned_content[:500] + "...")
                
                # Show token usage
                if 'usage' in api_response:
                    usage = api_response['usage']
                    print(f"🎯 Token Usage: {usage}")
            else:
                print(f"❌ API Call Failed: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
    except Exception as e:
        print(f"💥 Error occurred: {e}")
        print(f"💥 Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_groq_api()) 