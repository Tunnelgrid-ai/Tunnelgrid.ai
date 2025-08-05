"""
STUDY MANAGEMENT API ROUTES

PURPOSE: Simplified study management using existing audit table

FEATURES:
- Create, read, update, delete studies (using audit table)
- Progress saving and restoration
- Study sharing and collaboration
- Search and filtering
- Statistics and analytics

ENDPOINTS:
- POST /studies - Create new study (audit)
- GET /studies - List user's studies (audits)
- GET /studies/{study_id} - Get study details
- PUT /studies/{study_id} - Update study metadata
- DELETE /studies/{study_id} - Delete study
- POST /studies/{study_id}/progress - Save progress
- GET /studies/{study_id}/progress - Get progress
- GET /studies/stats - Get study statistics
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ..core.database import get_supabase_client
from ..models.studies import (
    StudyCreateRequest, StudyUpdateRequest, StudyProgressRequest,
    StudyResponse, StudyListResponse, StudyProgressResponse,
    StudyStatsResponse, StudySearchRequest,
    StudyStep, StudyStatus
)

# Setup logging
logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def get_current_user() -> str:
    """
    Get current user ID from authentication
    This is a placeholder - implement based on your auth system
    """
    # TODO: Implement proper authentication
    # For now, return a valid UUID for development
    # This should be replaced with actual user authentication
    return "72f7b6f6-ce78-41dd-a691-44d1ff8f7a01"

# =============================================================================
# STUDY CRUD OPERATIONS (USING AUDIT TABLE)
# =============================================================================

@router.post("/", response_model=StudyResponse)
async def create_study(request: StudyCreateRequest, user_id: str = Depends(get_current_user)):
    """
    Create a new study using the audit table
    """
    try:
        logger.info(f"Creating new study for user {user_id}")
        
        supabase = get_supabase_client()
        
        # Create audit record (this is our study)
        audit_id = str(uuid.uuid4())
        audit_data = {
            "audit_id": audit_id,
            "user_id": user_id,
            "brand_id": request.brand_id,
            "product_id": request.product_id,
            "status": "draft",  # Start as draft
            "created_timestamp": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("audit").insert(audit_data).execute()
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(status_code=500, detail=f"Failed to create study: {result.error}")
        
        logger.info(f"✅ Study {audit_id} created successfully")
        
        # Return study response (mapped from audit)
        return StudyResponse(
            study_id=audit_id,
            user_id=user_id,
            brand_id=request.brand_id,
            product_id=request.product_id,
            study_name=request.study_name or "Brand Analysis Study",
            study_description=request.study_description,
            current_step=StudyStep.BRAND_INFO,
            progress_percentage=0,
            status=StudyStatus.DRAFT,
            is_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow(),
            completed_at=None,
            analysis_job_id=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating study: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create study: {str(e)}")

@router.get("/", response_model=StudyListResponse)
async def list_studies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    status: Optional[StudyStatus] = Query(None, description="Filter by status"),
    user_id: str = Depends(get_current_user)
):
    """
    List all studies (audits) for the authenticated user with pagination
    """
    try:
        logger.info(f"Listing studies for user {user_id}")
        
        supabase = get_supabase_client()
        
        # Build query for audit table (excluding deleted ones)
        query = supabase.table("audit").select("*").eq("user_id", user_id).neq("status", "deleted")
        
        # Apply status filter (map study status to audit status)
        if status:
            audit_status = status.value
            query = query.eq("status", audit_status)
        
        # Get total count
        count_result = query.execute()
        total_count = len(count_result.data)
        
        # Apply pagination
        offset = (page - 1) * page_size
        audits_result = query.range(offset, offset + page_size - 1).order("created_timestamp", desc=True).execute()
        
        if hasattr(audits_result, 'error') and audits_result.error:
            raise HTTPException(status_code=500, detail=f"Failed to fetch studies: {audits_result.error}")
        
        # Convert audits to studies
        studies = []
        for audit in audits_result.data:
            # Map audit status to study status
            study_status = StudyStatus.DRAFT
            if audit["status"] == "completed":
                study_status = StudyStatus.COMPLETED
            elif audit["status"] == "in_progress":
                study_status = StudyStatus.IN_PROGRESS
            elif audit["status"] == "failed":
                study_status = StudyStatus.FAILED
            
            study = StudyResponse(
                study_id=audit["audit_id"],
                user_id=audit["user_id"],
                brand_id=audit["brand_id"] or "",
                product_id=audit["product_id"],
                study_name=f"Brand Analysis {audit['audit_id'][:8]}",
                study_description=None,
                current_step=StudyStep.BRAND_INFO,  # Default
                progress_percentage=0,  # Default
                status=study_status,
                is_completed=audit["status"] == "completed",
                created_at=datetime.fromisoformat(audit["created_timestamp"]),
                updated_at=datetime.fromisoformat(audit["created_timestamp"]),
                last_accessed_at=datetime.fromisoformat(audit["created_timestamp"]),
                completed_at=datetime.fromisoformat(audit["created_timestamp"]) if audit["status"] == "completed" else None,
                analysis_job_id=None  # Not implemented yet
            )
            studies.append(study)
        
        logger.info(f"✅ Retrieved {len(studies)} studies")
        
        return StudyListResponse(
            studies=studies,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_more=offset + page_size < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listing studies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list studies: {str(e)}")

@router.get("/{study_id}", response_model=StudyResponse)
async def get_study(study_id: str, user_id: str = Depends(get_current_user)):
    """
    Get study details by ID (using audit table)
    """
    try:
        logger.info(f"Getting study {study_id}")
        
        supabase = get_supabase_client()
        
        # Get audit record
        result = supabase.table("audit").select("*").eq("audit_id", study_id).eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Study not found")
        
        audit = result.data[0]
        
        # Map audit status to study status
        study_status = StudyStatus.DRAFT
        if audit["status"] == "completed":
            study_status = StudyStatus.COMPLETED
        elif audit["status"] == "in_progress":
            study_status = StudyStatus.IN_PROGRESS
        elif audit["status"] == "failed":
            study_status = StudyStatus.FAILED
        
        return StudyResponse(
            study_id=audit["audit_id"],
            user_id=audit["user_id"],
            brand_id=audit["brand_id"] or "",
            product_id=audit["product_id"],
            study_name=f"Brand Analysis {audit['audit_id'][:8]}",
            study_description=None,
            current_step=StudyStep.BRAND_INFO,
            progress_percentage=0,
            status=study_status,
            is_completed=audit["status"] == "completed",
            created_at=datetime.fromisoformat(audit["created_timestamp"]),
            updated_at=datetime.fromisoformat(audit["created_timestamp"]),
            last_accessed_at=datetime.fromisoformat(audit["created_timestamp"]),
            completed_at=datetime.fromisoformat(audit["created_timestamp"]) if audit["status"] == "completed" else None,
            analysis_job_id=None  # Not implemented yet
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting study: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get study: {str(e)}")

@router.put("/{study_id}", response_model=StudyResponse)
async def update_study(
    study_id: str, 
    request: StudyUpdateRequest, 
    user_id: str = Depends(get_current_user)
):
    """
    Update study metadata (using audit table)
    """
    try:
        logger.info(f"Updating study {study_id}")
        
        supabase = get_supabase_client()
        
        # Update audit record
        update_data = {}
        if request.study_name:
            update_data["study_name"] = request.study_name
        if request.study_description:
            update_data["study_description"] = request.study_description
        
        if update_data:
            result = supabase.table("audit").update(update_data).eq("audit_id", study_id).eq("user_id", user_id).execute()
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(status_code=500, detail=f"Failed to update study: {result.error}")
        
        # Return updated study
        return await get_study(study_id, user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating study: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update study: {str(e)}")

@router.delete("/{study_id}")
async def delete_study(study_id: str, user_id: str = Depends(get_current_user)):
    """
    Delete study (soft delete from audit table)
    """
    try:
        logger.info(f"Deleting study {study_id}")
        
        supabase = get_supabase_client()
        
        # Soft delete by updating status
        result = supabase.table("audit").update({"status": "deleted"}).eq("audit_id", study_id).eq("user_id", user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(status_code=500, detail=f"Failed to delete study: {result.error}")
        
        logger.info(f"✅ Study {study_id} deleted successfully")
        
        return {"message": "Study deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting study: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete study: {str(e)}")

# =============================================================================
# PROGRESS MANAGEMENT (SIMPLIFIED)
# =============================================================================

@router.post("/{study_id}/progress", response_model=StudyProgressResponse)
async def save_progress(
    study_id: str,
    request: StudyProgressRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Save study progress (simplified - just update audit status)
    """
    try:
        logger.info(f"Saving progress for study {study_id}")
        
        supabase = get_supabase_client()
        
        # Update audit status based on progress
        status = "in_progress"
        if request.progress_percentage >= 100:
            status = "completed"
        elif request.progress_percentage > 0:
            status = "in_progress"
        else:
            status = "draft"
        
        result = supabase.table("audit").update({
            "status": status,
            "progress_data": request.step_data  # Store progress data in audit table
        }).eq("audit_id", study_id).eq("user_id", user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(status_code=500, detail=f"Failed to save progress: {result.error}")
        
        logger.info(f"✅ Progress saved for study {study_id}")
        
        return StudyProgressResponse(
            study_id=study_id,
            current_step=request.step_name,
            progress_percentage=request.progress_percentage,
            step_data=request.step_data,
            last_updated=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save progress: {str(e)}")

@router.get("/{study_id}/progress", response_model=StudyProgressResponse)
async def get_progress(study_id: str, user_id: str = Depends(get_current_user)):
    """
    Get study progress (simplified)
    """
    try:
        logger.info(f"Getting progress for study {study_id}")
        
        supabase = get_supabase_client()
        
        result = supabase.table("audit").select("status, progress_data").eq("audit_id", study_id).eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Study not found")
        
        audit = result.data[0]
        
        # Calculate progress based on status
        progress_percentage = 0
        current_step = StudyStep.BRAND_INFO
        
        if audit["status"] == "completed":
            progress_percentage = 100
            current_step = StudyStep.COMPLETED
        elif audit["status"] == "in_progress":
            progress_percentage = 50  # Default for in-progress
            current_step = StudyStep.REVIEW
        
        return StudyProgressResponse(
            study_id=study_id,
            current_step=current_step,
            progress_percentage=progress_percentage,
            step_data=audit.get("progress_data", {}),
            last_updated=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=StudyStatsResponse)
async def get_study_stats(user_id: str = Depends(get_current_user)):
    """
    Get study statistics (using audit table)
    """
    try:
        logger.info(f"Getting study stats for user {user_id}")
        
        supabase = get_supabase_client()
        
        # Get all audits for user (excluding deleted ones)
        result = supabase.table("audit").select("status, created_timestamp").eq("user_id", user_id).neq("status", "deleted").execute()
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(status_code=500, detail=f"Failed to get stats: {result.error}")
        
        audits = result.data
        
        # Calculate statistics
        total_studies = len(audits)
        completed_studies = len([a for a in audits if a["status"] == "completed"])
        in_progress_studies = len([a for a in audits if a["status"] == "in_progress"])
        draft_studies = len([a for a in audits if a["status"] == "draft"])
        
        # Get recent studies (last 5)
        recent_audits = sorted(audits, key=lambda x: x["created_timestamp"], reverse=True)[:5]
        recent_studies = []
        
        for audit in recent_audits:
            study_status = StudyStatus.DRAFT
            if audit["status"] == "completed":
                study_status = StudyStatus.COMPLETED
            elif audit["status"] == "in_progress":
                study_status = StudyStatus.IN_PROGRESS
            
            study = StudyResponse(
                study_id=audit["audit_id"],
                user_id=user_id,
                brand_id="",
                product_id=None,
                study_name=f"Brand Analysis {audit['audit_id'][:8]}",
                study_description=None,
                current_step=StudyStep.BRAND_INFO,
                progress_percentage=0,
                status=study_status,
                is_completed=audit["status"] == "completed",
                created_at=datetime.fromisoformat(audit["created_timestamp"]),
                updated_at=datetime.fromisoformat(audit["created_timestamp"]),
                last_accessed_at=datetime.fromisoformat(audit["created_timestamp"]),
                completed_at=datetime.fromisoformat(audit["created_timestamp"]) if audit["status"] == "completed" else None,
                analysis_job_id=None
            )
            recent_studies.append(study)
        
        return StudyStatsResponse(
            total_studies=total_studies,
            completed_studies=completed_studies,
            in_progress_studies=in_progress_studies,
            draft_studies=draft_studies,
            recent_studies=recent_studies
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") 