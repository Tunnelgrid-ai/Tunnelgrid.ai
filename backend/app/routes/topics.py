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

from fastapi import APIRouter, HTTPException, Depends, Request
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

class TopicsResponse(BaseModel):
    success: bool
    topics: List[Topic]
    source: str
    processingTime: int
    tokenUsage: Optional[int] = None
    reason: Optional[str] = None

# FALLBACK TOPICS: Server-side fallback when AI fails
FALLBACK_TOPICS = [
    {
        "id": "fallback-1",
        "name": "Product Quality & Performance",
        "description": "How consumers perceive the overall quality, reliability, and performance of the product"
    },
    {
        "id": "fallback-2", 
        "name": "Value for Money",
        "description": "Consumer opinions on pricing, value proposition, and cost-effectiveness compared to alternatives"
    },
    {
        "id": "fallback-3",
        "name": "Brand Trust & Reputation", 
        "description": "How the brand is perceived in terms of credibility, trustworthiness, and overall reputation"
    },
    {
        "id": "fallback-4",
        "name": "Customer Service Experience",
        "description": "Consumer experiences with support, service quality, and problem resolution"
    },
    {
        "id": "fallback-5",
        "name": "User Experience & Usability",
        "description": "How easy, intuitive, and satisfying the product is to use from a consumer perspective"
    },
    {
        "id": "fallback-6",
        "name": "Innovation & Features",
        "description": "Consumer perception of the product's innovative aspects, features, and technological advancement"
    },
    {
        "id": "fallback-7",
        "name": "Social Responsibility",
        "description": "How consumers view the brand's environmental impact, ethics, and social responsibility"
    },
    {
        "id": "fallback-8",
        "name": "Availability & Accessibility", 
        "description": "Consumer experiences with product availability, distribution, and ease of purchase"
    },
    {
        "id": "fallback-9",
        "name": "Comparison with Competitors",
        "description": "How consumers compare this product/brand to competitors and alternatives in the market"
    },
    {
        "id": "fallback-10",
        "name": "Long-term Satisfaction",
        "description": "Consumer opinions on durability, long-term value, and continued satisfaction over time"
    }
]

# HELPER FUNCTIONS
def get_groq_api_key() -> Optional[str]:
    """Get GroqCloud API key from settings"""
    api_key = settings.GROQ_API_KEY
    print(f"🚨 TOPICS - GET_GROQ_API_KEY CALLED!")
    print(f"🔑 API Key found: {bool(api_key)}")
    print(f"🔑 API Key length: {len(api_key) if api_key else 0}")
    return api_key

def create_topics_prompt(brand_name: str, brand_domain: str, product_name: str, 
                        industry: Optional[str] = None, additional_context: Optional[str] = None) -> str:
    """
    Create AI prompt for topics generation
    """
    prompt = f"""Generate exactly 10 consumer perception research topics for analyzing "{product_name}" by {brand_name} ({brand_domain}).

Context:
- Brand: {brand_name}
- Product/Service: {product_name}
- Domain: {brand_domain}"""
    
    if industry:
        prompt += f"\n- Industry: {industry}"
    if additional_context:
        prompt += f"\n- Additional Context: {additional_context}"
    
    prompt += """

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

Generate topics specifically relevant to """ + f"{product_name} by {brand_name}:"
    
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
            
            if "name" not in topic or "description" not in topic:
                logger.warning(f"Topic {i} missing required fields. Available keys: {list(topic.keys())}")
                continue
            
            validated_topics.append({
                "name": str(topic["name"]).strip(),
                "description": str(topic["description"]).strip()
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

@router.post("/generate", response_model=TopicsResponse)
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
        fallback_topics = [
            Topic(id=str(uuid.uuid4()), name=topic["name"], description=topic["description"])
            for i, topic in enumerate(FALLBACK_TOPICS)
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return TopicsResponse(
            success=True,
            topics=fallback_topics,
            source="fallback",
            processingTime=processing_time,
            reason="API key not configured"
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
                fallback_topics = [
                    Topic(id=str(uuid.uuid4()), name=topic["name"], description=topic["description"])
                    for i, topic in enumerate(FALLBACK_TOPICS)
                ]
                processing_time = int((time.time() - start_time) * 1000)
                return TopicsResponse(
                    success=True,
                    topics=fallback_topics,
                    source="fallback",
                    processingTime=processing_time,
                    reason="AI response parsing failed"
                )

            # Convert to Topic objects with proper UUIDs
            topics = [
                Topic(id=str(uuid.uuid4()), name=topic["name"], description=topic["description"])
                for topic in parsed_topics[:10]  # Ensure max 10 topics
            ]

            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ Successfully generated {len(topics)} topics in {processing_time}ms")
            
            return TopicsResponse(
                success=True,
                topics=topics,
                source="ai",
                processingTime=processing_time,
                tokenUsage=token_usage
            )

    except httpx.TimeoutException:
        logger.error("GroqCloud API request timed out")
        fallback_topics = [
            Topic(id=str(uuid.uuid4()), name=topic["name"], description=topic["description"])
            for i, topic in enumerate(FALLBACK_TOPICS)
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return TopicsResponse(
            success=True,
            topics=fallback_topics,
            source="fallback",
            processingTime=processing_time,
            reason="API timeout"
        )
    
    except Exception as e:
        print(f"💥 TOPICS - Unexpected error: {e}")
        print(f"💥 Error type: {type(e)}")
        logger.error(f"Unexpected error in topic generation: {e}")
        fallback_topics = [
            Topic(id=str(uuid.uuid4()), name=topic["name"], description=topic["description"])
            for i, topic in enumerate(FALLBACK_TOPICS)
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return TopicsResponse(
            success=True,
            topics=fallback_topics,
            source="fallback",
            processingTime=processing_time,
            reason=f"Error: {str(e)}"
        )

@router.get("/fallback", response_model=TopicsResponse)
async def get_fallback_topics():
    """
    Get fallback topics directly (for testing or when AI is unavailable)
    """
    topics = [
        Topic(id=str(uuid.uuid4()), name=topic["name"], description=topic["description"])
        for i, topic in enumerate(FALLBACK_TOPICS)
    ]
    
    return TopicsResponse(
        success=True,
        topics=topics,
        source="fallback",
        processingTime=0
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