"""
TOPICS API ROUTES - SECURE FASTAPI IMPLEMENTATION

PURPOSE: Provides secure server-side API for AI-powered topics generation

SECURITY BENEFITS:
- API keys stored securely on server-side only  
- Rate limiting and usage monitoring
- Proper error handling and logging
- Input validation and sanitization

ENDPOINTS:
- POST /generate - Generate topics using GroqCloud AI
- GET /fallback - Get fallback topics when AI fails
- GET /health - Health check endpoint

ARCHITECTURE:
Frontend → FastAPI Backend → GroqCloud → Backend → Frontend
"""

import time
import json
import httpx
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from ..core.config import settings
from ..models.common import HealthResponse

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

# REQUEST MODELS: Input validation with Pydantic
class TopicsGenerateRequest(BaseModel):
    brandName: str = Field(..., min_length=1, max_length=100, description="Brand name")
    brandDomain: str = Field(..., min_length=1, max_length=255, description="Brand domain/website")
    productName: str = Field(..., min_length=1, max_length=200, description="Product or service name")
    industry: Optional[str] = Field(None, max_length=100, description="Industry category")
    additionalContext: Optional[str] = Field(None, max_length=500, description="Additional context")
    
    @validator('brandName', 'brandDomain', 'productName')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()
    
    @validator('industry', 'additionalContext')
    def validate_optional_fields(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

# RESPONSE MODELS
class Topic(BaseModel):
    id: str
    name: str
    description: str
    category: str = Field(..., pattern="^(unbranded|branded|comparative)$")

class TopicsGenerateResponse(BaseModel):
    topics: List[Topic]
    source: str = Field(..., description="Source of topics: 'ai' or 'fallback'")
    message: str = Field(..., description="Success message")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")

class HealthCheckResponse(BaseModel):
    status: str
    services: Dict[str, str]
    message: str

class TopicUpdateRequest(BaseModel):
    """Request model for updating a topic"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated topic name")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated topic description")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

class TopicUpdateResponse(BaseModel):
    """Response model for updating a topic"""
    success: bool
    message: str
    topic: Optional[Topic] = None
    errors: Optional[List[str]] = None

# HELPER FUNCTIONS
def get_groq_api_key() -> Optional[str]:
    """Get GroqCloud API key from settings"""
    api_key = settings.GROQ_API_KEY
    print(f"🚨 TOPICS - GET_GROQ_API_KEY CALLED!")
    print(f"🔑 API Key found: {bool(api_key)}")
    print(f"🔑 API Key length: {len(api_key) if api_key else 0}")
    return api_key

# FALLBACK TOPICS: Used when AI generation fails
def get_fallback_topics(brand_name: str, product_name: str) -> List[Dict[str, Any]]:
    """
    Provide fallback topics when AI generation fails
    Ensures proper category distribution: 4 unbranded, 3 branded, 3 comparative
    """
    return [
        # Unbranded Topics (4)
        {
            "id": str(uuid.uuid4()),
            "name": f"Best {product_name.split()[-1]} Options",
            "description": f"General recommendations where {brand_name} might be mentioned naturally",
            "category": "unbranded"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"Top Industry Solutions",
            "description": f"Consumer preferences in the {product_name} space",
            "category": "unbranded"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"Popular Platform Reviews",
            "description": f"User experiences with leading platforms",
            "category": "unbranded"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"Market Leaders Analysis",
            "description": f"Discussion of top performers in the market",
            "category": "unbranded"
        },
        # Branded Topics (3)
        {
            "id": str(uuid.uuid4()),
            "name": f"{brand_name} User Experience",
            "description": f"Direct feedback and opinions about {brand_name}",
            "category": "branded"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"{brand_name} Service Quality",
            "description": f"Assessment of {brand_name}'s service quality and reliability",
            "category": "branded"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"{brand_name} Value Proposition",
            "description": f"Discussion of {brand_name}'s unique benefits and value",
            "category": "branded"
        },
        # Comparative Topics (3)
        {
            "id": str(uuid.uuid4()),
            "name": f"{brand_name} vs Competitors",
            "description": f"Direct comparisons between {brand_name} and market alternatives",
            "category": "comparative"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"{brand_name} Feature Comparison",
            "description": f"Comparing specific features and capabilities with rivals",
            "category": "comparative"
        },
        {
            "id": str(uuid.uuid4()),
            "name": f"{brand_name} Market Position",
            "description": f"How {brand_name} ranks against industry competitors",
            "category": "comparative"
        }
    ]

def create_topics_prompt(brand_name: str, brand_domain: str, product_name: str, 
                        industry: Optional[str] = None, additional_context: Optional[str] = None) -> str:
    """
    Create AI prompt for categorized topics generation
    Ensures proper distribution: 4 unbranded, 3 branded, 3 comparative topics
    """
    prompt = f"""Generate exactly 10 consumer perception research topics for analyzing "{product_name}" by {brand_name} ({brand_domain}).

IMPORTANT: Topics must be distributed across these 3 categories with exact counts:

1. UNBRANDED TOPICS (exactly 4 topics):
   - Questions where consumers might mention {brand_name} naturally without direct prompting
   - Example: "Best dating apps for college students" (where {brand_name} might be mentioned)
   - Focus: General industry discussions where your brand could appear organically

2. BRANDED TOPICS (exactly 3 topics):
   - Direct questions specifically about {brand_name}
   - Example: "Is {brand_name} good for serious relationships?"
   - Focus: Direct brand-specific inquiries and discussions

3. COMPARATIVE TOPICS (exactly 3 topics):
   - Questions comparing {brand_name} to specific competitors
   - Example: "Competitor vs {brand_name} for college students"
   - Focus: Head-to-head comparisons with named competitors

Context:
- Brand: {brand_name}
- Product/Service: {product_name}
- Domain: {brand_domain}"""
    
    if industry:
        prompt += f"\n- Industry: {industry}"
    if additional_context:
        prompt += f"\n- Additional Context: {additional_context}"
    
    prompt += f"""

Requirements:
1. Generate exactly 10 topics total (4 unbranded + 3 branded + 3 comparative)
2. Each topic needs: name (2-6 words), description, category
3. Categories must be exactly: "unbranded", "branded", "comparative"
4. Topics should be specific to {product_name} by {brand_name}
5. Use realistic competitor names in comparative topics
6. Make topics natural and conversational

Respond with a JSON array containing exactly 10 objects:
[
  {{
    "name": "Best Dating Apps 2024",
    "description": "General recommendations where users naturally mention top brands",
    "category": "unbranded"
  }},
  {{
    "name": "{brand_name} Success Stories",
    "description": "Direct discussion about {brand_name}'s effectiveness",
    "category": "branded"
  }},
  {{
    "name": "{brand_name} vs Bumble Features",
    "description": "Comparing features between {brand_name} and specific competitors",
    "category": "comparative"
  }}
]

Generate topics specifically relevant to {product_name} by {brand_name}:"""
    
    return prompt

def parse_topics_from_response(response_text: str) -> Optional[List[Dict[str, str]]]:
    """
    Parse topics from AI response - handles both object and array formats
    """
    try:
        # Clean response text
        cleaned_text = response_text.strip()
        if not cleaned_text:
            logger.error("Empty response text")
            return None
        
        # Log the raw response for debugging
        logger.info(f"🔍 Raw response (first 200 chars): {cleaned_text[:200]}")
        
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
            logger.info(f"🔧 Extracted JSON: {cleaned_text[:200]}")
        
        # Remove any leading/trailing whitespace after cleaning
        cleaned_text = cleaned_text.strip()
        
        # Log cleaned text
        logger.info(f"🧹 Cleaned response (first 200 chars): {cleaned_text[:200]}")
        
        # Parse JSON
        parsed_response = json.loads(cleaned_text)
        
        # Handle both formats: {"topics": [...]} and [...]
        if isinstance(parsed_response, dict):
            if "topics" in parsed_response:
                topics_data = parsed_response["topics"]
            else:
                logger.warning("Response is object but doesn't contain 'topics' key")
                logger.warning(f"Available keys: {list(parsed_response.keys())}")
                return None
        elif isinstance(parsed_response, list):
            topics_data = parsed_response
        else:
            logger.warning(f"Unexpected response format: {type(parsed_response)}")
            return None
        
        # Validate topics structure
        if not isinstance(topics_data, list):
            logger.warning("Topics data is not a list")
            return None
        
        validated_topics = []
        for i, topic in enumerate(topics_data):
            if not isinstance(topic, dict):
                logger.warning(f"Topic {i} is not a dictionary: {type(topic)}")
                continue
            
            if "name" not in topic or "description" not in topic or "category" not in topic:
                logger.warning(f"Topic {i} missing required fields. Available keys: {list(topic.keys())}")
                continue
            
            # Validate category
            category = str(topic["category"]).strip().lower()
            if category not in ["unbranded", "branded", "comparative"]:
                logger.warning(f"Topic {i} has invalid category '{category}', defaulting to 'unbranded'")
                category = "unbranded"
            
            validated_topics.append({
                "name": str(topic["name"]).strip(),
                "description": str(topic["description"]).strip(),
                "category": category
            })
        
        logger.info(f"✅ Successfully parsed {len(validated_topics)} topics")
        return validated_topics if validated_topics else None
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Failed to parse: '{cleaned_text[:100]}...'")
        return None
    except Exception as e:
        logger.error(f"Error parsing topics response: {e}")
        return None

# API ENDPOINTS

@router.post("/generate", response_model=TopicsGenerateResponse)
# @limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}")
async def generate_topics(request: Request, body: TopicsGenerateRequest):
    """
    Generate topics using GroqCloud AI with enhanced error handling and fallback
    """
    start_time = time.time()
    
    # Validate API key
    api_key = get_groq_api_key()
    if not api_key:
        logger.warning("🔑 No GroqCloud API key available, returning fallback topics")
        fallback_topics_data = get_fallback_topics(body.brandName, body.productName)
        fallback_topics = [
            Topic(id=topic_data["id"], name=topic_data["name"], description=topic_data["description"], category=topic_data["category"])
            for topic_data in fallback_topics_data
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return TopicsGenerateResponse(
            topics=fallback_topics,
            source="fallback",
            message="Fallback topics provided due to missing API key",
            processing_time_ms=processing_time
        )

    try:
        # Create AI prompt
        prompt = create_topics_prompt(
            body.brandName, 
            body.brandDomain, 
            body.productName, 
            body.industry, 
            body.additionalContext
        )

        # Prepare GroqCloud API request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": GroqConfig.MODEL,
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
            "max_tokens": GroqConfig.MAX_TOKENS,
            "temperature": GroqConfig.TEMPERATURE
        }

        # Make API request with timeout
        timeout = httpx.Timeout(GroqConfig.TIMEOUT)
        print(f"🚨 TOPICS - Making GroqCloud API call...")
        print(f"🌐 URL: {GroqConfig.BASE_URL}")
        print(f"🎯 Model: {GroqConfig.MODEL}")
        print(f"⏱️ Timeout: {GroqConfig.TIMEOUT}")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(GroqConfig.BASE_URL, headers=headers, json=payload)
            
            print(f"📡 Response status: {response.status_code}")
            
            # Handle API errors
            if response.status_code != 200:
                error_text = response.text
                print(f"❌ GroqCloud API error: {response.status_code}")
                print(f"❌ Error response: {error_text}")
                logger.error(f"GroqCloud API error: {response.status_code} - {error_text}")
                raise HTTPException(status_code=response.status_code, detail=f"AI API error: {error_text}")

            # Parse response
            response_data = response.json()
            print(f"✅ GroqCloud API call successful!")
            print(f"📋 Response keys: {list(response_data.keys())}")
            
            ai_content = response_data["choices"][0]["message"]["content"]
            token_usage = response_data.get("usage", {}).get("total_tokens", 0)
            
            print(f"📏 Content length: {len(ai_content)}")
            print(f"🎯 Token usage: {token_usage}")
            print(f"🔍 Raw AI Content: '{ai_content[:500]}{'...' if len(ai_content) > 500 else ''}'")

            # Parse topics from AI response
            parsed_topics = parse_topics_from_response(ai_content)
            
            if not parsed_topics:
                logger.warning("Failed to parse AI response, returning fallback topics")
                fallback_topics_data = get_fallback_topics(body.brandName, body.productName)
                fallback_topics = [
                    Topic(id=topic_data["id"], name=topic_data["name"], description=topic_data["description"], category=topic_data["category"])
                    for topic_data in fallback_topics_data
                ]
                processing_time = int((time.time() - start_time) * 1000)
                return TopicsGenerateResponse(
                    topics=fallback_topics,
                    source="fallback",
                    message="AI response parsing failed, returning fallback topics",
                    processing_time_ms=processing_time
                )

            # Convert to Topic objects with proper UUIDs and validate categories
            topics = []
            for topic in parsed_topics[:10]:  # Ensure max 10 topics
                # Validate required fields
                if not all(key in topic for key in ["name", "description", "category"]):
                    logger.warning(f"Skipping invalid topic: {topic}")
                    continue
                
                # Validate category
                if topic["category"] not in ["unbranded", "branded", "comparative"]:
                    logger.warning(f"Invalid category '{topic['category']}', defaulting to 'unbranded'")
                    topic["category"] = "unbranded"
                
                topics.append(Topic(
                    id=str(uuid.uuid4()), 
                    name=topic["name"], 
                    description=topic["description"],
                    category=topic["category"]
                ))
            
            # Validate category distribution
            category_counts = {}
            for topic in topics:
                category_counts[topic.category] = category_counts.get(topic.category, 0) + 1
            
            expected_distribution = {"unbranded": 4, "branded": 3, "comparative": 3}
            if category_counts != expected_distribution:
                logger.warning(f"Category distribution doesn't match expected: {category_counts} vs {expected_distribution}")
                # Use fallback topics if distribution is wrong
                fallback_topics_data = get_fallback_topics(body.brandName, body.productName)
                topics = [
                    Topic(id=topic_data["id"], name=topic_data["name"], description=topic_data["description"], category=topic_data["category"])
                    for topic_data in fallback_topics_data
                ]

            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ Successfully generated {len(topics)} topics in {processing_time}ms")
            
            return TopicsGenerateResponse(
                topics=topics,
                source="ai",
                message="Topics generated successfully",
                processing_time_ms=processing_time
            )

    except httpx.TimeoutException:
        logger.error("GroqCloud API request timed out")
        fallback_topics_data = get_fallback_topics(body.brandName, body.productName)
        fallback_topics = [
            Topic(id=topic_data["id"], name=topic_data["name"], description=topic_data["description"], category=topic_data["category"])
            for topic_data in fallback_topics_data
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return TopicsGenerateResponse(
            topics=fallback_topics,
            source="fallback",
            message="API timeout, returning fallback topics",
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        print(f"💥 TOPICS - Unexpected error: {e}")
        print(f"💥 Error type: {type(e)}")
        logger.error(f"Unexpected error in topic generation: {e}")
        fallback_topics_data = get_fallback_topics(body.brandName, body.productName)
        fallback_topics = [
            Topic(id=topic_data["id"], name=topic_data["name"], description=topic_data["description"], category=topic_data["category"])
            for topic_data in fallback_topics_data
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return TopicsGenerateResponse(
            topics=fallback_topics,
            source="fallback",
            message=f"Error: {str(e)}, returning fallback topics",
            processing_time_ms=processing_time
        )

@router.get("/fallback", response_model=TopicsGenerateResponse)
async def get_fallback_topics_endpoint(request: Request):
    """
    Get fallback topics directly (for testing or when AI is unavailable)
    """
    # This endpoint is primarily for testing and should not use the AI model
    # It will return a fixed set of fallback topics
    fallback_topics_data = get_fallback_topics("BrandName", "ProductName") # Placeholder for testing
    fallback_topics = [
        Topic(id=topic_data["id"], name=topic_data["name"], description=topic_data["description"], category=topic_data["category"])
        for topic_data in fallback_topics_data
    ]
    
    return TopicsGenerateResponse(
        topics=fallback_topics,
        source="fallback",
        message="Fallback topics provided for testing",
        processing_time_ms=0
    )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check for topics service
    """
    services = {
        "topics_api": "running",
        "groqcloud": "available" if settings.has_groq_config else "unavailable"
    }
    
    return HealthResponse(
        status="healthy",
        services=services,
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.ENVIRONMENT
    )

@router.put("/{topic_id}", response_model=TopicUpdateResponse)
async def update_topic(
    topic_id: str = Path(..., description="Topic ID"),
    body: TopicUpdateRequest = ...
):
    """
    Update a specific topic's name and/or description
    """
    try:
        from ..core.database import get_supabase_client
        supabase = get_supabase_client()
        
        # Validate that at least one field is provided for update
        update_data = {}
        if body.name is not None:
            update_data["topic_name"] = body.name
        if body.description is not None:
            update_data["topic_type"] = body.description  # Note: topic_type is used for description in DB
            
        if not update_data:
            return TopicUpdateResponse(
                success=False,
                message="No valid fields provided for update",
                errors=["At least one field (name or description) must be provided"]
            )
        
        # Update the topic in database
        result = supabase.table("topics").update(update_data).eq("topic_id", topic_id).execute()
        
        # Check for errors
        if hasattr(result, 'error') and result.error:
            return TopicUpdateResponse(
                success=False,
                message=f"Database update failed: {result.error}",
                errors=[str(result.error)]
            )
        
        if not result.data or len(result.data) == 0:
            return TopicUpdateResponse(
                success=False,
                message="Topic not found or not updated",
                errors=["Topic with the specified ID was not found"]
            )
        
        # Convert updated data back to Topic model
        updated_data = result.data[0]
        updated_topic = Topic(
            id=updated_data["topic_id"],
            name=updated_data["topic_name"],
            description=updated_data.get("topic_type", ""),
            category=updated_data.get("topic_category", "unbranded")
        )
        
        logger.info(f"✅ Updated topic {topic_id}")
        
        return TopicUpdateResponse(
            success=True,
            message="Topic updated successfully",
            topic=updated_topic
        )
        
    except Exception as e:
        logger.error(f"❌ Error updating topic: {e}")
        return TopicUpdateResponse(
            success=False,
            message=f"Failed to update topic: {str(e)}",
            errors=[str(e)]
        ) 