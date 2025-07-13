"""
Web Search API Routes using OpenAI Responses API
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging

from ..core.config import settings
from ..services.websearch_service import websearch_service
from ..models.common import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="The search query")
    context_size: Optional[str] = Field("medium", description="Search context size: low, medium, high")
    force_search: Optional[bool] = Field(False, description="Force use of web search tool")
    user_location: Optional[Dict[str, Any]] = Field(None, description="User location context")

class WebSearchResponse(BaseModel):
    success: bool
    output_text: Optional[str]
    citations: List[Dict[str, Any]]
    search_calls: List[Dict[str, str]]
    error: Optional[str] = None

@router.post("/search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """
    Perform web search using OpenAI Responses API
    """
    if not settings.has_openai_websearch_config:
        raise HTTPException(
            status_code=503,
            detail="OpenAI web search is not properly configured"
        )
    
    try:
        result = await websearch_service.search_web(
            query=request.query,
            context_size=request.context_size,
            user_location=request.user_location,
            force_search=request.force_search
        )
        
        return WebSearchResponse(**result)
        
    except Exception as e:
        logger.error(f"Web search endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check for web search service"""
    return {
        "status": "healthy",
        "services": {
            "openai_websearch": "available" if settings.has_openai_websearch_config else "unavailable",
            "responses_api": "available" if settings.OPENAI_API_KEY else "unavailable"
        },
        "config": {
            "model": settings.OPENAI_RESPONSES_MODEL,
            "tool_version": settings.OPENAI_WEB_SEARCH_TOOL_VERSION,
            "context_size": settings.OPENAI_SEARCH_CONTEXT_SIZE
        }
    } 