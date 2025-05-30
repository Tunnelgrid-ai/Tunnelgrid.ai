"""
Pydantic models for questions-related operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class QuestionGenerateRequest(BaseModel):
    """Request model for generating questions via AI"""
    auditId: str = Field(..., description="Associated audit ID")
    brandName: str = Field(..., min_length=1, max_length=100, description="Brand name")
    brandDescription: Optional[str] = Field(None, max_length=500, description="Brand description")
    brandDomain: str = Field(..., min_length=1, max_length=255, description="Brand domain/website")
    productName: str = Field(..., min_length=1, max_length=200, description="Product or service name")
    topics: List[Dict[str, str]] = Field(..., min_items=1, description="List of topics with id, name, description")
    personas: List[Dict[str, Any]] = Field(..., min_items=1, description="List of personas with their characteristics")
    
    @validator('auditId', 'brandName', 'brandDomain', 'productName')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()
    
    @validator('brandDescription')
    def validate_optional_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('topics')
    def validate_topics(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one topic is required')
        return v
    
    @validator('personas')
    def validate_personas(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one persona is required')
        return v

class Question(BaseModel):
    """Individual question model"""
    id: str
    text: str
    personaId: str
    auditId: str
    topicName: Optional[str] = None
    queryType: Optional[str] = "brand_analysis"

class QuestionsResponse(BaseModel):
    """Response model for questions generation"""
    success: bool
    questions: List[Question]
    source: str
    processingTime: int
    tokenUsage: Optional[int] = None
    reason: Optional[str] = None

class QuestionsRetrieveResponse(BaseModel):
    """Response model for retrieving questions by audit ID"""
    success: bool
    questions: List[Question]
    message: str

class QuestionsStoreRequest(BaseModel):
    """Request model for storing questions in database"""
    auditId: str = Field(..., description="Associated audit ID")
    questions: List[Question] = Field(..., description="List of questions to store")
    
    @validator('auditId')
    def validate_audit_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Audit ID cannot be empty')
        return v.strip()

class QuestionsStoreResponse(BaseModel):
    """Response model for storing questions"""
    success: bool
    storedCount: int
    message: str
    errors: Optional[List[str]] = None 