"""
Common Pydantic models used across the application
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    services: Dict[str, str]
    timestamp: str
    environment: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: Optional[str] = None

class SuccessResponse(BaseModel):
    """Standard success response model"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None 