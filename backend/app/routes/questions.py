"""
QUESTIONS API ROUTES - AI-POWERED QUESTION GENERATION

PURPOSE: Provides secure server-side API for AI-powered question generation

SECURITY BENEFITS:
- API keys stored securely on server-side only  
- Rate limiting and usage monitoring
- Proper error handling and logging
- Input validation and sanitization

ENDPOINTS:
- POST /generate - Generate questions using GroqCloud AI
- POST /store - Store generated questions in database
- GET /by-audit/{audit_id} - Get questions for a specific audit
- POST /retry-failed-personas - Retry question generation for failed personas

ARCHITECTURE:
Frontend → FastAPI Backend → GroqCloud → Backend → Frontend
"""

import time
import json
import httpx
import asyncio
import uuid
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from ..core.config import settings
from ..core.database import get_supabase_client
from ..models.common import HealthResponse
from ..models.questions import (
    QuestionGenerateRequest, QuestionsResponse, Question,
    QuestionsStoreRequest, QuestionsStoreResponse, QuestionsRetrieveResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# CONFIGURATION: GroqCloud API Settings
class GroqConfig:
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = settings.GROQ_MODEL
    MAX_TOKENS = settings.GROQ_MAX_TOKENS
    TEMPERATURE = settings.GROQ_TEMPERATURE
    TIMEOUT = settings.GROQ_TIMEOUT

def get_groq_api_key() -> Optional[str]:
    """Get GroqCloud API key from environment variables"""
    api_key = settings.GROQ_API_KEY
    return api_key

def create_question_generation_prompt(brand_name: str, brand_description: Optional[str], brand_domain: str, 
                                    product_name: str, topics: List[Dict], personas: List[Dict]) -> str:
    """Create a comprehensive prompt for question generation"""
    
    # Build topics context
    topics_context = "\n".join([
        f"- {topic.get('name', 'Unknown')}: {topic.get('description', 'No description')}"
        for topic in topics
    ])
    
    # Build personas context
    personas_context = ""
    for persona in personas:
        persona_info = f"\n{persona.get('name', 'Unknown Persona')}:\n"
        persona_info += f"  Description: {persona.get('description', 'No description')}\n"
        
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
    
    brand_desc_text = f" - {brand_description}" if brand_description else ""
    
    prompt = f"""You are an expert market researcher generating customer questions for brand analysis research.

BRAND CONTEXT:
- Brand: {brand_name} ({brand_domain}){brand_desc_text}
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

CRITICAL REQUIREMENTS:
- Generate exactly 10 questions per persona (Total: {len(personas) * 10} questions)
- Each question must include the exact persona ID from the context
- Make questions persona-specific (reflect their pain points, motivators, demographics)
- Questions should sound natural as if the persona is asking them
- Focus on brand/product evaluation, not general advice

OUTPUT FORMAT (JSON array only, no additional text):
[
  {{
    "text": "question text here",
    "personaId": "exact_persona_id_from_context",
    "topicName": "most_relevant_topic_name",
    "queryType": "brand_analysis"
  }},
  ...
]

PERSONA IDs TO USE:
{chr(10).join([f"- {persona.get('name', 'Unknown')}: {persona.get('id', 'NO_ID')}" for persona in personas])}

Generate exactly {len(personas) * 10} questions now:"""
    
    return prompt

def parse_questions_from_response(response_text: str, personas: List[Dict]) -> Optional[List[Question]]:
    """Parse questions from GroqCloud response - Enhanced for large responses"""
    
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
        logger.info(f"📥 RAW AI Response length: {len(response_text)} characters")
        logger.info(f"📥 RAW AI Response preview (first 500 chars): {response_text[:500]}")
        logger.info(f"📥 RAW AI Response ending (last 200 chars): {response_text[-200:]}")
        
        # Try to extract JSON from the response
        response_text = response_text.strip()
        original_response = response_text
        
        # 🔧 ENHANCED RESPONSE CLEANING FOR GROQCLOUD FORMAT
        # Remove common prefixes that GroqCloud includes
        prefixes_to_remove = [
            "Here are the generated customer questions",
            "Here are the questions", 
            "Here are the 10 consumer perception research questions",
            "Here are 10 consumer perception research questions",
            "Here are the consumer perception research questions",
            "Here is the JSON",
            "```json",
            "```",
            "**",
            "JSON:"
        ]
        
        for prefix in prefixes_to_remove:
            if response_text.lower().startswith(prefix.lower()):
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
        
        # 🆕 ENHANCED: Handle truncated responses by trying to repair them
        if json_type == 'object':
            # For objects, ensure we have a closing brace
            if not response_text.strip().endswith('}'):
                logger.warning("⚠️ Response appears truncated (missing closing }), attempting to repair...")
                # Find the last complete question entry
                last_complete_entry = response_text.rfind('"}')
                if last_complete_entry != -1:
                    # Truncate to the last complete entry and close the JSON
                    response_text = response_text[:last_complete_entry + 2]
                    if not response_text.strip().endswith(']}'):
                        response_text += ']}'
                    else:
                        response_text += '}'
                    logger.info(f"🔧 Repaired truncated object response")
        else:  # array
            # For arrays, ensure we have a closing bracket
            if not response_text.strip().endswith(']'):
                logger.warning("⚠️ Response appears truncated (missing closing ]), attempting to repair...")
                # Find the last complete question entry
                last_complete_entry = response_text.rfind('}')
                if last_complete_entry != -1:
                    # Truncate to the last complete entry and close the array
                    response_text = response_text[:last_complete_entry + 1] + ']'
                    logger.info(f"🔧 Repaired truncated array response")
        
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
        
        # 🐛 LOG CLEANED RESPONSE
        logger.info(f"🧹 CLEANED Response length: {len(response_text)} characters")
        logger.info(f"🧹 CLEANED Response preview (first 500 chars): {response_text[:500]}")
        
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
            logger.error(f"❌ Failed parsing this text (first 1000 chars): {response_text[:1000]}...")
            logger.error(f"❌ Failed parsing this text (last 500 chars): {response_text[-500:]}")
            
            # 🆕 ATTEMPT PARTIAL PARSING for truncated responses
            logger.info("🔧 Attempting partial parsing for truncated response...")
            questions_array = attempt_partial_parsing(response_text)
            if not questions_array:
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
                    original_persona_id = persona_id
                    persona_id = persona_name_to_id[persona_id]
                    logger.info(f"🔄 Mapped persona name '{original_persona_id}' to ID '{persona_id}'")
                else:
                    logger.warning(f"⚠️ Invalid persona ID '{persona_id}', using first available")
                    persona_id = list(valid_persona_ids)[0] if valid_persona_ids else str(uuid.uuid4())
            
            # Create Question object
            question = Question(
                id=str(uuid.uuid4()),
                text=q_data["text"],
                personaId=persona_id,
                auditId="", # Will be set when storing
                topicName=q_data.get("topicName", "General"),
                queryType=q_data.get("queryType", "brand_analysis")
            )
            
            questions.append(question)
            logger.info(f"✅ Successfully created question {i+1} for persona {persona_id}")
        
        logger.info(f"✅ Successfully parsed {len(questions)} questions from AI response")
        return questions
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in parse_questions_from_response: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

def attempt_partial_parsing(response_text: str) -> Optional[List[Dict]]:
    """Attempt to parse partial/truncated JSON responses"""
    try:
        logger.info("🔧 Attempting to extract partial questions from truncated response...")
        
        # Extract individual question objects using regex
        import re
        
        # Pattern to match question objects
        question_pattern = r'\{\s*"text":\s*"([^"]+)"\s*,\s*"personaId":\s*"([^"]+)"\s*(?:,\s*"topicName":\s*"([^"]*)")?\s*(?:,\s*"queryType":\s*"([^"]*)")?\s*\}'
        
        matches = re.findall(question_pattern, response_text)
        
        if matches:
            questions = []
            for match in matches:
                text, persona_id, topic_name, query_type = match
                question_obj = {
                    "text": text,
                    "personaId": persona_id,
                    "topicName": topic_name or "General",
                    "queryType": query_type or "brand_analysis"
                }
                questions.append(question_obj)
            
            logger.info(f"🔧 Extracted {len(questions)} questions from partial response")
            return questions
        
        logger.warning("⚠️ Could not extract any questions from partial response")
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to parse partial response: {e}")
        return None

def should_use_chunking(personas: List[Dict], topics: List[Dict]) -> bool:
    """Determine if we should chunk the request for better success"""
    persona_count = len(personas)
    topic_count = len(topics)
    estimated_questions = persona_count * 10  # 10 questions per persona
    
    # Use chunking if we expect 50+ questions or have complex personas
    return estimated_questions >= 50 or persona_count >= 6

def chunk_personas_for_processing(personas: List[Dict], chunk_size: int = 3) -> List[List[Dict]]:
    """Split personas into smaller chunks for processing"""
    chunks = []
    for i in range(0, len(personas), chunk_size):
        chunk = personas[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

async def generate_questions_chunked(
    audit_id: str,
    brand_name: str,
    brand_description: str,
    brand_domain: str,
    product_name: str,
    topics: List[Dict],
    personas: List[Dict],
    max_retries: int = 2
) -> Tuple[bool, List[Question], str, float, Optional[Dict]]:
    """Generate questions using chunking strategy for large requests"""
    
    logger.info(f"🔄 Using chunked generation for {len(personas)} personas")
    
    all_questions = []
    total_processing_time = 0.0
    all_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    # Split personas into chunks of 3
    persona_chunks = chunk_personas_for_processing(personas, chunk_size=3)
    logger.info(f"📦 Split into {len(persona_chunks)} chunks")
    
    for chunk_idx, persona_chunk in enumerate(persona_chunks, 1):
        logger.info(f"🔄 Processing chunk {chunk_idx}/{len(persona_chunks)} with {len(persona_chunk)} personas")
        
        chunk_success = False
        chunk_questions = []
        
        # Retry this chunk up to max_retries times
        for retry_attempt in range(max_retries + 1):
            try:
                logger.info(f"🔄 Chunk {chunk_idx} attempt {retry_attempt + 1}/{max_retries + 1}")
                
                # Generate questions for this chunk
                success, questions, source, chunk_time, chunk_token_usage = await generate_questions_for_chunk(
                    audit_id, brand_name, brand_description, brand_domain, product_name, 
                    topics, persona_chunk
                )
                
                if success and questions:
                    # Verify we got roughly the expected number of questions (allow some variance)
                    expected_questions = len(persona_chunk) * 10
                    if len(questions) >= expected_questions * 0.5:  # Allow 50% variance (was 0.7)
                        chunk_questions = questions
                        total_processing_time += chunk_time
                        
                        # Aggregate token usage
                        if chunk_token_usage:
                            if isinstance(chunk_token_usage, dict):
                                for key in all_token_usage:
                                    all_token_usage[key] += chunk_token_usage.get(key, 0)
                            elif isinstance(chunk_token_usage, int):
                                all_token_usage["total_tokens"] += chunk_token_usage
                        
                        logger.info(f"✅ Chunk {chunk_idx} successful: {len(chunk_questions)} questions")
                        chunk_success = True
                        break
                    else:
                        # 🆕 CHANGED: Try to use questions even if below threshold on final attempt  
                        if retry_attempt == max_retries and questions:
                            logger.warning(f"⚠️ Chunk {chunk_idx} using {len(questions)} questions despite being below threshold")
                            chunk_questions = questions
                            total_processing_time += chunk_time
                            
                            # Aggregate token usage
                            if chunk_token_usage:
                                if isinstance(chunk_token_usage, dict):
                                    for key in all_token_usage:
                                        all_token_usage[key] += chunk_token_usage.get(key, 0)
                                elif isinstance(chunk_token_usage, int):
                                    all_token_usage["total_tokens"] += chunk_token_usage
                            
                            chunk_success = True
                            break
                        else:
                            logger.warning(f"⚠️ Chunk {chunk_idx} returned {len(questions)} questions, expected ~{expected_questions}")
                else:
                    logger.warning(f"⚠️ Chunk {chunk_idx} attempt {retry_attempt + 1} failed")
                
                # Wait a bit before retrying (exponential backoff)
                if retry_attempt < max_retries:
                    wait_time = (retry_attempt + 1) * 2
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"❌ Error processing chunk {chunk_idx} attempt {retry_attempt + 1}: {e}")
                if retry_attempt < max_retries:
                    wait_time = (retry_attempt + 1) * 2
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                continue
        
        if chunk_success:
            all_questions.extend(chunk_questions)
        else:
            logger.error(f"❌ Chunk {chunk_idx} failed after {max_retries + 1} attempts")
            # Return what we have so far instead of continuing with failed chunks
            if all_questions:
                logger.warning(f"⚠️ Returning partial results: {len(all_questions)} questions from successful chunks")
                return True, all_questions, "ai_chunked_partial", total_processing_time, all_token_usage
            else:
                logger.error("❌ No chunks succeeded, cannot generate any questions")
                return False, [], "failed", total_processing_time, all_token_usage
    
    if all_questions:
        logger.info(f"✅ Chunked generation successful: {len(all_questions)} total questions")
        return True, all_questions, "ai_chunked", total_processing_time, all_token_usage
    else:
        logger.error("❌ All chunks failed, no questions generated")
        return False, [], "failed", total_processing_time, all_token_usage

async def generate_questions_for_chunk(
    audit_id: str,
    brand_name: str,
    brand_description: str,
    brand_domain: str,
    product_name: str,
    topics: List[Dict],
    personas: List[Dict]
) -> Tuple[bool, List[Question], str, float, Optional[Dict]]:
    """Generate questions for a single chunk of personas"""
    
    # Use the existing generate_questions_single logic but with the persona chunk
    return await generate_questions_single(
        audit_id, brand_name, brand_description, brand_domain, product_name, topics, personas
    )

async def generate_questions_single(
    audit_id: str,
    brand_name: str,
    brand_description: str,
    brand_domain: str,
    product_name: str,
    topics: List[Dict],
    personas: List[Dict],
    max_retries: int = 3
) -> Tuple[bool, List[Question], str, float, Optional[Dict]]:
    """Generate questions using single API call with retry logic"""
    
    start_time = time.time()
    
    # Check API key
    api_key = get_groq_api_key()
    if not api_key:
        logger.error("🔑 No GroqCloud API key available")
        processing_time = time.time() - start_time
        return False, [], "no_api_key", processing_time, 0

    logger.info(f"🤖 Generating questions for {len(personas)} personas and {len(topics)} topics")
    logger.info(f"📊 Expected questions: {len(personas) * 10}")
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"🔄 Generation attempt {attempt + 1}/{max_retries + 1}")
            
            # Create the prompt
            prompt = create_question_generation_prompt(brand_name, brand_description, brand_domain, product_name, topics, personas)
            logger.info(f"📝 Prompt length: {len(prompt)} characters")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": GroqConfig.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an expert consumer research analyst. Generate exactly {len(personas) * 10} specific, actionable questions for brand analysis - exactly 10 questions per persona. Always respond with ONLY a valid JSON array in this format: [{{\"text\": \"question\", \"personaId\": \"exact_id\", \"topicName\": \"topic\", \"queryType\": \"brand_analysis\"}}, ...]"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": GroqConfig.MAX_TOKENS,
                "temperature": GroqConfig.TEMPERATURE
            }
            
            logger.info(f"🌐 Making API request to GroqCloud...")
            logger.info(f"⚙️ Config: model={GroqConfig.MODEL}, max_tokens={GroqConfig.MAX_TOKENS}, temp={GroqConfig.TEMPERATURE}")

            # Make API request with timeout
            timeout = httpx.Timeout(GroqConfig.TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(GroqConfig.BASE_URL, headers=headers, json=payload)
                
                logger.info(f"📡 API Response: status={response.status_code}")
                
                # Handle API errors
                if response.status_code != 200:
                    logger.error(f"GroqCloud API error: {response.status_code} - {response.text}")
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 2
                        logger.info(f"⏳ Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        processing_time = time.time() - start_time
                        return False, [], "api_error", processing_time, 0

                # Parse response
                response_data = response.json()
                ai_content = response_data["choices"][0]["message"]["content"]
                token_usage = response_data.get("usage", {})
                
                logger.info(f"📥 AI Response length: {len(ai_content)} characters")
                logger.info(f"🔢 Token usage: {token_usage}")

                # Parse questions from AI response
                logger.info(f"🔄 Attempting to parse AI response...")
                questions = parse_questions_from_response(ai_content, personas)
                
                if questions:
                    logger.info(f"✅ Successfully parsed {len(questions)} questions")
                    # Verify we got a reasonable number of questions (lowered threshold)
                    expected_questions = len(personas) * 10
                    if len(questions) >= expected_questions * 0.5:  # Allow 50% variance (was 0.7)
                        # Set audit ID for all questions
                        for question in questions:
                            question.auditId = audit_id
                        
                        processing_time = time.time() - start_time
                        logger.info(f"✅ Generated {len(questions)} questions in {processing_time:.2f}s")
                        return True, questions, "ai", processing_time, token_usage
                    else:
                        logger.warning(f"⚠️ Only got {len(questions)} questions, expected ~{expected_questions}")
                        if attempt < max_retries:
                            wait_time = (attempt + 1) * 2
                            logger.info(f"⏳ Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            # 🆕 CHANGED: Even if below threshold, return what we have instead of failing
                            logger.warning(f"⚠️ Returning {len(questions)} questions despite being below threshold")
                            for question in questions:
                                question.auditId = audit_id
                            processing_time = time.time() - start_time
                            return True, questions, "ai_partial", processing_time, token_usage
                else:
                    logger.warning(f"🔄 Failed to parse AI response on attempt {attempt + 1}")
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 2
                        logger.info(f"⏳ Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("❌ Failed to parse AI response after all retries")
                        processing_time = time.time() - start_time
                        return False, [], "parsing_failed", processing_time, 0

        except httpx.TimeoutException:
            logger.error(f"GroqCloud API request timed out on attempt {attempt + 1}")
            if attempt < max_retries:
                wait_time = (attempt + 1) * 3  # Longer wait for timeouts
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                continue
            else:
                processing_time = time.time() - start_time
                return False, [], "timeout", processing_time, 0
        
        except Exception as e:
            logger.error(f"❌ Error in generate_questions_single attempt {attempt + 1}: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            if attempt < max_retries:
                wait_time = (attempt + 1) * 2
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                continue
            else:
                processing_time = time.time() - start_time
                return False, [], "error", processing_time, 0

    # This should never be reached, but just in case
    processing_time = time.time() - start_time
    logger.error("❌ Unexpected: Reached end of function without returning")
    return False, [], "max_retries_exceeded", processing_time, 0

# API ENDPOINTS

@router.post("/generate", response_model=QuestionsResponse)
# @limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}")
async def generate_questions(request: Request, body: QuestionGenerateRequest):
    """
    Generate questions using GroqCloud AI with intelligent chunking for large requests
    Only returns AI-generated questions - no fallback questions
    """
    start_time = time.time()
    
    # Validate API key
    api_key = get_groq_api_key()
    
    if not api_key:
        logger.error("🔑 No GroqCloud API key available")
        processing_time = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable: API key not configured"
        )

    try:
        logger.info(f"🤖 Generating questions for {len(body.personas)} personas and {len(body.topics)} topics...")
        
        # 🆕 INTELLIGENT CHUNKING DECISION
        use_chunking = should_use_chunking(body.personas, body.topics)
        
        if use_chunking:
            logger.info(f"🔄 Using chunked generation strategy (estimated {len(body.personas) * 10} questions)")
            success, questions, source, processing_time_sec, token_usage = await generate_questions_chunked(
                body.auditId, body.brandName, body.brandDescription, body.brandDomain,
                body.productName, body.topics, body.personas
            )
        else:
            logger.info(f"🚀 Using single request strategy (estimated {len(body.personas) * 10} questions)")
            success, questions, source, processing_time_sec, token_usage = await generate_questions_single(
                body.auditId, body.brandName, body.brandDescription, body.brandDomain,
                body.productName, body.topics, body.personas
            )
        
        if success and questions:
            processing_time_ms = int(processing_time_sec * 1000)
            logger.info(f"✅ Successfully generated {len(questions)} questions via {source}")
            
            return QuestionsResponse(
                success=True,
                questions=questions,
                source=source,
                processingTime=processing_time_ms,
                tokenUsage=token_usage.get("total_tokens", 0) if isinstance(token_usage, dict) else (token_usage if isinstance(token_usage, int) else 0)
            )
        else:
            # All AI generation strategies failed
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"❌ All AI generation strategies failed after retries")
            raise HTTPException(
                status_code=503,
                detail=f"AI question generation failed: {source}. Please try again later."
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in generate_questions: {e}")
        processing_time_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during question generation: {str(e)}"
        )

@router.post("/store", response_model=QuestionsStoreResponse)
async def store_questions(body: QuestionsStoreRequest):
    """
    Store generated questions in the database
    """
    try:
        supabase = get_supabase_client()
        
        # Prepare data for insertion
        questions_data = []
        for question in body.questions:
            question_data = {
                "query_id": question.id,
                "audit_id": question.auditId,
                "persona": question.personaId,
                "query_text": question.text,
                "query_type": question.queryType,
                "topic_name": question.topicName
            }
            questions_data.append(question_data)
        
        # Insert questions
        result = supabase.table("queries").insert(questions_data).execute()
        
        # Check for errors
        if hasattr(result, 'error') and result.error:
            raise HTTPException(
                status_code=400,
                detail=f"Database insertion failed: {result.error}"
            )
        
        stored_count = len(result.data) if result.data else 0
        
        logger.info(f"✅ Stored {stored_count} questions for audit {body.auditId}")
        
        return QuestionsStoreResponse(
            success=True,
            storedCount=stored_count,
            message=f"Successfully stored {stored_count} questions"
        )
        
    except Exception as e:
        logger.error(f"❌ Error storing questions: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/by-audit/{audit_id}", response_model=QuestionsRetrieveResponse)
async def get_questions_by_audit(audit_id: str = Path(..., description="Audit ID")):
    """
    Retrieve questions for a specific audit
    """
    try:
        supabase = get_supabase_client()
        
        # Query questions by audit ID
        result = supabase.table("queries").select("*").eq("audit_id", audit_id).execute()
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(
                status_code=400,
                detail=f"Database query failed: {result.error}"
            )
        
        # Convert database records to Question objects
        questions = []
        if result.data:
            for row in result.data:
                question = Question(
                    id=row["query_id"],
                    text=row["query_text"],
                    personaId=row["persona"],
                    auditId=row["audit_id"],
                    topicName=row.get("topic_name"),
                    queryType=row.get("query_type", "brand_analysis")
                )
                questions.append(question)
        
        logger.info(f"✅ Retrieved {len(questions)} questions for audit {audit_id}")
        
        return QuestionsRetrieveResponse(
            success=True,
            questions=questions,
            message=f"Retrieved {len(questions)} questions"
        )
        
    except Exception as e:
        logger.error(f"❌ Error retrieving questions: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/retry-failed-personas", response_model=QuestionsResponse)
async def retry_failed_personas(request: Request, body: QuestionGenerateRequest):
    """
    Retry question generation for personas that failed or have insufficient questions
    """
    start_time = time.time()
    
    # Validate API key
    api_key = get_groq_api_key()
    if not api_key:
        logger.error("🔑 No GroqCloud API key available")
        processing_time = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable: API key not configured"
        )

    try:
        logger.info(f"🔄 Retrying question generation for failed personas...")
        
        # Check existing questions for this audit
        supabase = get_supabase_client()
        existing_result = supabase.table("queries").select("*").eq("audit_id", body.auditId).execute()
        
        # Group existing questions by persona
        existing_questions_by_persona = {}
        if existing_result.data:
            for q in existing_result.data:
                persona_id = q.get("persona")
                if persona_id not in existing_questions_by_persona:
                    existing_questions_by_persona[persona_id] = []
                existing_questions_by_persona[persona_id].append(q)
        
        # Identify personas that need retries (< 8 questions per persona)
        failed_personas = []
        for persona in body.personas:
            persona_id = persona.get("id")
            existing_count = len(existing_questions_by_persona.get(persona_id, []))
            if existing_count < 8:  # Threshold for retry
                logger.info(f"🔄 Persona {persona.get('name')} ({persona_id}) has {existing_count} questions, needs retry")
                failed_personas.append(persona)
            else:
                logger.info(f"✅ Persona {persona.get('name')} ({persona_id}) has {existing_count} questions, skipping")
        
        if not failed_personas:
            logger.info("✅ All personas have sufficient questions, no retry needed")
            # Return existing questions
            all_questions = []
            for persona_questions in existing_questions_by_persona.values():
                for q in persona_questions:
                    question = Question(
                        id=q["query_id"],
                        text=q["query_text"],
                        personaId=q["persona"],
                        auditId=q["audit_id"],
                        topicName=q.get("topic_name"),
                        queryType=q.get("query_type", "brand_analysis")
                    )
                    all_questions.append(question)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            return QuestionsResponse(
                success=True,
                questions=all_questions,
                source="existing",
                processingTime=processing_time_ms,
                tokenUsage=0
            )
        
        # Generate questions only for failed personas
        logger.info(f"🔄 Generating questions for {len(failed_personas)} failed personas")
        
        success, new_questions, source, processing_time_sec, token_usage = await generate_questions_single(
            body.auditId, body.brandName, body.brandDescription, body.brandDomain,
            body.productName, body.topics, failed_personas
        )
        
        if success and new_questions:
            # Store new questions
            questions_data = []
            for question in new_questions:
                question_data = {
                    "query_id": question.id,
                    "audit_id": question.auditId,
                    "persona": question.personaId,
                    "query_text": question.text,
                    "query_type": question.queryType,
                    "topic_name": question.topicName
                }
                questions_data.append(question_data)
            
            store_result = supabase.table("queries").insert(questions_data).execute()
            if hasattr(store_result, 'error') and store_result.error:
                logger.error(f"❌ Failed to store retry questions: {store_result.error}")
            
            # Combine with existing questions
            all_questions = []
            
            # Add existing questions
            for persona_questions in existing_questions_by_persona.values():
                for q in persona_questions:
                    question = Question(
                        id=q["query_id"],
                        text=q["query_text"],
                        personaId=q["persona"],
                        auditId=q["audit_id"],
                        topicName=q.get("topic_name"),
                        queryType=q.get("query_type", "brand_analysis")
                    )
                    all_questions.append(question)
            
            # Add new questions
            all_questions.extend(new_questions)
            
            processing_time_ms = int(processing_time_sec * 1000)
            logger.info(f"✅ Retry successful: {len(new_questions)} new questions, {len(all_questions)} total")
            
            return QuestionsResponse(
                success=True,
                questions=all_questions,
                source=f"retry_{source}",
                processingTime=processing_time_ms,
                tokenUsage=token_usage.get("total_tokens", 0) if isinstance(token_usage, dict) else (token_usage if isinstance(token_usage, int) else 0)
            )
        else:
            # Return existing questions even if retry failed
            all_questions = []
            for persona_questions in existing_questions_by_persona.values():
                for q in persona_questions:
                    question = Question(
                        id=q["query_id"],
                        text=q["query_text"],
                        personaId=q["persona"],
                        auditId=q["audit_id"],
                        topicName=q.get("topic_name"),
                        queryType=q.get("query_type", "brand_analysis")
                    )
                    all_questions.append(question)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.warning(f"⚠️ Retry failed, returning {len(all_questions)} existing questions")
            
            return QuestionsResponse(
                success=True,
                questions=all_questions,
                source="existing_partial",
                processingTime=processing_time_ms,
                tokenUsage=0
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in retry_failed_personas: {e}")
        processing_time_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during retry: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check for questions service"""
    api_key = get_groq_api_key()
    
    return {
        "status": "healthy",
        "services": {
            "groqapi": "available" if api_key else "unavailable",
            "database": "available" if settings.has_supabase_config else "unavailable"
        },
        "timestamp": time.time()
    } 