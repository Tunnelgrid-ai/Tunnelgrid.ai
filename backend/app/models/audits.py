"""
Pydantic models for audit-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class AuditCreateRequest(BaseModel):
    """Request model for creating a new audit"""
    brand_id: str = Field(..., description="Brand ID")
    product_id: str = Field(..., description="Product ID")
    user_id: str = Field(..., description="User ID")
    product_name: Optional[str] = Field(None, description="Product name (for verification)")
    
    @validator('brand_id', 'product_id', 'user_id')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()
    
    @validator('product_name')
    def validate_product_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Product name cannot be empty string')
        return v.strip() if v else None

class AuditCreateResponse(BaseModel):
    """Response model for audit creation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class AuditResponse(BaseModel):
    """Standard audit response model"""
    audit_id: str
    brand_id: str
    product_id: str
    user_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: Optional[str] = None 