#!/usr/bin/env python3
"""
Test the fixed parsing logic with actual Groq responses
"""

import json
import uuid
import re
from typing import List, Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Question:
    def __init__(self, id, text, personaId, auditId, topicName, queryType):
        self.id = id
        self.text = text
        self.personaId = personaId
        self.auditId = auditId
        self.topicName = topicName
        self.queryType = queryType

def parse_questions_from_response(response_text: str, personas: List[Dict]) -> Optional[List[Question]]:
    """Parse questions from GroqCloud response - FIXED VERSION"""
    
    try:
        # Create a mapping of persona IDs for validation
        valid_persona_ids = {persona.get('id') for persona in personas if persona.get('id')}
        logger.info(f"Valid persona IDs: {valid_persona_ids}")
        
        # 🔧 CREATE PERSONA NAME TO ID MAPPING
        persona_name_to_id = {}
        for persona in personas:
            if persona.get('id') and persona.get('name'):
                persona_name_to_id[persona['name']] = persona['id']
        logger.info(f"Persona name to ID mapping: {persona_name_to_id}")
        
        # 🐛 ADD DETAILED LOGGING FOR RESPONSE CONTENT
        logger.info(f"📥 RAW AI Response (first 1000 chars): {response_text[:1000]}")
        logger.info(f"📏 Full response length: {len(response_text)} characters")
        
        # Try to extract JSON from the response
        response_text = response_text.strip()
        original_response = response_text
        
        # 🔧 ENHANCED RESPONSE CLEANING FOR GROQCLOUD FORMAT
        # Remove common prefixes that GroqCloud includes
        prefixes_to_remove = [
            "Here are the generated customer questions",
            "Here are the questions", 
            "Here are the 10 consumer perception research questions",
            "Here is the JSON",
            "**",
            "```json",
            "```"
        ]
        
        for prefix in prefixes_to_remove:
            if response_text.startswith(prefix):
                logger.info(f"🔧 Removing prefix: '{prefix}'")
                response_text = response_text[len(prefix):].strip()
        
        # 🔧 HANDLE BOTH OBJECT AND ARRAY FORMATS
        # Look for both { (object) and [ (array) as JSON start
        json_start_obj = response_text.find('{')
        json_start_arr = response_text.find('[')
        
        # Use whichever comes first (or only one if the other is -1)
        if json_start_obj != -1 and json_start_arr != -1:
            json_start = min(json_start_obj, json_start_arr)
            json_type = 'object' if json_start == json_start_obj else 'array'
        elif json_start_obj != -1:
            json_start = json_start_obj
            json_type = 'object'
        elif json_start_arr != -1:
            json_start = json_start_arr
            json_type = 'array'
        else:
            logger.error("❌ No JSON found in response")
            return None
        
        if json_start > 0:
            logger.info(f"🔧 Found JSON {json_type} start at position {json_start}, removing prefix text")
            response_text = response_text[json_start:]
        
        # Remove everything after the last } or ] character depending on type
        if json_type == 'object':
            json_end = response_text.rfind('}')
            if json_end > 0 and json_end < len(response_text) - 1:
                logger.info(f"🔧 Found JSON object end at position {json_end}, removing suffix text")
                response_text = response_text[:json_end + 1]
        else:  # array
            json_end = response_text.rfind(']')
            if json_end > 0 and json_end < len(response_text) - 1:
                logger.info(f"🔧 Found JSON array end at position {json_end}, removing suffix text")
                response_text = response_text[:json_end + 1]
        
        # Handle markdown code blocks
        if response_text.startswith("```json"):
            logger.info("🔧 Removing ```json prefix")
            response_text = response_text[7:]
        if response_text.endswith("```"):
            logger.info("🔧 Removing ``` suffix")
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # 🔧 FIX GROQCLOUD JSON FORMATTING ISSUES (only for malformed objects)
        if json_type == 'object':
            logger.info("🔧 Attempting to fix GroqCloud JSON formatting issues...")
            
            # Fix missing personaId field names
            import re
            
            # Pattern: "text": "...", "SomePersonaName", -> "text": "...", "personaId": "SomePersonaName",
            response_text = re.sub(
                r'("text":\s*"[^"]*"),\s*"([^"]*"),\s*("topicName":)',
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
        
        # 🐛 LOG CLEANED RESPONSE
        logger.info(f"🧹 CLEANED Response (first 500 chars): {response_text[:500]}")
        
        # Parse JSON - Handle both object and array formats
        parsed_data = None
        questions_array = None
        
        try:
            # Parse the JSON
            parsed_json = json.loads(response_text)
            logger.info(f"✅ JSON parsing successful! Type: {type(parsed_json)}")
            
            if isinstance(parsed_json, list):
                # Direct array format: [question1, question2, ...]
                logger.info(f"📋 Found direct array with {len(parsed_json)} questions")
                questions_array = parsed_json
            elif isinstance(parsed_json, dict):
                # Object format: {"questions": [question1, question2, ...]}
                if "questions" in parsed_json:
                    logger.info(f"📋 Found object with questions array: {len(parsed_json['questions'])} questions")
                    questions_array = parsed_json["questions"]
                else:
                    logger.error(f"❌ Object format but no 'questions' field. Available fields: {list(parsed_json.keys())}")
                    return None
            else:
                logger.error(f"❌ Unexpected JSON type: {type(parsed_json)}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            logger.error(f"❌ Failed parsing this text: {response_text[:1000]}...")
            return None
        
        if not questions_array:
            logger.error("❌ No questions array found in parsed response")
            return None
        
        logger.info(f"📊 Found {len(questions_array)} questions in AI response")
        
        questions = []
        for i, q_data in enumerate(questions_array):
            logger.info(f"🔍 Processing question {i+1}: {q_data}")
            
            # 🔧 MORE FLEXIBLE QUESTION PARSING
            if not isinstance(q_data, dict):
                logger.warning(f"⚠️ Skipping question {i+1} - not a dict: {q_data}")
                continue
                
            if "text" not in q_data:
                logger.warning(f"⚠️ Skipping question {i+1} without text: {q_data}")
                continue
            
            # Handle missing or malformed personaId
            persona_id = q_data.get("personaId", "")
            if not persona_id:
                logger.warning(f"⚠️ Question {i+1} missing personaId, using first available")
                persona_id = list(valid_persona_ids)[0] if valid_persona_ids else str(uuid.uuid4())
            
            # 🔧 HANDLE BOTH PERSONA IDS AND NAMES
            if persona_id not in valid_persona_ids:
                # Try to map persona name to ID
                if persona_id in persona_name_to_id:
                    logger.info(f"🔧 Mapping persona name '{persona_id}' to ID '{persona_name_to_id[persona_id]}'")
                    persona_id = persona_name_to_id[persona_id]
                else:
                    logger.warning(f"⚠️ Invalid persona ID/name in question {i+1}: {persona_id}, using first valid persona ID")
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
            logger.info(f"✅ Successfully created question {i+1} for persona {persona_id}")
        
        logger.info(f"✅ Parsed {len(questions)} questions from AI response")
        # Log questions per persona for debugging
        questions_per_persona = {}
        for q in questions:
            questions_per_persona[q.personaId] = questions_per_persona.get(q.personaId, 0) + 1
        logger.info(f"Questions per persona: {questions_per_persona}")
        
        return questions
        
    except Exception as e:
        logger.error(f"❌ Error parsing questions: {e}")
        logger.error(f"❌ Exception type: {type(e)}")
        return None

def test_parsing():
    print("🧪 Testing FIXED JSON parsing logic...")
    
    # Test personas
    personas = [
        {
            "id": "persona-1",
            "name": "Test User",
            "description": "A test persona"
        }
    ]
    
    # Test Case 1: Actual Groq response format (array with prefix)
    print("\n📋 Test Case 1: Actual Groq Array Format")
    actual_groq_response = '''Here are the 10 consumer perception research questions for analyzing "TestProduct" by TestBrand:

[
  {
    "personaId": "Test User",
    "text": "How would you rate the overall quality of TestProduct?",
    "queryType": "brand_analysis",
    "topicName": "Quality"
  },
  {
    "personaId": "Test User",
    "text": "Is TestProduct worth the price you paid for it?",
    "queryType": "brand_analysis",
    "topicName": "Pricing"
  }
]'''
    
    questions1 = parse_questions_from_response(actual_groq_response, personas)
    if questions1:
        print(f"✅ Test 1 PASSED: Parsed {len(questions1)} questions")
        for q in questions1:
            print(f"   - {q.text[:50]}... (persona: {q.personaId})")
    else:
        print("❌ Test 1 FAILED")
    
    # Test Case 2: Expected object format
    print("\n📋 Test Case 2: Expected Object Format")
    expected_format = '''{
  "questions": [
    {
      "personaId": "Test User",
      "text": "How satisfied are you with TestProduct's customer service?",
      "queryType": "brand_analysis",
      "topicName": "Service"
    }
  ]
}'''
    
    questions2 = parse_questions_from_response(expected_format, personas)
    if questions2:
        print(f"✅ Test 2 PASSED: Parsed {len(questions2)} questions")
        for q in questions2:
            print(f"   - {q.text[:50]}... (persona: {q.personaId})")
    else:
        print("❌ Test 2 FAILED")
    
    print("\n🎯 Testing Complete!")

if __name__ == "__main__":
    test_parsing() 