"""
PERSONAS API ROUTES - AI-POWERED PERSONA GENERATION

PURPOSE: Provides secure server-side API for AI-powered personas generation

SECURITY BENEFITS:
- API keys stored securely on server-side only  
- Rate limiting and usage monitoring
- Proper error handling and logging
- Input validation and sanitization

ENDPOINTS:
- POST /generate - Generate personas using GroqCloud AI
- POST /store - Store generated personas in database
- GET /by-audit/{audit_id} - Get personas for a specific audit
- GET /fallback - Get fallback personas when AI fails

ARCHITECTURE:
Frontend → FastAPI Backend → GroqCloud → Backend → Frontend
"""

import time
import json
import httpx
import asyncio
import uuid
from typing import List, Dict, Any, Optional

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
from ..models.personas import (
    PersonaGenerateRequest, PersonasResponse, Persona, Demographics,
    PersonaStoreRequest, PersonaStoreResponse
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

# FALLBACK PERSONAS: Used when AI is unavailable
FALLBACK_PERSONAS = [
    {
        "name": "Tech Professional",
        "description": "Technology professionals who are looking for advanced solutions to improve workflow efficiency.",
        "painPoints": ["Limited time for research", "Complex integration requirements", "Need for reliable support"],
        "motivators": ["Productivity improvements", "Time savings", "Cutting-edge features"],
        "demographics": {
            "ageRange": "28-45",
            "gender": "All genders",
            "location": "Urban areas",
            "goals": ["Streamline workflows", "Reduce overhead costs"]
        }
    },
    {
        "name": "Small Business Owner",
        "description": "Entrepreneurs and small business owners seeking cost-effective solutions.",
        "painPoints": ["Budget constraints", "Limited technical knowledge", "Need for simple solutions"],
        "motivators": ["Cost savings", "Easy implementation", "Growth opportunities"],
        "demographics": {
            "ageRange": "30-55",
            "gender": "All genders",
            "location": "Nationwide",
            "goals": ["Expand customer base", "Optimize operations"]
        }
    },
    {
        "name": "Creative Professional",
        "description": "Designers, writers, and content creators who need tools to enhance their creative output.",
        "painPoints": ["Deadline pressures", "Need for inspiration", "Technical limitations"],
        "motivators": ["Enhanced creative freedom", "Collaboration features", "Portfolio showcase options"],
        "demographics": {
            "ageRange": "25-40",
            "gender": "All genders",
            "location": "Urban creative hubs",
            "goals": ["Improve creative output", "Find new clients"]
        }
    },
    {
        "name": "Enterprise Manager",
        "description": "Mid to senior-level managers in large organizations who need scalable solutions for their teams.",
        "painPoints": ["Team coordination challenges", "Compliance requirements", "ROI measurement"],
        "motivators": ["Team efficiency", "Scalability", "Management visibility"],
        "demographics": {
            "ageRange": "35-50",
            "gender": "All genders",
            "location": "Major business centers",
            "goals": ["Improve team performance", "Meet KPIs"]
        }
    },
    {
        "name": "Startup Founder",
        "description": "Early-stage entrepreneurs building new products and need flexible, cost-effective tools.",
        "painPoints": ["Limited budget", "Rapid scaling needs", "Resource constraints"],
        "motivators": ["Flexibility", "Cost-effectiveness", "Future-proof solutions"],
        "demographics": {
            "ageRange": "25-40",
            "gender": "All genders",
            "location": "Tech hubs and cities",
            "goals": ["Build MVP", "Scale rapidly"]
        }
    },
    {
        "name": "Digital Marketer",
        "description": "Marketing professionals focused on digital channels and data-driven campaigns.",
        "painPoints": ["Attribution challenges", "Campaign optimization", "ROI tracking"],
        "motivators": ["Better analytics", "Campaign performance", "Audience insights"],
        "demographics": {
            "ageRange": "26-42",
            "gender": "All genders",
            "location": "Urban and suburban",
            "goals": ["Increase conversions", "Optimize ad spend"]
        }
    },
    {
        "name": "Freelancer",
        "description": "Independent professionals who need affordable, reliable tools to manage their business.",
        "painPoints": ["Inconsistent income", "Client management", "Time tracking"],
        "motivators": ["Affordability", "Simplicity", "Professional image"],
        "demographics": {
            "ageRange": "24-45",
            "gender": "All genders",
            "location": "Global, remote-first",
            "goals": ["Stable income", "Work-life balance"]
        }
    }
]

# HELPER FUNCTIONS

def get_groq_api_key() -> Optional[str]:
    """Get GroqCloud API key from settings"""
    return settings.GROQ_API_KEY

def create_personas_prompt(brand_name: str, brand_description: str, brand_domain: str, product_name: str, 
                         topics: List[str], industry: Optional[str] = None, 
                         additional_context: Optional[str] = None) -> str:
    """
    Create AI prompt for personas generation
    """
    prompt = f"""You MUST generate exactly 7 distinct customer personas for "{product_name}" by {brand_name} ({brand_domain}).

Context:
- Brand: {brand_name}
- Brand Description: {brand_description}
- Product/Service: {product_name}
- Domain: {brand_domain}"""
    
    if industry:
        prompt += f"\n- Industry: {industry}"
    
    if topics:
        prompt += f"\n- Research Topics: {', '.join(topics)}"
    
    if additional_context:
        prompt += f"\n- Additional Context: {additional_context}"
    
    prompt += """

CRITICAL REQUIREMENTS:
1. You MUST generate exactly 7 personas (not more, not less)
2. Each persona must represent a completely different target customer segment
3. Focus on realistic, well-researched customer profiles that align with the research topics
4. Each persona requires:
   - Clear, descriptive name (2-4 words, e.g., "Tech Professional", "Budget-Conscious Parent")
   - Detailed description of who they are and what they need
   - 3-5 specific pain points they experience
   - 3-5 motivators that drive their purchase decisions
   - Demographics including age range, gender, location, and 2-3 specific goals

RESPONSE FORMAT:
You must respond with a valid JSON array containing exactly 7 objects. Do not include any other text.

Each object must have:
- "name": string (persona name, 2-4 words)
- "description": string (detailed description of who they are and their needs)
- "painPoints": array of strings (3-5 specific pain points)
- "motivators": array of strings (3-5 key motivators)
- "demographics": object with:
  - "ageRange": string (e.g., "25-35")
  - "gender": string (e.g., "All genders", "Primarily female")
  - "location": string (e.g., "Urban areas", "Suburban families")
  - "goals": array of strings (2-3 specific goals)

EXAMPLE FORMAT (YOU MUST RETURN EXACTLY 7 PERSONAS):
[
  {
    "name": "Tech Professional",
    "description": "Technology professionals who need efficient solutions to improve workflow and productivity",
    "painPoints": ["Limited time for research", "Complex integration requirements", "Need for reliable support"],
    "motivators": ["Productivity improvements", "Time savings", "Cutting-edge features"],
    "demographics": {
      "ageRange": "28-45",
      "gender": "All genders", 
      "location": "Urban areas",
      "goals": ["Streamline workflows", "Reduce overhead costs"]
    }
  },
  ... (6 more similar objects for a total of 7)
]

Generate 7 personas specifically relevant to """ + f"{product_name} by {brand_name} and informed by the research topics: {', '.join(topics)}. REMEMBER: You must return exactly 7 personas in valid JSON format."
    
    return prompt

def parse_personas_from_response(response_text: str) -> Optional[List[Dict[str, Any]]]:
    """
    Parse personas from AI response with robust error handling
    """
    try:
        # Try to parse as JSON
        parsed = json.loads(response_text)
        
        if not isinstance(parsed, list):
            logger.warning("AI response is not a list")
            return None
            
        if len(parsed) == 0:
            logger.warning("AI response is empty list")
            return None
            
        # Validate each persona structure
        valid_personas = []
        for i, persona_data in enumerate(parsed):
            try:
                if not isinstance(persona_data, dict):
                    logger.warning(f"Persona {i} is not a dict")
                    continue
                    
                # Check required fields
                required_fields = ['name', 'description', 'painPoints', 'motivators']
                if not all(field in persona_data for field in required_fields):
                    logger.warning(f"Persona {i} missing required fields")
                    continue
                    
                # Validate field types
                if not isinstance(persona_data['name'], str) or not persona_data['name'].strip():
                    logger.warning(f"Persona {i} has invalid name")
                    continue
                    
                if not isinstance(persona_data['description'], str) or not persona_data['description'].strip():
                    logger.warning(f"Persona {i} has invalid description")
                    continue
                    
                if not isinstance(persona_data['painPoints'], list) or len(persona_data['painPoints']) == 0:
                    logger.warning(f"Persona {i} has invalid painPoints")
                    continue
                    
                if not isinstance(persona_data['motivators'], list) or len(persona_data['motivators']) == 0:
                    logger.warning(f"Persona {i} has invalid motivators")
                    continue
                
                # Validate demographics if present
                demographics = persona_data.get('demographics', {})
                if demographics and not isinstance(demographics, dict):
                    logger.warning(f"Persona {i} has invalid demographics")
                    demographics = {}
                
                # Clean and validate demographics fields
                if demographics:
                    if 'goals' in demographics and not isinstance(demographics['goals'], list):
                        demographics['goals'] = []
                
                persona_data['demographics'] = demographics
                valid_personas.append(persona_data)
                
            except Exception as e:
                logger.warning(f"Error validating persona {i}: {e}")
                continue
        
        if len(valid_personas) == 0:
            logger.warning("No valid personas found in AI response")
            return None
            
        if len(valid_personas) < 7:
            logger.warning(f"AI returned only {len(valid_personas)} personas, but we need exactly 7. Using fallback personas.")
            return None
            
        if len(valid_personas) > 7:
            logger.info(f"AI returned {len(valid_personas)} personas, using first 7")
            valid_personas = valid_personas[:7]
            
        logger.info(f"Successfully parsed exactly {len(valid_personas)} personas from AI response")
        return valid_personas
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse AI response as JSON: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error parsing personas: {e}")
        return None

# API ENDPOINTS

@router.post("/generate", response_model=PersonasResponse)
# @limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}")
async def generate_personas(request: Request, body: PersonaGenerateRequest):
    """
    Generate personas using GroqCloud AI with enhanced error handling and fallback
    """
    start_time = time.time()
    
    # Validate API key
    api_key = get_groq_api_key()
    if not api_key:
        logger.warning("🔑 No GroqCloud API key available, returning fallback personas")
        fallback_personas = [
            Persona(
                id=str(uuid.uuid4()), 
                name=persona["name"], 
                description=persona["description"],
                painPoints=persona["painPoints"],
                motivators=persona["motivators"],
                demographics=Demographics(**persona.get("demographics", {})),
                productId=body.productId
            )
            for persona in FALLBACK_PERSONAS
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return PersonasResponse(
            success=True,
            personas=fallback_personas,
            source="fallback",
            processingTime=processing_time,
            reason="API key not configured"
        )

    try:
        # Create AI prompt
        prompt = create_personas_prompt(
            body.brandName, 
            body.brandDescription, 
            body.brandDomain, 
            body.productName, 
            body.topics, 
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
                    "content": "You are an expert customer research analyst specializing in persona development. Generate realistic, well-researched customer personas based on brand and product information. Always respond with a valid JSON array containing exactly 7 persona objects."
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
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(GroqConfig.BASE_URL, headers=headers, json=payload)
            
            # Handle API errors
            if response.status_code != 200:
                logger.error(f"GroqCloud API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"AI API error: {response.text}")

            # Parse response
            response_data = response.json()
            ai_content = response_data["choices"][0]["message"]["content"]
            token_usage = response_data.get("usage", {}).get("total_tokens", 0)

            # Parse personas from AI response
            parsed_personas = parse_personas_from_response(ai_content)
            
            if not parsed_personas:
                logger.warning("Failed to parse AI response, returning fallback personas")
                fallback_personas = [
                    Persona(
                        id=str(uuid.uuid4()), 
                        name=persona["name"], 
                        description=persona["description"],
                        painPoints=persona["painPoints"],
                        motivators=persona["motivators"],
                        demographics=Demographics(**persona.get("demographics", {})),
                        productId=body.productId
                    )
                    for persona in FALLBACK_PERSONAS
                ]
                processing_time = int((time.time() - start_time) * 1000)
                return PersonasResponse(
                    success=True,
                    personas=fallback_personas,
                    source="fallback",
                    processingTime=processing_time,
                    reason="AI response parsing failed"
                )

            # Convert to Persona objects with proper UUIDs
            personas = []
            for persona_data in parsed_personas[:7]:  # Ensure max 7 personas
                try:
                    demographics_data = persona_data.get('demographics', {})
                    demographics = Demographics(**demographics_data) if demographics_data else None
                    
                    persona = Persona(
                        id=str(uuid.uuid4()),
                        name=persona_data["name"],
                        description=persona_data["description"],
                        painPoints=persona_data["painPoints"],
                        motivators=persona_data["motivators"],
                        demographics=demographics,
                        productId=body.productId
                    )
                    personas.append(persona)
                except Exception as e:
                    logger.warning(f"Error creating persona object: {e}")
                    continue

            if not personas:
                # If no personas could be created, use fallback
                logger.warning("No personas could be created from AI response, using fallback")
                fallback_personas = [
                    Persona(
                        id=str(uuid.uuid4()), 
                        name=persona["name"], 
                        description=persona["description"],
                        painPoints=persona["painPoints"],
                        motivators=persona["motivators"],
                        demographics=Demographics(**persona.get("demographics", {})),
                        productId=body.productId
                    )
                    for persona in FALLBACK_PERSONAS
                ]
                processing_time = int((time.time() - start_time) * 1000)
                return PersonasResponse(
                    success=True,
                    personas=fallback_personas,
                    source="fallback",
                    processingTime=processing_time,
                    reason="Error creating persona objects"
                )

            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ Successfully generated {len(personas)} personas in {processing_time}ms")
            
            return PersonasResponse(
                success=True,
                personas=personas,
                source="ai",
                processingTime=processing_time,
                tokenUsage=token_usage
            )

    except httpx.TimeoutException:
        logger.error("GroqCloud API request timed out")
        fallback_personas = [
            Persona(
                id=str(uuid.uuid4()), 
                name=persona["name"], 
                description=persona["description"],
                painPoints=persona["painPoints"],
                motivators=persona["motivators"],
                demographics=Demographics(**persona.get("demographics", {})),
                productId=body.productId
            )
            for persona in FALLBACK_PERSONAS
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return PersonasResponse(
            success=True,
            personas=fallback_personas,
            source="fallback",
            processingTime=processing_time,
            reason="API timeout"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in persona generation: {e}")
        fallback_personas = [
            Persona(
                id=str(uuid.uuid4()), 
                name=persona["name"], 
                description=persona["description"],
                painPoints=persona["painPoints"],
                motivators=persona["motivators"],
                demographics=Demographics(**persona.get("demographics", {})),
                productId=body.productId
            )
            for persona in FALLBACK_PERSONAS
        ]
        processing_time = int((time.time() - start_time) * 1000)
        return PersonasResponse(
            success=True,
            personas=fallback_personas,
            source="fallback",
            processingTime=processing_time,
            reason=f"Error: {str(e)}"
        )

@router.post("/store", response_model=PersonaStoreResponse)
async def store_personas(body: PersonaStoreRequest):
    """
    Store generated personas in the database linked to an audit
    """
    try:
        supabase = get_supabase_client()
        stored_count = 0
        errors = []
        
        # First, let's validate that the audit_id exists
        audit_check = supabase.table("audit").select("audit_id").eq("audit_id", body.auditId).execute()
        if not audit_check.data:
            logger.error(f"❌ Audit ID {body.auditId} does not exist in database")
            return PersonaStoreResponse(
                success=False,
                storedCount=0,
                message=f"Audit ID {body.auditId} not found",
                errors=[f"Audit ID {body.auditId} not found"]
            )
        
        # Check what product_ids are being used
        product_ids = set()
        for persona in body.personas:
            if persona.productId:
                product_ids.add(persona.productId)
        
        logger.info(f"🔍 Checking product IDs: {list(product_ids)}")
        
        # Validate all product_ids exist
        if product_ids:
            existing_products = supabase.table("product").select("product_id").in_("product_id", list(product_ids)).execute()
            existing_product_ids = {p["product_id"] for p in existing_products.data}
            logger.info(f"✅ Found existing products: {list(existing_product_ids)}")
            
            missing_product_ids = product_ids - existing_product_ids
            if missing_product_ids:
                logger.error(f"❌ Missing product IDs: {list(missing_product_ids)}")
                return PersonaStoreResponse(
                    success=False,
                    storedCount=0,
                    message=f"Product IDs not found: {list(missing_product_ids)}",
                    errors=[f"Product IDs not found: {list(missing_product_ids)}"]
                )
        
        for persona in body.personas:
            try:
                # Log detailed persona information
                logger.info(f"🔄 Attempting to store persona: {persona.name}")
                logger.info(f"   - persona_id: {persona.id}")
                logger.info(f"   - audit_id: {body.auditId}")
                logger.info(f"   - brand_id: {body.brandId}")
                logger.info(f"   - product_id: {persona.productId}")
                
                # Insert persona into database with correct schema
                # Combine all additional info into persona_characteristics
                characteristics_data = {
                    "pain_points": persona.painPoints,
                    "motivators": persona.motivators,
                    "demographics": persona.demographics.__dict__ if persona.demographics else {}
                }
                characteristics_text = json.dumps(characteristics_data, indent=2)
                
                # Log the data being inserted
                insert_data = {
                    "persona_id": persona.id,
                    "audit_id": body.auditId,
                    "brand_id": body.brandId,
                    "product_id": persona.productId,
                    "persona_type": persona.name,
                    "persona_description": persona.description,
                    "persona_characteristics": characteristics_text
                }
                logger.info(f"📝 Inserting data: {insert_data}")
                
                result = supabase.table("personas").insert(insert_data).execute()
                
                if result.data:
                    stored_count += 1
                    logger.info(f"✅ Successfully stored persona: {persona.name} with ID: {persona.id}")
                    logger.info(f"   - Database returned: {result.data}")
                else:
                    error_msg = f"Failed to store persona: {persona.name} - No data returned"
                    errors.append(error_msg)
                    logger.warning(f"⚠️ {error_msg}")
                    
            except Exception as e:
                error_msg = f"Error storing persona {persona.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
                
                # Log additional error details if it's a database error
                if hasattr(e, 'details'):
                    logger.error(f"   - Error details: {e.details}")
                if hasattr(e, 'code'):
                    logger.error(f"   - Error code: {e.code}")
        
        if stored_count == 0:
            return PersonaStoreResponse(
                success=False,
                storedCount=0,
                message="Failed to store any personas",
                errors=errors
            )
        
        message = f"Successfully stored {stored_count} out of {len(body.personas)} personas"
        if errors:
            message += f" with {len(errors)} errors"
        
        logger.info(f"✅ {message}")
        
        return PersonaStoreResponse(
            success=True,
            storedCount=stored_count,
            message=message,
            errors=errors if errors else None
        )
        
    except Exception as e:
        logger.error(f"❌ Error storing personas: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/by-audit/{audit_id}", response_model=PersonasResponse)
async def get_personas_by_audit(audit_id: str = Path(..., description="Audit ID")):
    """
    Get all personas associated with a specific audit
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch personas from database
        result = supabase.table("personas").select("*").eq("audit_id", audit_id).execute()
        
        if not result.data:
            return PersonasResponse(
                success=True,
                personas=[],
                source="database",
                processingTime=0,
                reason="No personas found for this audit"
            )
        
        # Convert database records to Persona objects
        personas = []
        for record in result.data:
            try:
                # Parse characteristics JSON back to individual fields
                characteristics = {}
                if record.get("persona_characteristics"):
                    try:
                        characteristics = json.loads(record["persona_characteristics"])
                    except json.JSONDecodeError:
                        characteristics = {}
                
                persona = Persona(
                    id=record["persona_id"],
                    name=record["persona_type"], 
                    description=record["persona_description"],
                    painPoints=characteristics.get("pain_points", []),
                    motivators=characteristics.get("motivators", []),
                    demographics=Demographics(**characteristics.get("demographics", {})) if characteristics.get("demographics") else None,
                    productId=record.get("product_id")
                )
                personas.append(persona)
            except Exception as e:
                logger.warning(f"Error converting database record to Persona: {e}")
                continue
        
        logger.info(f"✅ Retrieved {len(personas)} personas for audit {audit_id}")
        
        return PersonasResponse(
            success=True,
            personas=personas,
            source="database",
            processingTime=0
        )
        
    except Exception as e:
        logger.error(f"❌ Error retrieving personas: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/fallback", response_model=PersonasResponse)
async def get_fallback_personas():
    """
    Get fallback personas directly (for testing or when AI is unavailable)
    """
    personas = [
        Persona(
            id=str(uuid.uuid4()), 
            name=persona["name"], 
            description=persona["description"],
            painPoints=persona["painPoints"],
            motivators=persona["motivators"],
            demographics=Demographics(**persona.get("demographics", {})),
            productId=None  # No productId available in fallback endpoint
        )
        for persona in FALLBACK_PERSONAS
    ]
    
    return PersonasResponse(
        success=True,
        personas=personas,
        source="fallback",
        processingTime=0
    ) 