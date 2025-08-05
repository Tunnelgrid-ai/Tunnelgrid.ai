"""
Pydantic models for study management and progress tracking
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class StudyStep(str, Enum):
    """Enum for study progress steps"""
    BRAND_INFO = "brand_info"
    PERSONAS = "personas"
    PRODUCTS = "products"
    QUESTIONS = "questions"
    TOPICS = "topics"
    REVIEW = "review"
    ANALYSIS = "analysis"
    COMPLETED = "completed"

class StudyStatus(str, Enum):
    """Enum for study status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SETUP_COMPLETED = "setup_completed"
    ANALYSIS_RUNNING = "analysis_running"
    COMPLETED = "completed"
    FAILED = "failed"

class PermissionLevel(str, Enum):
    """Enum for study sharing permissions"""
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"

# =============================================================================
# STUDY MODELS
# =============================================================================

class StudyCreateRequest(BaseModel):
    """Request model for creating a new study"""
    brand_id: str = Field(..., description="Brand ID")
    product_id: Optional[str] = Field(None, description="Product ID (optional)")
    study_name: Optional[str] = Field(None, max_length=255, description="Custom study name")
    study_description: Optional[str] = Field(None, description="Study description")
    template_id: Optional[str] = Field(None, description="Template ID to start from")
    
    @validator('brand_id')
    def validate_brand_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Brand ID cannot be empty')
        return v.strip()
    
    @validator('study_name')
    def validate_study_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Study name cannot be empty string')
        return v.strip() if v else None

class StudyUpdateRequest(BaseModel):
    """Request model for updating study metadata"""
    study_name: Optional[str] = Field(None, max_length=255)
    study_description: Optional[str] = Field(None)
    
    @validator('study_name')
    def validate_study_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Study name cannot be empty string')
        return v.strip() if v else None

class StudyProgressRequest(BaseModel):
    """Request model for saving study progress"""
    step_name: StudyStep = Field(..., description="Current step")
    step_data: Dict[str, Any] = Field(..., description="Complete step data")
    progress_percentage: int = Field(..., ge=0, le=100, description="Progress percentage")
    
    @validator('step_data')
    def validate_step_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Step data must be a dictionary')
        return v

class StudyResponse(BaseModel):
    """Response model for study data"""
    study_id: str
    user_id: str
    brand_id: str
    product_id: Optional[str]
    study_name: str
    study_description: Optional[str]
    current_step: StudyStep
    progress_percentage: int
    status: StudyStatus
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    completed_at: Optional[datetime]
    analysis_job_id: Optional[str]
    
    class Config:
        from_attributes = True

class StudyListResponse(BaseModel):
    """Response model for study list"""
    studies: List[StudyResponse]
    total_count: int
    page: int
    page_size: int
    has_more: bool

class StudyProgressResponse(BaseModel):
    """Response model for study progress data"""
    study_id: str
    current_step: StudyStep
    progress_percentage: int
    step_data: Dict[str, Any]
    last_updated: datetime

# =============================================================================
# PROGRESS SNAPSHOT MODELS
# =============================================================================

class ProgressSnapshotResponse(BaseModel):
    """Response model for progress snapshot"""
    snapshot_id: str
    study_id: str
    step_name: StudyStep
    step_data: Dict[str, Any]
    created_at: datetime
    is_current: bool
    
    class Config:
        from_attributes = True

# =============================================================================
# SHARING MODELS
# =============================================================================

class StudyShareRequest(BaseModel):
    """Request model for sharing a study"""
    shared_with_email: str = Field(..., description="Email of person to share with")
    permission_level: PermissionLevel = Field(default=PermissionLevel.VIEW)
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    
    @validator('shared_with_email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Valid email address required')
        return v.strip().lower()

class StudyShareResponse(BaseModel):
    """Response model for study share"""
    share_id: str
    study_id: str
    shared_by: str
    shared_with_email: str
    permission_level: PermissionLevel
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

# =============================================================================
# TEMPLATE MODELS
# =============================================================================

class StudyTemplateRequest(BaseModel):
    """Request model for creating study template"""
    template_name: str = Field(..., max_length=255)
    template_description: Optional[str] = Field(None)
    template_data: Dict[str, Any] = Field(..., description="Template data")
    is_public: bool = Field(default=False)
    
    @validator('template_name')
    def validate_template_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip()

class StudyTemplateResponse(BaseModel):
    """Response model for study template"""
    template_id: str
    template_name: str
    template_description: Optional[str]
    template_data: Dict[str, Any]
    created_by: Optional[str]
    is_public: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# =============================================================================
# UTILITY MODELS
# =============================================================================

class StudyStatsResponse(BaseModel):
    """Response model for study statistics"""
    total_studies: int
    completed_studies: int
    in_progress_studies: int
    draft_studies: int
    recent_studies: List[StudyResponse]

class StudySearchRequest(BaseModel):
    """Request model for searching studies"""
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[StudyStatus] = Field(None, description="Filter by status")
    brand_id: Optional[str] = Field(None, description="Filter by brand")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Page size") 