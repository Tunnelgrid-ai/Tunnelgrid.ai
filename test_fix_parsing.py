#!/usr/bin/env python3
"""
Test the parsing fix with real AI response
"""

import json

def parse_topics_from_response(response_text: str):
    """
    Parse topics from AI response - handles both object and array formats
    """
    try:
        # Clean response text
        cleaned_text = response_text.strip()
        if not cleaned_text:
            print("❌ Empty response text")
            return None
        
        print(f"🔍 Raw response (first 200 chars): {cleaned_text[:200]}")
        
        # Remove markdown code blocks if present
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text.replace('```json\n', '').replace('```json', '').replace('```', '')
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text.replace('```\n', '').replace('```', '')
        
        # Try to extract JSON from response if it's mixed with other text
        json_start = -1
        json_end = -1
        
        # Look for JSON array start
        if '[' in cleaned_text:
            json_start = cleaned_text.find('[')
            # Find matching closing bracket
            bracket_count = 0
            for i in range(json_start, len(cleaned_text)):
                if cleaned_text[i] == '[':
                    bracket_count += 1
                elif cleaned_text[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_end = i + 1
                        break
        
        # Look for JSON object start if no array found
        elif '{' in cleaned_text:
            json_start = cleaned_text.find('{')
            # Find matching closing brace
            brace_count = 0
            for i in range(json_start, len(cleaned_text)):
                if cleaned_text[i] == '{':
                    brace_count += 1
                elif cleaned_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
        
        # Extract just the JSON part if found
        if json_start >= 0 and json_end > json_start:
            cleaned_text = cleaned_text[json_start:json_end].strip()
            print(f"🔧 Extracted JSON: {cleaned_text[:200]}")
        
        # Remove any leading/trailing whitespace after cleaning
        cleaned_text = cleaned_text.strip()
        
        print(f"🧹 Cleaned response (first 200 chars): {cleaned_text[:200]}")
        
        # Parse JSON
        parsed_response = json.loads(cleaned_text)
        
        # Handle both formats: {"topics": [...]} and [...]
        if isinstance(parsed_response, dict):
            if "topics" in parsed_response:
                topics_data = parsed_response["topics"]
            else:
                print(f"❌ Response is object but doesn't contain 'topics' key. Available keys: {list(parsed_response.keys())}")
                return None
        elif isinstance(parsed_response, list):
            topics_data = parsed_response
        else:
            print(f"❌ Unexpected response format: {type(parsed_response)}")
            return None
        
        # Validate topics structure
        if not isinstance(topics_data, list):
            print("❌ Topics data is not a list")
            return None
        
        validated_topics = []
        for i, topic in enumerate(topics_data):
            if not isinstance(topic, dict):
                print(f"❌ Topic {i} is not a dictionary: {type(topic)}")
                continue
            
            if "name" not in topic or "description" not in topic:
                print(f"❌ Topic {i} missing required fields. Available keys: {list(topic.keys())}")
                continue
            
            validated_topics.append({
                "name": str(topic["name"]).strip(),
                "description": str(topic["description"]).strip()
            })
        
        print(f"✅ Successfully parsed {len(validated_topics)} topics")
        return validated_topics if validated_topics else None
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"❌ Failed to parse: '{cleaned_text[:100] if 'cleaned_text' in locals() else response_text[:100]}...'")
        return None
    except Exception as e:
        print(f"❌ Error parsing topics response: {e}")
        return None

def test_parsing():
    print("🧪 Testing parsing with real AI response...")
    
    # The actual AI response from our test
    ai_response = """Here are 10 consumer perception research topics for analyzing GO Transit Services by Metrolinx:


[
  {
    "name": "Reliability and Punctuality",
    "description": "Consumer opinions on the frequency, timeliness, and reliability of GO Transit Services"
  },
  {
    "name": "Fare Pricing and Value",
    "description": "Consumer perceptions of the affordability and value for money of GO Transit Services compared to alternative transportation options"
  },
  {
    "name": "Station and Terminal Experience",
    "description": "Consumer opinions on the cleanliness, safety, and amenities of GO Transit stations and terminals"
  },
  {
    "name": "On-Board Comfort and Cleanliness",
    "description": "Consumer experiences with the comfort, cleanliness, and overall condition of GO Transit vehicles"
  },
  {
    "name": "Customer Service and Support",
    "description": "Consumer evaluations of the helpfulness, responsiveness, and friendliness of GO Transit customer service representatives"
  },
  {
    "name": "Route Network and Coverage",
    "description": "Consumer opinions on the convenience, frequency, and geographic coverage of GO Transit routes"
  },
  {
    "name": "Safety and Security Concerns",
    "description": "Consumer perceptions of the safety and security of GO Transit Services, including concerns about crime, accidents, and emergency response"
  },
  {
    "name": "Innovation and Technology Adoption",
    "description": "Consumer opinions on the adoption and effectiveness of technology, such as mobile apps and digital signage, in enhancing the GO Transit experience"
  },
  {
    "name": "Environmental Sustainability",
    "description": "Consumer perceptions of GO Transit's environmental impact and efforts to reduce carbon footprint"
  },
  {
    "name": "Trust and Loyalty",
    "description": "Consumer attitudes towards Metrolinx and GO Transit, including levels of trust, loyalty, and likelihood to recommend"
  }
]"""
    
    result = parse_topics_from_response(ai_response)
    
    if result:
        print(f"🎉 SUCCESS! Parsed {len(result)} topics:")
        for i, topic in enumerate(result[:3]):
            print(f"  {i+1}. {topic['name']}")
            print(f"     {topic['description']}")
        return True
    else:
        print("❌ FAILED to parse!")
        return False

if __name__ == "__main__":
    success = test_parsing()
    print(f"\n🎯 Overall result: {'✅ PASS' if success else '❌ FAIL'}") 