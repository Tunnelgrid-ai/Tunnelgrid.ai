"""
AUDITS API ROUTES

PURPOSE: Audit creation and management

ENDPOINTS:
- POST /create - Create a new audit
- PUT /{audit_id}/complete - Complete an audit

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

@router.put("/{audit_id}/complete")
async def complete_audit(audit_id: str):
    """
    Complete an audit by updating its status to 'completed'
    
    This endpoint uses the service role key to bypass RLS policies,
    ensuring the update works even when frontend client has permission issues.
    """
    try:
        supabase = get_supabase_client()
        
        logger.info(f"🔄 Completing audit: {audit_id}")
        
        # STEP 1: Check if audit exists
        check_result = supabase.table("audit").select("audit_id, status").eq("audit_id", audit_id).execute()
        
        if not check_result.data:
            logger.warning(f"❌ Audit not found: {audit_id}")
            raise HTTPException(status_code=404, detail="Audit not found")
        
        current_audit = check_result.data[0]
        logger.info(f"📋 Found audit {audit_id} with status: {current_audit['status']}")
        
        # STEP 2: Update audit status to completed
        update_result = supabase.table("audit").update({
            "status": "completed"
        }).eq("audit_id", audit_id).execute()
        
        # Check for errors in update operation
        if hasattr(update_result, 'error') and update_result.error:
            logger.error(f"❌ Update failed: {update_result.error}")
            raise HTTPException(status_code=500, detail=f"Update failed: {update_result.error}")
        
        logger.info(f"✅ Successfully completed audit: {audit_id}")
        
        return {
            "success": True,
            "data": {
                "audit_id": audit_id,
                "status": "completed"
            },
            "message": "Audit completed successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error completing audit {audit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 