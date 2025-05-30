"""
Pydantic models for product-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class ProductCreateRequest(BaseModel):
    """Request model for creating a new product"""
    brand_id: str = Field(..., description="Brand ID")
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    
    @validator('brand_id', 'product_name')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

class ProductCreateResponse(BaseModel):
    """Response model for product creation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class ProductResponse(BaseModel):
    """Standard product response model"""
    product_id: str
    brand_id: str
    product_name: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None 