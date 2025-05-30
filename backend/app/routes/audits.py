"""
AUDITS API ROUTES

PURPOSE: Audit creation and management

ENDPOINTS:
- POST /create - Create a new audit

ARCHITECTURE:
Frontend → FastAPI Backend → Supabase → Backend → Frontend
"""

import logging
from fastapi import APIRouter, HTTPException

from ..core.database import get_supabase_client
from ..models.audits import AuditCreateRequest, AuditCreateResponse

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create", response_model=AuditCreateResponse)
async def create_audit(audit: AuditCreateRequest):
    """
    Create a new audit
    """
    try:
        supabase = get_supabase_client()
        
        # Insert the audit
        result = supabase.table("audit").insert({
            "brand_id": audit.brand_id,
            "product_id": audit.product_id,
            "user_id": audit.user_id,
            "status": "in_progress"
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
        
        logger.info(f"✅ Successfully created audit for brand {audit.brand_id}, product {audit.product_id}, user {audit.user_id}")
        
        # Ensure response includes the product_id for frontend to update its state
        response_data = result.data[0] if result.data else {}
        if result.data and 'product_id' not in response_data:
            response_data['product_id'] = audit.product_id
        
        return AuditCreateResponse(
            success=True,
            data=response_data,
            message="Audit created successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error creating audit: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 