"""
Pydantic models for brand-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class BrandSearchResponse(BaseModel):
    """Response model for brand search from Logo.dev API"""
    # This will contain the raw response from Logo.dev
    # Structure depends on their API response format
    pass

class BrandInsertRequest(BaseModel):
    """Request model for inserting a new brand"""
    brand_name: str = Field(..., min_length=1, max_length=255, description="Brand name")
    domain: Optional[str] = Field(None, max_length=255, description="Brand domain/website")
    brand_description: Optional[str] = Field(None, max_length=1000, description="Brand description")
    
    @validator('brand_name')
    def validate_brand_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Brand name cannot be empty or whitespace only')
        return v.strip()
    
    @validator('domain')
    def validate_domain(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
            # Basic domain validation could be added here
            return v
        return v

class BrandInsertResponse(BaseModel):
    """Response model for brand insertion"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class BrandLlamaRequest(BaseModel):
    """Request model for brand analysis via Llama"""
    brand_name: str = Field(..., min_length=1, max_length=255, description="Brand name")
    domain: str = Field(..., min_length=1, max_length=255, description="Brand domain")
    
    @validator('brand_name', 'domain')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

class BrandLlamaResponse(BaseModel):
    """Response model for brand analysis via Llama"""
    description: str = Field(..., description="Brand description")
    product: List[str] = Field(..., description="List of brand products")

class BrandUpdateRequest(BaseModel):
    """Request model for updating brand with AI-generated data"""
    brand_name: str = Field(..., min_length=1, max_length=255, description="Brand name")
    brand_description: str = Field(..., min_length=1, max_length=1000, description="Brand description")
    product: List[str] = Field(..., description="List of brand products")
    
    @validator('brand_name', 'brand_description')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()
    
    @validator('product')
    def validate_product_list(cls, v):
        if not isinstance(v, list):
            raise ValueError('Product must be a list')
        # Filter out empty strings and strip whitespace
        cleaned = [item.strip() for item in v if item and item.strip()]
        return cleaned[:5]  # Limit to 5 products

class BrandUpdateResponse(BaseModel):
    """Response model for brand update"""
    success: bool
    message: str
    brand_id: Optional[str] = None
    products_created: Optional[int] = None

class BrandDescriptionUpdateRequest(BaseModel):
    """Request model for updating just brand description"""
    description: str = Field(..., min_length=1, max_length=1000, description="Updated brand description")
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()

class BrandDescriptionUpdateResponse(BaseModel):
    """Response model for brand description update"""
    success: bool
    message: str
    brand_id: Optional[str] = None 