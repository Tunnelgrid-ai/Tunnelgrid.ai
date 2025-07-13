"""
OpenAI Web Search Service using Responses API
"""
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..core.config import settings

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def search_web(
        self,
        query: str,
        context_size: Optional[str] = None,
        user_location: Optional[Dict[str, Any]] = None,
        force_search: bool = False
    ) -> Dict[str, Any]:
        """
        Perform web search using OpenAI Responses API
        
        Args:
            query: The search query
            context_size: 'low', 'medium', or 'high'
            user_location: Location context for search
            force_search: Force use of web search tool
        """
        try:
            # Configure web search tool
            web_search_tool = {
                "type": settings.OPENAI_WEB_SEARCH_TOOL_VERSION,
                "search_context_size": context_size or settings.OPENAI_SEARCH_CONTEXT_SIZE
            }
            
            # Add user location if provided or configured
            if user_location or any([
                settings.OPENAI_SEARCH_USER_LOCATION_COUNTRY,
                settings.OPENAI_SEARCH_USER_LOCATION_CITY,
                settings.OPENAI_SEARCH_USER_LOCATION_REGION,
                settings.OPENAI_SEARCH_USER_LOCATION_TIMEZONE
            ]):
                location_config = user_location or {
                    "type": "approximate",
                    "country": settings.OPENAI_SEARCH_USER_LOCATION_COUNTRY,
                    "city": settings.OPENAI_SEARCH_USER_LOCATION_CITY,
                    "region": settings.OPENAI_SEARCH_USER_LOCATION_REGION,
                    "timezone": settings.OPENAI_SEARCH_USER_LOCATION_TIMEZONE
                }
                # Remove None values
                location_config = {k: v for k, v in location_config.items() if v is not None}
                web_search_tool["user_location"] = location_config
            
            # Configure request parameters
            request_params = {
                "model": settings.OPENAI_RESPONSES_MODEL,
                "tools": [web_search_tool],
                "input": query
            }
            
            # Force web search if requested
            if force_search:
                request_params["tool_choice"] = {"type": settings.OPENAI_WEB_SEARCH_TOOL_VERSION}
            
            # Make the API call
            response = self.client.responses.create(**request_params)
            
            # Extract results
            result = {
                "success": True,
                "output_text": response.output_text,
                "citations": [],
                "search_calls": []
            }
            
            # Parse response for citations and search calls
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    if item.type == "web_search_call":
                        result["search_calls"].append({
                            "id": item.id,
                            "status": item.status
                        })
                    elif item.type == "message" and hasattr(item, 'content'):
                        for content in item.content:
                            if hasattr(content, 'annotations'):
                                for annotation in content.annotations:
                                    if annotation.type == "url_citation":
                                        result["citations"].append({
                                            "url": annotation.url,
                                            "title": annotation.title,
                                            "start_index": annotation.start_index,
                                            "end_index": annotation.end_index
                                        })
            
            return result
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output_text": None,
                "citations": [],
                "search_calls": []
            }

# Global instance
websearch_service = WebSearchService() 