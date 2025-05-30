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

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.database import get_supabase_client
from ..models.brands import (
    BrandInsertRequest, BrandInsertResponse,
    BrandLlamaRequest, BrandLlamaResponse, 
    BrandUpdateRequest, BrandUpdateResponse
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
    Generate brand description and products using AI
    """
    if not settings.has_groq_config:
        raise HTTPException(
            status_code=500,
            detail="Groq API key not configured"
        )

    # Strict system prompt for JSON-only output
    system_prompt = (
        "You are a helpful assistant. Given a brand name and domain, "
        "return a JSON object with two keys: "
        "\"description\" (a concise brand description, max 500 chars) and "
        "\"product\" (an array of up to 5 product names). "
        "No extra keys, no preamble, no postamble, just pure JSON. "
        "Use up-to-date knowledge as of May 2025. "
        "The description should summarize the company's offerings, services, or core focus clearly and professionally. "
        "The \"product\" list should highlight the most prominent product lines, services, or categories associated with the brand. "
        "If uncertain, make an informed generalization, but never fabricate specific product names. "
        "Output must always be valid JSON."
    )

    user_prompt = f"Brand: {request.brand_name}\nDomain: {request.domain}"

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            groq_resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if groq_resp.status_code != 200:
                raise HTTPException(
                    status_code=groq_resp.status_code, 
                    detail=groq_resp.text
                )
            
            result = groq_resp.json()
            
            # The model's response is in result['choices'][0]['message']['content']
            try:
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                if not isinstance(parsed, dict) or "description" not in parsed or "product" not in parsed:
                    raise ValueError("Invalid response structure")
                
                if not isinstance(parsed["product"], list):
                    raise ValueError("product must be a list")
                
                parsed["product"] = parsed["product"][:5]  # Limit to 5 products
                
                logger.info(f"✅ Successfully analyzed brand: {request.brand_name}")
                
                return BrandLlamaResponse(
                    description=parsed["description"],
                    product=parsed["product"]
                )
                
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to parse Groq response: {e}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI API request timed out")
    except Exception as e:
        logger.error(f"❌ Error analyzing brand: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")

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