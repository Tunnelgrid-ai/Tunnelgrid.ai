"""
Pydantic models for AI analysis operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalysisJobStatus(str, Enum):
    """Enum for analysis job status values"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_FAILURE = "partial_failure"

class LLMServiceType(str, Enum):
    """Enum for supported LLM services"""
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    GEMINI = "gemini"

class LLMServiceStatus(BaseModel):
    """Model for individual LLM service status tracking"""
    service: LLMServiceType
    status: AnalysisJobStatus
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0)
    completed_queries: int = Field(0, ge=0)
    total_queries: int = Field(0, ge=0)
    failed_queries: int = Field(0, ge=0)
    error_message: Optional[str] = None
    estimated_time_remaining: Optional[int] = Field(None, ge=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @validator('progress_percentage')
    def validate_progress(cls, v):
        if not (0.0 <= v <= 100.0):
            raise ValueError('Progress percentage must be between 0.0 and 100.0')
        return v

    @validator('completed_queries', 'failed_queries')
    def validate_query_counts(cls, v, values):
        total = values.get('total_queries', 0)
        if v > total:
            raise ValueError('Completed/failed queries cannot exceed total queries')
        return v

class AnalysisJobRequest(BaseModel):
    """Request model for starting AI analysis"""
    audit_id: str = Field(..., description="Audit ID to analyze")
    services: Optional[List[LLMServiceType]] = Field(
        default=[LLMServiceType.OPENAI], 
        description="List of LLM services to use for analysis"
    )
    
    @validator('audit_id')
    def validate_audit_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Audit ID cannot be empty')
        return v.strip()

    @validator('services')
    def validate_services(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one LLM service must be specified')
        return v

class AIAnalysisRequest(BaseModel):
    """Request model for individual AI analysis call"""
    query_id: str = Field(..., description="Query ID from database")
    persona_description: str = Field(..., description="Persona description for system prompt")
    question_text: str = Field(..., description="Question text for user prompt")
    model: str = Field(..., description="AI model identifier (e.g., 'openai-4o')")
    service: LLMServiceType = Field(..., description="LLM service to use")
    
    @validator('persona_description', 'question_text')
    def validate_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Text fields cannot be empty')
        return v.strip()

class Citation(BaseModel):
    """Model for citations extracted from AI responses"""
    text: str = Field(..., description="Citation text or reference")
    source_url: Optional[str] = Field(None, description="Source URL if available")
    service: LLMServiceType = Field(..., description="LLM service that provided this citation")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Citation text cannot be empty')
        return v.strip()

class BrandMention(BaseModel):
    """Model for brand mentions extracted from AI responses"""
    brand_name: str = Field(..., description="Extracted brand name")
    context: str = Field(..., description="Context around the brand mention")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    service: LLMServiceType = Field(..., description="LLM service that provided this mention")
    
    @validator('brand_name', 'context')
    def validate_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Brand mention fields cannot be empty')
        return v.strip()
    
    @validator('sentiment_score')
    def validate_sentiment(cls, v):
        if v is not None and not (-1.0 <= v <= 1.0):
            raise ValueError('Sentiment score must be between -1.0 and 1.0')
        return v

class AIAnalysisResponse(BaseModel):
    """Response model for individual AI analysis"""
    query_id: str
    model: str
    service: LLMServiceType
    response_text: str
    citations: List[Citation] = []
    brand_mentions: List[BrandMention] = []
    processing_time_ms: int
    token_usage: Optional[Dict[str, Any]] = None  # Changed to Any to handle complex structures
    
    @validator('response_text')
    def validate_response_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Response text cannot be empty')
        return v.strip()

class AnalysisJobStatusResponse(BaseModel):
    """Response model for analysis job status"""
    job_id: str
    audit_id: str
    status: AnalysisJobStatus
    total_queries: int
    completed_queries: int
    failed_queries: int
    progress_percentage: float
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated time in seconds")
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    # New field for multi-service tracking
    service_statuses: Optional[List[LLMServiceStatus]] = Field(default=[], description="Status of each LLM service")
    
    @validator('progress_percentage')
    def validate_progress(cls, v):
        if not (0.0 <= v <= 100.0):
            raise ValueError('Progress percentage must be between 0.0 and 100.0')
        return v

class AnalysisJobResponse(BaseModel):
    """Response model for starting analysis job"""
    success: bool
    job_id: str
    message: str
    estimated_completion_time: Optional[datetime] = None
    total_queries: int = 0
    services: List[LLMServiceType] = Field(default=[], description="LLM services being used")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class AnalysisError(BaseModel):
    """Model for tracking analysis errors"""
    query_id: str
    service: LLMServiceType
    error_type: str
    error_message: str
    timestamp: datetime
    retry_count: int = 0

class AnalysisResults(BaseModel):
    """Response model for comprehensive analysis results"""
    job_status: Dict[str, Any] = Field(..., description="Analysis job status information")
    total_responses: int = Field(..., description="Total number of AI responses")
    total_citations: int = Field(..., description="Total number of citations extracted")
    total_brand_mentions: int = Field(..., description="Total number of brand mentions found")
    responses: List[Dict[str, Any]] = Field(default=[], description="List of AI responses with query details")
    citations: List[Dict[str, Any]] = Field(default=[], description="List of extracted citations")
    brand_mentions: List[Dict[str, Any]] = Field(default=[], description="List of brand mentions with sentiment")
    service_summary: Dict[LLMServiceType, Dict[str, Any]] = Field(default={}, description="Summary by service")
    
    @validator('total_responses', 'total_citations', 'total_brand_mentions')
    def validate_totals(cls, v):
        if v < 0:
            raise ValueError('Total counts cannot be negative')
        return v

class AnalysisMetrics(BaseModel):
    """Model for analysis performance metrics"""
    total_processing_time_ms: int
    average_response_time_ms: float
    total_tokens_used: int
    api_calls_made: int
    success_rate: float
    citations_extracted: int
    brand_mentions_extracted: int
    service_metrics: Dict[LLMServiceType, Dict[str, Any]] = Field(default={}, description="Metrics by service") 