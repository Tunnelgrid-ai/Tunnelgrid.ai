"""
OpenAI AI Analysis Service using Responses API

This service handles brand perception analysis using OpenAI's Responses API
with web search capabilities for comprehensive, citation-rich responses.
"""

import time
import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

import httpx
from openai import OpenAI

from ..core.config import settings
from ..models.analysis import (
    AIAnalysisRequest, AIAnalysisResponse, Citation, 
    BrandMention, LLMServiceType
)

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    OpenAI AI Analysis Service using Responses API
    
    This service provides comprehensive brand analysis with web search capabilities,
    citation extraction, and brand mention tracking.
    """
    
    def __init__(self):
        """Initialize the OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_brand_perception(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        """
        Analyze brand perception using OpenAI Responses API with web search
        
        This method uses the Responses API to:
        1. Perform web search for current information
        2. Generate persona-based responses
        3. Extract comprehensive citations
        4. Track brand mentions with source attribution
        
        Args:
            request: AIAnalysisRequest containing query details and persona information
            
        Returns:
            AIAnalysisResponse with response text, citations, and brand mentions
            
        Raises:
            Exception: If API calls fail after retries
        """
        start_time = time.time()
        max_retries = 3
        retry_delay = 2
        
        logger.info(f"🔍 Starting brand perception analysis for query {request.query_id}")
        logger.info(f"👤 Persona: {request.persona_description[:100]}...")
        logger.info(f"❓ Question: {request.question_text}")
        
        for attempt in range(max_retries):
            try:
                # Build comprehensive system prompt with persona details
                system_prompt = OpenAIService._build_persona_system_prompt(request.persona_description)
                
                # Configure web search tool for comprehensive results
                web_search_tool = {
                    "type": "web_search",
                    "search_context_size": "medium",  # Balanced approach for speed and comprehensiveness
                    "user_location": {
                        "type": "approximate",
                        "country": "US"
                    }
                }
                
                logger.info(f"🤖 Making OpenAI Responses API call (attempt {attempt + 1}/{max_retries})")
                logger.debug(f"📝 System prompt length: {len(system_prompt)} characters")
                
                # Make API call using Responses API
                response = self.client.responses.create(
                    model="gpt-4o",
                    tools=[web_search_tool],
                    input=f"{system_prompt}\n\nQuestion: {request.question_text}"
                )
                
                # Extract and process response
                ai_content = response.output_text
                citations = OpenAIService._extract_citations_from_response(response, request.service)
                brand_mentions = OpenAIService._extract_brand_mentions_with_sources(
                    ai_content, citations, request.service
                )
                
                processing_time = int((time.time() - start_time) * 1000)
                
                logger.info(f"✅ Analysis completed successfully")
                logger.info(f"📊 Results: {len(citations)} citations, {len(brand_mentions)} brand mentions")
                logger.info(f"⏱️ Processing time: {processing_time}ms")
                
                return AIAnalysisResponse(
                    query_id=request.query_id,
                    model=request.model,
                    service=request.service,
                    response_text=ai_content,
                    citations=citations,
                    brand_mentions=brand_mentions,
                    processing_time_ms=processing_time,
                    token_usage={"total_tokens": 0}  # Responses API doesn't provide token usage
                )
                
            except Exception as e:
                logger.error(f"❌ OpenAI Responses API error for query {request.query_id} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"�� All retry attempts failed for query {request.query_id}")
                    raise Exception(f"OpenAI Responses API failed after {max_retries} attempts: {str(e)}")

    @staticmethod
    def _build_persona_system_prompt(persona_description: str) -> str:
        """
        Build a comprehensive system prompt that tailors responses to the specified persona
        
        This prompt is designed to:
        1. Establish the persona's characteristics and needs
        2. Guide the LLM to respond TO this persona (not AS this persona)
        3. Tailor language, complexity, and explanations to their background
        4. Address their specific pain points and concerns proactively
        5. Present information in a way that resonates with their situation
        
        Args:
            persona_description: Detailed persona information including demographics, 
                               pain points, motivators, and characteristics
            
        Returns:
            Formatted system prompt that tailors responses to the persona
        """
        return f"""# System Prompt: "You are responding to the following persona. The user sending this request IS this persona, and you should tailor your responses specifically to their profile, needs, and situation."

PERSONA PROFILE:
{persona_description}

INSTRUCTIONS:
- The user sending this request IS this persona
- Respond to their questions with answers tailored specifically to this persona's situation, knowledge level, and needs
- Use language and explanations appropriate for their background and expertise
- Address their specific pain points, motivators, and concerns in your responses  
- Consider what this persona would realistically know vs. what they might need explained
- When providing information, cite sources and present it in a way this persona would find most useful
- Adjust your tone and complexity to match what would resonate with this persona
- If this persona would have specific follow-up concerns or considerations about the topic, proactively address them

Remember: You are responding TO this persona, not AS this persona. Tailor every aspect of your response to their specific profile, needs, and situation."""

    @staticmethod
    def _extract_citations_from_response(response, service: LLMServiceType) -> List[Citation]:
        """
        Extract comprehensive citations from OpenAI Responses API response
        
        This method processes the structured response from the Responses API to extract:
        1. URL citations with full metadata
        2. Source titles and URLs
        3. Text positions for citation mapping
        4. Search call metadata
        
        Args:
            response: OpenAI Responses API response object
            service: LLM service type for tracking
            
        Returns:
            List of Citation objects with full metadata
        """
        citations = []
        
        logger.debug("🔍 Extracting citations from Responses API response")
        
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                if item.type == "web_search_call":
                    logger.debug(f"🔍 Found web search call: {item.id} - {item.status}")
                    
                elif item.type == "message" and hasattr(item, 'content'):
                    for content in item.content:
                        if hasattr(content, 'annotations'):
                            for annotation in content.annotations:
                                if annotation.type == "url_citation":
                                    # Extract the actual cited text snippet from the response
                                    cited_text = ""
                                    if hasattr(annotation, 'start_index') and hasattr(annotation, 'end_index'):
                                        start_idx = annotation.start_index
                                        end_idx = annotation.end_index
                                        if start_idx is not None and end_idx is not None:
                                            cited_text = response.output_text[start_idx:end_idx].strip()
                                    
                                    # If we couldn't extract the text snippet, use a descriptive reference
                                    if not cited_text:
                                        cited_text = f"Information from {annotation.title or 'web source'}"
                                    
                                    # Create citation with actual cited text
                                    citation = Citation(
                                        text=cited_text,  # The actual cited text snippet
                                        source_url=annotation.url,
                                        source_title=annotation.title or "Web source",  # Page title
                                        start_index=annotation.start_index,
                                        end_index=annotation.end_index,
                                        service=service
                                    )
                                    
                                    citations.append(citation)
                                    
                                    logger.debug(f"�� Extracted citation: {annotation.title} - {annotation.url}")
                                    logger.debug(f"�� Cited text: {cited_text[:100]}...")
        
        logger.info(f"📊 Extracted {len(citations)} citations from response")
        return citations

    @staticmethod
    def _extract_brand_mentions_with_sources(
        text: str, 
        citations: List[Citation], 
        service: LLMServiceType
    ) -> List[BrandMention]:
        """
        Extract brand mentions with source attribution from response text and citations
        
        This method identifies brand mentions and associates them with their sources:
        1. Extracts brand mentions from main response text
        2. Maps mentions to specific citations when possible
        3. Provides source attribution for each mention
        4. Handles both direct and contextual brand references
        
        Args:
            text: Main response text
            citations: List of citations with source information
            service: LLM service type for tracking
            
        Returns:
            List of BrandMention objects with source attribution
        """
        brand_mentions = []
        
        logger.debug("🔍 Extracting brand mentions with source attribution")
        
        # Extract brand mentions from main text
        main_mentions = OpenAIService._extract_brand_mentions_from_text(text, service)
        brand_mentions.extend(main_mentions)
        
        # Extract brand mentions from citation contexts
        for citation in citations:
            if citation.source_url:
                # Extract brand mentions from citation text
                citation_mentions = OpenAIService._extract_brand_mentions_from_text(
                    citation.text, service
                )
                
                # Associate mentions with this citation source
                for mention in citation_mentions:
                    mention.source_url = citation.source_url
                    mention.source_title = citation.text
                    brand_mentions.append(mention)
        
        # Remove duplicates while preserving source information
        unique_mentions = OpenAIService._deduplicate_brand_mentions(brand_mentions)
        
        logger.info(f"📊 Extracted {len(unique_mentions)} unique brand mentions with sources")
        return unique_mentions

    @staticmethod
    def _extract_brand_mentions_from_text(text: str, service: LLMServiceType) -> List[BrandMention]:
        """
        Extract brand mentions from text using pattern matching
        
        This method identifies brand mentions using various patterns:
        1. Direct brand name mentions
        2. Brand name variations and abbreviations
        3. Contextual brand references
        4. Product/service associations
        
        Args:
            text: Text to analyze for brand mentions
            service: LLM service type for tracking
            
        Returns:
            List of BrandMention objects
        """
        mentions = []
        
        # Common brand name patterns (case-insensitive)
        brand_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Co|Brand|Products|Services)\b',
            r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b',  # Acronyms like "IBM", "HP"
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'  # Multi-word brand names
        ]
        
        for pattern in brand_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                brand_name = match.group().strip()
                
                # Filter out common words that aren't brands
                if len(brand_name) > 2 and brand_name.lower() not in [
                    'the', 'and', 'or', 'but', 'for', 'with', 'from', 'this', 'that'
                ]:
                    mention = BrandMention(
                        brand_name=brand_name,
                        context=match.group(),
                        sentiment="neutral",  # Basic sentiment, could be enhanced
                        service=service
                    )
                    mentions.append(mention)
        
        return mentions

    @staticmethod
    def _deduplicate_brand_mentions(mentions: List[BrandMention]) -> List[BrandMention]:
        """
        Remove duplicate brand mentions while preserving source information
        
        Args:
            mentions: List of brand mentions that may contain duplicates
            
        Returns:
            List of unique brand mentions with combined source information
        """
        unique_mentions = {}
        
        for mention in mentions:
            key = mention.brand_name.lower()
            
            if key not in unique_mentions:
                unique_mentions[key] = mention
            else:
                # Combine source information if this mention has additional sources
                existing = unique_mentions[key]
                if mention.source_url and not existing.source_url:
                    existing.source_url = mention.source_url
                    existing.source_title = mention.source_title
                elif mention.source_url and existing.source_url and mention.source_url != existing.source_url:
                    # Multiple sources - could enhance this to store multiple sources
                    existing.source_url = f"{existing.source_url}; {mention.source_url}"
        
        return list(unique_mentions.values())

# Create service instance for import
openai_service = OpenAIService()