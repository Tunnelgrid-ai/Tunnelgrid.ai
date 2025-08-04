"""
BRANDS API ROUTES

PURPOSE: Brand search, creation, and AI-powered analysis

ENDPOINTS:
- GET /search - Search for brands using Logo.dev API
- POST /create - Insert a new brand into the database
- POST /analyze - Generate brand description and products using AI
- POST /update - Update brand with AI-generated data

ARCHITECTURE:
Frontend → FastAPI Backend → (Logo.dev API / GroqCloud / Supabase) → Backend → Frontend
"""

import json
import httpx
import logging
import os
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request, Path
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.database import get_supabase_client
from ..models.brands import (
    BrandInsertRequest, BrandInsertResponse,
    BrandLlamaRequest, BrandLlamaResponse, 
    BrandUpdateRequest, BrandUpdateResponse,
    BrandDescriptionUpdateRequest, BrandDescriptionUpdateResponse
)

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search")
async def search_brands(q: str = Query(..., min_length=1, description="Search query")):
    """
    Search for brands using Logo.dev API
    """
    if not settings.has_logodev_config:
        raise HTTPException(
            status_code=500, 
            detail="Logo.dev API key not configured. Please check environment variables."
        )
    
    url = f"https://api.logo.dev/search?q={q}"
    # Try getting the API key directly from environment as fallback
    api_key = settings.LOGODEV_SECRET_KEY or os.getenv("LOGODEV_SECRET_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Debug logging to diagnose API key issue
    logger.info(f"🔧 DEBUG: API key from settings: {settings.LOGODEV_SECRET_KEY}")
    logger.info(f"🔧 DEBUG: API key from direct env: {os.getenv('LOGODEV_SECRET_KEY')}")
    logger.info(f"🔧 DEBUG: Using API key: {api_key}")
    
    try:
        # Enhanced connection configuration
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=True
        ) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                # Logo.dev API success - process the real response
                logo_data = response.json()
                
                # Convert Logo.dev format to frontend format
                # Logo.dev returns either an array or object with results
                if isinstance(logo_data, list):
                    brands = logo_data
                elif isinstance(logo_data, dict) and 'results' in logo_data:
                    brands = logo_data['results']
                elif isinstance(logo_data, dict) and 'data' in logo_data:
                    brands = logo_data['data']
                else:
                    # Fallback for unexpected format
                    brands = [logo_data] if isinstance(logo_data, dict) else []
                
                # Ensure each brand has the required fields for frontend
                formatted_brands = []
                for brand in brands:
                    domain = brand.get("domain", "unknown.com")
                    formatted_brand = {
                        "name": brand.get("name", "Unknown"),
                        "domain": domain,
                        # Use a reliable logo service that doesn't require authentication
                        # Logo.dev image API with secret key doesn't work, so use alternative
                        "logo": f"https://logo.clearbit.com/{domain}" if domain and domain != "unknown.com" else None
                    }
                    formatted_brands.append(formatted_brand)
                
                return JSONResponse(content=formatted_brands)
            
            elif response.status_code == 401:
                logger.error(f"❌ Logo.dev API authentication failed. Check API key validity.")
                raise HTTPException(
                    status_code=401,
                    detail="Logo.dev API authentication failed. Invalid or expired API key."
                )
            else:
                # Other API errors
                logger.error(f"❌ Logo.dev API returned status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Logo.dev API error: {response.text}"
                )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Logo.dev API HTTP error: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Logo.dev API HTTP error: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"❌ Logo.dev API request failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Logo.dev API request failed: {str(e)}"
        )

@router.post("/create", response_model=BrandInsertResponse)
async def create_brand(brand: BrandInsertRequest):
    """
    Insert a new brand into the database
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("brand").insert({
            "brand_name": brand.brand_name,
            "domain": brand.domain,
            "brand_description": brand.brand_description,
        }).execute()
        
        # Check for error in the raw JSON response
        raw = result.json()
        if "error" in raw and raw["error"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Insert failed: {raw['error']['message']}"
            )
        
        if not result.data:
            raise HTTPException(
                status_code=400, 
                detail="Insert failed: No data returned"
            )
        
        logger.info(f"✅ Successfully created brand: {brand.brand_name}")
        
        return BrandInsertResponse(
            success=True,
            data=result.data[0] if result.data else None,
            message="Brand created successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating brand: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/analyze", response_model=BrandLlamaResponse)
async def analyze_brand(request: BrandLlamaRequest):
    """
    Generate brand description and products using OpenAI GPT-4o with web search
    """
    if not settings.OPENAI_API_KEY:
        logger.error("❌ OpenAI API key not configured")
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please check environment variables."
        )

    # Enhanced system prompt optimized for web search and JSON output
    system_prompt = (
        "You are a brand analysis expert with access to real-time web search. "
        "Your task is to research and analyze brands using the most current information available online. "
        
        "IMPORTANT: Return ONLY a valid JSON object with these exact keys:\n"
        "{\n"
        "  \"description\": \"A comprehensive brand description (300-500 characters) based on current web information\",\n"
        "  \"product\": [\"Product 1\", \"Product 2\", \"Product 3\", \"Product 4\", \"Product 5\"]\n"
        "}\n"
        
        "Research Guidelines:\n"
        "- Use web search to find the most current information about the brand\n"
        "- Description should cover: what the company does, key offerings, market position, recent developments\n"
        "- Products should be their main/flagship products, services, or product categories\n"
        "- Focus on current, active products (not discontinued ones)\n"
        "- If it's a service company, list service categories as 'products'\n"
        "- Ensure all information is factual and up-to-date\n"
        
        "Output must be valid JSON only - no explanations, no markdown, no additional text."
    )

    user_prompt = (
        f"Research and analyze this brand using current web information:\n\n"
        f"Brand Name: {request.brand_name}\n"
        f"Domain: {request.domain}\n\n"
        f"Provide a JSON response with current brand description and main products/services."
    )

    payload = {
        "model": "gpt-4o-search-preview",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 800,
        "web_search_options": {}  # Simplified - just enable web search
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        logger.info(f"🔍 Starting OpenAI web search analysis for brand: {request.brand_name}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout for web search
            openai_resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers
            )

        logger.info(f"📡 OpenAI API response status: {openai_resp.status_code}")

        if openai_resp.status_code != 200:
            error_text = openai_resp.text
            logger.error(f"❌ OpenAI API error {openai_resp.status_code}: {error_text}")
            raise HTTPException(
                status_code=openai_resp.status_code,
                detail=f"OpenAI API error: {error_text}"
            )

        result = openai_resp.json()
        logger.info(f"📊 OpenAI API response received successfully")
        
        # Extract the response content
        choices = result.get("choices", [])
        if not choices:
            logger.error("❌ No choices in OpenAI response")
            raise HTTPException(status_code=500, detail="Empty response from OpenAI API")

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            logger.error("❌ No content in OpenAI response")
            raise HTTPException(status_code=500, detail="No content in OpenAI response")

        logger.info(f"📝 Raw OpenAI content: {content[:200]}...")

        # Clean and parse JSON response
        try:
            # Remove any markdown formatting if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            parsed = json.loads(content)
            logger.info(f"✅ Successfully parsed JSON response")

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            logger.error(f"❌ Content that failed to parse: {content}")
            
            # Attempt to extract JSON from response if it's embedded in text
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    logger.info(f"✅ Successfully extracted and parsed JSON from text")
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to parse JSON response from OpenAI: {str(e)}"
                    )
            except Exception as fallback_error:
                logger.error(f"❌ Fallback JSON extraction failed: {fallback_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"OpenAI returned invalid JSON: {str(e)}"
                )

        # Validate response structure
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=500, detail="Response is not a JSON object")

        if "description" not in parsed:
            logger.error(f"❌ Missing 'description' key in response: {parsed}")
            raise HTTPException(status_code=500, detail="Missing 'description' in response")

        if "product" not in parsed:
            logger.error(f"❌ Missing 'product' key in response: {parsed}")
            raise HTTPException(status_code=500, detail="Missing 'product' in response")

        if not isinstance(parsed["product"], list):
            logger.error(f"❌ 'product' is not a list: {parsed['product']}")
            raise HTTPException(status_code=500, detail="'product' must be an array")

        # Clean and validate the data
        description = str(parsed["description"]).strip()
        products = [str(p).strip() for p in parsed["product"] if str(p).strip()]
        
        # Limit products to 5 and ensure we have at least some data
        products = products[:5]
        
        if not description:
            description = f"AI-powered analysis for {request.brand_name}"
        
        if not products:
            products = ["Primary Products/Services"]

        logger.info(f"✅ Successfully analyzed brand: {request.brand_name}")
        logger.info(f"📋 Description length: {len(description)} chars")
        logger.info(f"🛍️ Products count: {len(products)}")

        return BrandLlamaResponse(
            description=description,
            product=products
        )

    except httpx.TimeoutException:
        logger.error(f"❌ OpenAI API request timed out for brand: {request.brand_name}")
        raise HTTPException(status_code=504, detail="AI analysis request timed out")
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected error analyzing brand {request.brand_name}: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"AI analysis error: {str(e)}"
        )

@router.post("/update", response_model=BrandUpdateResponse)
async def update_brand_with_products(request: BrandUpdateRequest):
    """
    Update brand with AI-generated description and create associated products
    """
    try:
        supabase = get_supabase_client()
        
        # 1. Find the brand row
        brand_resp = supabase.table("brand").select("brand_id").eq("brand_name", request.brand_name).limit(1).execute()
        
        if not brand_resp.data:
            raise HTTPException(status_code=404, detail=f"Brand '{request.brand_name}' not found")
        
        brand_id = brand_resp.data[0]["brand_id"]
        
        # 2. Update the brand description
        update_resp = supabase.table("brand").update({
            "brand_description": request.brand_description
        }).eq("brand_id", brand_id).execute()
        
        if not update_resp.data:
            raise HTTPException(status_code=400, detail="Failed to update brand description")
        
        # 3. Create products
        products_created = 0
        for product_name in request.product:
            if product_name.strip():  # Skip empty product names
                try:
                    product_resp = supabase.table("product").insert({
                        "brand_id": brand_id,
                        "product_name": product_name.strip()
                    }).execute()
                    
                    if product_resp.data:
                        products_created += 1
                        logger.info(f"✅ Created product: {product_name} for brand {request.brand_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create product '{product_name}': {e}")
                    # Continue with other products
        
        logger.info(f"✅ Successfully updated brand {request.brand_name} with {products_created} products")
        
        return BrandUpdateResponse(
            success=True,
            message=f"Brand updated successfully with {products_created} products",
            brand_id=brand_id,
            products_created=products_created
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error updating brand: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 

@router.put("/{brand_id}/description", response_model=BrandDescriptionUpdateResponse)
async def update_brand_description(
    brand_id: str = Path(..., description="Brand ID"),
    body: BrandDescriptionUpdateRequest = ...
):
    """
    Update brand description for a specific brand
    """
    try:
        supabase = get_supabase_client()
        
        # Update the brand description
        result = supabase.table("brand").update({
            "brand_description": body.description
        }).eq("brand_id", brand_id).execute()
        
        # Check for errors
        if hasattr(result, 'error') and result.error:
            raise HTTPException(
                status_code=400,
                detail=f"Database update failed: {result.error}"
            )
        
        if not result.data or len(result.data) == 0:
            return BrandDescriptionUpdateResponse(
                success=False,
                message="Brand not found or not updated"
            )
        
        logger.info(f"✅ Updated brand description for brand {brand_id}")
        
        return BrandDescriptionUpdateResponse(
            success=True,
            message="Brand description updated successfully",
            brand_id=brand_id
        )
        
    except Exception as e:
        logger.error(f"❌ Error updating brand description: {e}")
        return BrandDescriptionUpdateResponse(
            success=False,
            message=f"Failed to update brand description: {str(e)}"
        )

@router.get("/config/validate")
async def validate_openai_config():
    """
    Validate OpenAI configuration and test web search functionality
    """
    try:
        # Check basic configuration
        if not settings.OPENAI_API_KEY:
            return JSONResponse(
                status_code=500,
                content={
                    "valid": False,
                    "error": "OpenAI API key not configured",
                    "details": "OPENAI_API_KEY environment variable is missing"
                }
            )

        # Test basic API connectivity
        test_payload = {
            "model": "gpt-4o-search-preview",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Return only the JSON: {\"status\": \"ok\", \"timestamp\": \"current_time\"}"},
                {"role": "user", "content": "Return the status JSON with current timestamp"}
            ],
            "max_tokens": 100,
            "web_search_options": {}
        }

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=test_payload,
                headers=headers
            )

        if response.status_code == 200:
            result = response.json()
            return JSONResponse(content={
                "valid": True,
                "model": "gpt-4o-search-preview",
                "web_search_enabled": True,
                "api_response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None,
                "test_result": result.get("choices", [{}])[0].get("message", {}).get("content", "No content")
            })
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "valid": False,
                    "error": f"OpenAI API test failed: {response.status_code}",
                    "details": response.text
                }
            )

    except Exception as e:
        logger.error(f"❌ OpenAI configuration validation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "valid": False,
                "error": "Configuration validation failed",
                "details": str(e)
            }
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        return JSONResponse(content={
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # You might want to use actual timestamp
            "services": {
                "openai": settings.has_openai_config,
                "supabase": settings.has_supabase_config,
                "logodev": settings.has_logodev_config
            },
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        ) 