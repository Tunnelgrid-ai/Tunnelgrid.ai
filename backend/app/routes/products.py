"""
PRODUCTS API ROUTES

PURPOSE: Product creation and management

ENDPOINTS:
- POST /create - Create a new product for a brand

ARCHITECTURE:
Frontend → FastAPI Backend → Supabase → Backend → Frontend
"""

import logging
from fastapi import APIRouter, HTTPException

from ..core.database import get_supabase_client
from ..models.products import ProductCreateRequest, ProductCreateResponse

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create", response_model=ProductCreateResponse)
async def create_product(product: ProductCreateRequest):
    """
    Create a new product for a brand
    """
    try:
        supabase = get_supabase_client()
        
        # Insert the product
        result = supabase.table("product").insert({
            "brand_id": product.brand_id,
            "product_name": product.product_name,
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
        
        logger.info(f"✅ Successfully created product: {product.product_name} for brand {product.brand_id}")
        
        return ProductCreateResponse(
            success=True,
            data=result.data[0] if result.data else None,
            message="Product created successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error creating product: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 