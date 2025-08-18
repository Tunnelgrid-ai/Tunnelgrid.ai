#!/usr/bin/env python3
"""
Test the JSON parsing fix with actual GroqCloud response
"""

# Copy the exact parse function from our backend
import json
import uuid
import re
from typing import List, Dict, Optional

class Question:
    def __init__(self, id, text, personaId, auditId, topicName, queryType):
        self.id = id
        self.text = text
        self.personaId = personaId
        self.auditId = auditId
        self.topicName = topicName
        self.queryType = queryType

def parse_questions_from_response(response_text: str, personas: List[Dict]) -> Optional[List[Question]]:
    """Parse questions from GroqCloud response - EXACT COPY FROM BACKEND"""
    
    try:
        # Create a mapping of persona IDs for validation
        valid_persona_ids = {persona.get('id') for persona in personas if persona.get('id')}
        print(f"Valid persona IDs: {valid_persona_ids}")
        
        # 🔧 CREATE PERSONA NAME TO ID MAPPING
        persona_name_to_id = {}
        for persona in personas:
            if persona.get('id') and persona.get('name'):
                persona_name_to_id[persona['name']] = persona['id']
        print(f"Persona name to ID mapping: {persona_name_to_id}")
        
        # Try to extract JSON from the response
        response_text = response_text.strip()
        
        # 🔧 ENHANCED RESPONSE CLEANING FOR GROQCLOUD FORMAT
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
            if response_text.startswith(prefix):
                print(f"🔧 Removing prefix: '{prefix}'")
                response_text = response_text[len(prefix):].strip()
        
        # Remove everything before the first '{' character
        json_start = response_text.find('{')
        if json_start > 0:
            print(f"🔧 Found JSON start at position {json_start}, removing prefix text")
            response_text = response_text[json_start:]
        
        # Remove everything after the last '}' character  
        json_end = response_text.rfind('}')
        if json_end > 0 and json_end < len(response_text) - 1:
            print(f"🔧 Found JSON end at position {json_end}, removing suffix text")
            response_text = response_text[:json_end + 1]
        
        # Handle various response formats
        if response_text.startswith("```json"):
            print("🔧 Removing ```json prefix")
            response_text = response_text[7:]
        if response_text.endswith("```"):
            print("🔧 Removing ``` suffix")
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # 🔧 FIX GROQCLOUD JSON FORMATTING ISSUES
        print("🔧 Attempting to fix GroqCloud JSON formatting issues...")
        
        # Fix missing personaId field names
        # Pattern: "text": "...", "SomePersonaName", -> "text": "...", "personaId": "SomePersonaName",
        response_text = re.sub(
            r'("text":\s*"[^"]*"),\s*"([^"]*)",\s*("topicName":)',
            r'\1, "personaId": "\2", \3',
            response_text
        )
        
        # Pattern: "personaId": "...", "SomeValue" -> "personaId": "...", "queryType": "SomeValue"
        response_text = re.sub(
            r'("personaId":\s*"[^"]*"),\s*"([^"]*)"(\s*})',
            r'\1, "queryType": "\2"\3',
            response_text
        )
        
        # Pattern: "topicName": "...", "some_value" -> "topicName": "...", "queryType": "some_value"
        response_text = re.sub(
            r'("topicName":\s*"[^"]*"),\s*"([^"]*)"(\s*})',
            r'\1, "queryType": "\2"\3',
            response_text
        )
        
        print(f"🧹 FIXED Response (first 500 chars): {response_text[:500]}")
        
        # Try to parse JSON
        try:
            parsed_data = json.loads(response_text)
            print(f"✅ JSON parsing successful! Keys: {list(parsed_data.keys())}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing still failed: {e}")
            return None
        
        if "questions" not in parsed_data:
            print("❌ No 'questions' field in parsed response")
            return None
        
        print(f"📊 Found {len(parsed_data['questions'])} questions in AI response")
        
        questions = []
        for i, q_data in enumerate(parsed_data["questions"]):
            print(f"🔍 Processing question {i+1}: {q_data}")
            
            # 🔧 MORE FLEXIBLE QUESTION PARSING
            if "text" not in q_data:
                print(f"⚠️ Skipping question {i+1} without text: {q_data}")
                continue
            
            # Handle missing or malformed personaId
            persona_id = q_data.get("personaId", "")
            if not persona_id:
                print(f"⚠️ Question {i+1} missing personaId, using first available")
                persona_id = list(valid_persona_ids)[0] if valid_persona_ids else str(uuid.uuid4())
            
            # 🔧 HANDLE BOTH PERSONA IDS AND NAMES
            if persona_id not in valid_persona_ids:
                # Try to map persona name to ID
                if persona_id in persona_name_to_id:
                    print(f"🔧 Mapping persona name '{persona_id}' to ID '{persona_name_to_id[persona_id]}'")
                    persona_id = persona_name_to_id[persona_id]
                else:
                    print(f"⚠️ Invalid persona ID/name in question {i+1}: {persona_id}, using first valid persona ID")
                    # Use the first valid persona ID as fallback
                    persona_id = list(valid_persona_ids)[0] if valid_persona_ids else str(uuid.uuid4())
            
            question = Question(
                id=str(uuid.uuid4()),
                text=q_data["text"],
                personaId=persona_id,  # Use validated persona ID
                auditId="",  # Will be set by caller
                topicName=q_data.get("topicName"),
                queryType=q_data.get("queryType", "brand_analysis")
            )
            questions.append(question)
            print(f"✅ Successfully created question {i+1} for persona {persona_id}")
        
        print(f"✅ Parsed {len(questions)} questions from AI response")
        return questions
        
    except Exception as e:
        print(f"❌ Error parsing questions: {e}")
        return None

def test_parsing():
    print("🧪 Testing JSON parsing with actual GroqCloud malformed response...")
    
    # Exact malformed response from GroqCloud 
    malformed_response = '''
{
  "questions": [
    {
      "text": "How reliable is GO Transit in getting me to work on time?",
      "personaId": "Daily Commuter",
      "topicName": "Service Reliability",
      "queryType": "brand_analysis"
    },
    {
      "text": "Can I easily get assistance from GO Transit staff?",
      "Daily Commuter",
      "topicName": "Customer Experience",
      "queryType": "brand_analysis"
    },
    {
      "text": "How easy is it to plan a family trip using GO Transit?",
      "personaId": "Family Traveler",
      "topicName": "Customer Experience",
      "brand_analysis"
    }
  ]
}
'''
    
    # Test personas (matching what backend receives)
    personas = [
        {
            "id": "persona-1",
            "name": "Daily Commuter",
            "description": "Regular travelers"
        },
        {
            "id": "persona-2", 
            "name": "Family Traveler",
            "description": "Families using transit"
        }
    ]
    
    print("🎯 Calling parse_questions_from_response...")
    questions = parse_questions_from_response(malformed_response, personas)
    
    if questions:
        print(f"🎉 SUCCESS! Parsed {len(questions)} questions:")
        for i, q in enumerate(questions):
            print(f"  {i+1}. {q.text[:50]}...")
            print(f"     Persona: {q.personaId}")
            print(f"     Topic: {q.topicName}")
            print(f"     QueryType: {q.queryType}")
            print()
    else:
        print("❌ FAILED to parse questions")

if __name__ == "__main__":
    test_parsing() 