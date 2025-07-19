"""
Pydantic models for personas-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class Demographics(BaseModel):
    """Demographics model for personas"""
    ageRange: Optional[str] = Field(None, description="Age range of the persona")
    gender: Optional[str] = Field(None, description="Gender of the persona")
    location: Optional[str] = Field(None, description="Location of the persona")
    goals: Optional[List[str]] = Field(None, description="Goals of the persona")

class PersonaGenerateRequest(BaseModel):
    """Request model for generating personas via AI"""
    brandName: str = Field(..., min_length=1, max_length=100, description="Brand name")
    brandDescription: str = Field(..., min_length=1, max_length=1000, description="Brand description")
    brandDomain: str = Field(..., min_length=1, max_length=255, description="Brand domain/website")
    productName: str = Field(..., min_length=1, max_length=200, description="Product or service name")
    industry: Optional[str] = Field(None, max_length=100, description="Industry category")
    additionalContext: Optional[str] = Field(None, max_length=500, description="Additional context")
    auditId: Optional[str] = Field(None, description="Associated audit ID")
    brandId: str = Field(..., description="Brand ID from database")
    productId: str = Field(..., description="Product ID from database")
    topics: List[str] = Field(..., min_items=1, description="List of topics for context")
    
    @validator('brandName', 'brandDescription', 'brandDomain', 'productName', 'brandId', 'productId')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()
    
    @validator('topics')
    def validate_topics(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one topic is required')
        return v
    
    @validator('industry', 'additionalContext', 'auditId')
    def validate_optional_fields(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

class Persona(BaseModel):
    """Individual persona model"""
    id: str
    name: str
    description: str
    painPoints: List[str]
    motivators: List[str]
    demographics: Optional[Demographics] = None
    topicId: Optional[str] = None
    productId: Optional[str] = None

class PersonasResponse(BaseModel):
    """Response model for personas generation"""
    success: bool
    personas: List[Persona]
    source: str
    processingTime: int
    tokenUsage: Optional[int] = None
    reason: Optional[str] = None

class PersonaStoreRequest(BaseModel):
    """Request model for storing personas in database"""
    auditId: str = Field(..., description="Associated audit ID")
    brandId: Optional[str] = Field(None, description="Associated brand ID")
    personas: List[Persona] = Field(..., description="List of personas to store")
    
    @validator('auditId')
    def validate_audit_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Audit ID cannot be empty')
        return v.strip()
    
    @validator('brandId')
    def validate_brand_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Brand ID cannot be empty string')
        return v.strip() if v else None

class PersonaStoreResponse(BaseModel):
    """Response model for storing personas"""
    success: bool
    storedCount: int
    message: str
    errors: Optional[List[str]] = None 