"""
OpenAI Responses API Routes

This module provides FastAPI endpoints for using OpenAI's Responses API
with web search capabilities for real-time information and citations.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from ..services.openai_basic_api import OpenAIResponsesAPI
from ..core.config import Settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/openai-responses", tags=["OpenAI Responses"])

# Pydantic models for request/response
class WebSearchRequest(BaseModel):
    """Request model for web search with OpenAI Responses API."""
    system_prompt: str = Field(..., description="System instructions for the assistant")
    user_prompt: str = Field(..., description="User's question or prompt")
    assistant_name: str = Field(default="AI Assistant", description="Name for the assistant")
    model: Optional[str] = Field(default=None, description="Model to use (defaults to config)")
    max_retries: int = Field(default=3, description="Maximum retries for polling")
    polling_interval: float = Field(default=1.0, description="Polling interval in seconds")

class Citation(BaseModel):
    """Citation model for web search results."""
    type: str
    file_id: str
    quote: str
    start_index: int
    end_index: int

class WebSearchResponse(BaseModel):
    """Response model for web search with OpenAI Responses API."""
    success: bool
    response: Optional[str] = None
    citations: List[Citation] = []
    thread_id: Optional[str] = None
    assistant_id: Optional[str] = None
    run_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str

class BrandAnalysisRequest(BaseModel):
    """Request model for brand analysis with web search."""
    brand_name: str = Field(..., description="Name of the brand to analyze")
    analysis_type: str = Field(default="general", description="Type of analysis (general, market, competition, etc.)")
    additional_context: Optional[str] = Field(default=None, description="Additional context for analysis")

class BrandAnalysisResponse(BaseModel):
    """Response model for brand analysis."""
    success: bool
    analysis: Optional[str] = None
    citations: List[Citation] = []
    brand_name: str
    analysis_type: str
    error: Optional[str] = None
    timestamp: str


def get_openai_client() -> OpenAIResponsesAPI:
    """Dependency to get OpenAI client."""
    try:
        return OpenAIResponsesAPI()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI configuration error: {str(e)}")


@router.post("/web-search", response_model=WebSearchResponse)
async def get_web_search_response(
    request: WebSearchRequest,
    client: OpenAIResponsesAPI = Depends(get_openai_client)
):
    """
    Get a response from OpenAI with web search capabilities.
    
    This endpoint uses OpenAI's Responses API to get real-time information
    from the web with proper citations.
    """
    try:
        logger.info(f"Processing web search request: {request.user_prompt[:100]}...")
        
        result = await client.get_response_with_web_search(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            assistant_name=request.assistant_name,
            model=request.model,
            max_retries=request.max_retries,
            polling_interval=request.polling_interval
        )
        
        # Convert citations to Pydantic models
        citations = []
        for citation in result.get("citations", []):
            citations.append(Citation(**citation))
        
        return WebSearchResponse(
            success=result["success"],
            response=result.get("response"),
            citations=citations,
            thread_id=result.get("thread_id"),
            assistant_id=result.get("assistant_id"),
            run_id=result.get("run_id"),
            error=result.get("error"),
            timestamp=result.get("timestamp")
        )
        
    except Exception as e:
        logger.error(f"Error in web search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")


@router.post("/brand-analysis", response_model=BrandAnalysisResponse)
async def analyze_brand_with_web_search(
    request: BrandAnalysisRequest,
    client: OpenAIResponsesAPI = Depends(get_openai_client)
):
    """
    Analyze a brand using web search for current information.
    
    This endpoint provides comprehensive brand analysis using real-time
    web data with proper citations.
    """
    try:
        logger.info(f"Processing brand analysis request for: {request.brand_name}")
        
        # Create system prompt based on analysis type
        system_prompts = {
            "general": f"""You are an expert brand analyst with access to real-time web search. 
            Analyze {request.brand_name} comprehensively using current information from the web. 
            Provide detailed insights about their market position, recent developments, challenges, 
            and opportunities. Always cite your sources properly.""",
            
            "market": f"""You are a market research expert with access to real-time web search. 
            Analyze {request.brand_name}'s market position, market share, competitive landscape, 
            and market trends. Use current data and provide proper citations.""",
            
            "competition": f"""You are a competitive intelligence expert with access to real-time web search. 
            Analyze {request.brand_name}'s competitive position, main competitors, competitive advantages, 
            and competitive threats. Use current information and cite sources properly.""",
            
            "financial": f"""You are a financial analyst with access to real-time web search. 
            Analyze {request.brand_name}'s financial performance, recent financial news, 
            stock performance, and financial outlook. Use current data and provide citations."""
        }
        
        system_prompt = system_prompts.get(
            request.analysis_type, 
            system_prompts["general"]
        )
        
        # Add additional context if provided
        if request.additional_context:
            system_prompt += f"\n\nAdditional context: {request.additional_context}"
        
        # Create user prompt
        user_prompt = f"Provide a comprehensive {request.analysis_type} analysis of {request.brand_name} using current information from 2024."
        
        result = await client.get_response_with_web_search(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            assistant_name=f"Brand Analysis Expert - {request.brand_name}",
            max_retries=5,
            polling_interval=2.0
        )
        
        # Convert citations to Pydantic models
        citations = []
        for citation in result.get("citations", []):
            citations.append(Citation(**citation))
        
        return BrandAnalysisResponse(
            success=result["success"],
            analysis=result.get("response"),
            citations=citations,
            brand_name=request.brand_name,
            analysis_type=request.analysis_type,
            error=result.get("error"),
            timestamp=result.get("timestamp")
        )
        
    except Exception as e:
        logger.error(f"Error in brand analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Brand analysis failed: {str(e)}")


@router.delete("/cleanup/{thread_id}/{assistant_id}")
async def cleanup_resources(
    thread_id: str,
    assistant_id: str,
    client: OpenAIResponsesAPI = Depends(get_openai_client)
):
    """
    Clean up OpenAI resources (thread and assistant).
    
    This endpoint deletes the specified thread and assistant to free up resources.
    """
    try:
        logger.info(f"Cleaning up resources: thread={thread_id}, assistant={assistant_id}")
        
        result = await client.cleanup_resources(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        return {
            "success": True,
            "thread_deleted": result["thread_deleted"],
            "assistant_deleted": result["assistant_deleted"]
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for OpenAI Responses API.
    
    Returns configuration status and API availability.
    """
    config = Settings()
    
    return {
        "status": "healthy",
        "openai_configured": config.has_openai_config,
        "model": config.OPENAI_RESPONSES_MODEL,
        "web_search_version": config.OPENAI_WEB_SEARCH_TOOL_VERSION,
        "timestamp": "2024-01-01T00:00:00Z"  # You can make this dynamic
    }


# Example usage endpoints for testing
@router.post("/example/ai-news")
async def get_ai_news_example(
    client: OpenAIResponsesAPI = Depends(get_openai_client)
):
    """
    Example endpoint: Get latest AI news with web search.
    """
    system_prompt = """You are a tech news expert with access to real-time web search. 
    Provide the latest news and developments in artificial intelligence with proper citations."""
    
    user_prompt = "What are the most significant AI developments and news from the past month?"
    
    result = await client.get_response_with_web_search(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        assistant_name="AI News Expert"
    )
    
    return result


@router.post("/example/company-analysis")
async def get_company_analysis_example(
    company_name: str = "Apple",
    client: OpenAIResponsesAPI = Depends(get_openai_client)
):
    """
    Example endpoint: Analyze a company with web search.
    """
    system_prompt = f"""You are a business analyst with access to real-time web search. 
    Provide a comprehensive analysis of {company_name} including their current market position, 
    recent developments, challenges, and future outlook. Use current information and cite sources."""
    
    user_prompt = f"Analyze {company_name}'s current business performance and market position."
    
    result = await client.get_response_with_web_search(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        assistant_name=f"{company_name} Analyst"
    )
    
    return result
