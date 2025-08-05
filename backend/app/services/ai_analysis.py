"""
AI Analysis Service for Brand Perception Analysis

This module provides AI-powered brand analysis using OpenAI GPT-4o.
It includes response parsing for citations and brand mentions.
"""

import asyncio
import time
import re
import logging
from typing import List, Dict, Tuple, Optional, Any
import httpx

from ..core.config import settings
from ..models.analysis import (
    AIAnalysisRequest, 
    AIAnalysisResponse, 
    Citation, 
    BrandMention,
    LLMServiceType
)

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI GPT-4o API integration"""
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    @staticmethod
    async def analyze_brand_perception(request: AIAnalysisRequest) -> AIAnalysisResponse:
        """
        Analyze brand perception using OpenAI GPT-4o with retry logic for server errors
        
        Args:
            request: AIAnalysisRequest with query details and persona
            
        Returns:
            AIAnalysisResponse with parsed citations and brand mentions
            
        Raises:
            Exception: If API call fails after all retries or response is invalid
        """
        start_time = time.time()
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Construct system prompt with persona context
                system_prompt = OpenAIService._build_system_prompt(request.persona_description)
                
                # Prepare API request
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4o",  # Using GPT-4o specifically for brand analysis
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.question_text}
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "presence_penalty": 0.1,  # Encourage diverse responses
                    "frequency_penalty": 0.1   # Reduce repetition
                }
                
                logger.info(f"🤖 Making OpenAI API call for query {request.query_id} (attempt {attempt + 1}/{max_retries})")
                logger.debug(f"Persona: {request.persona_description[:100]}...")
                logger.debug(f"Question: {request.question_text[:100]}...")
                
                # Make API call with timeout
                timeout = httpx.Timeout(60.0)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        OpenAIService.BASE_URL, 
                        headers=headers, 
                        json=payload
                    )
                    
                    if response.status_code == 500:
                        # Server error - retry
                        error_msg = f"OpenAI server error (attempt {attempt + 1}/{max_retries}): {response.status_code} - {response.text}"
                        logger.warning(error_msg)
                        if attempt < max_retries - 1:
                            logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                            logger.error(f"❌ All retries exhausted for query {request.query_id}")
                            raise Exception(f"OpenAI server error after {max_retries} attempts: {response.text}")
                    elif response.status_code != 200:
                        # Non-retryable error
                        error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    response_data = response.json()
                    ai_content = response_data["choices"][0]["message"]["content"]
                    token_usage = response_data.get("usage", {})
                    
                    logger.info(f"✅ OpenAI response received for query {request.query_id}")
                    logger.debug(f"Response length: {len(ai_content)} characters")
                    logger.debug(f"Token usage: {token_usage}")
                    
                    # Check for annotations in the response
                    annotations = response_data["choices"][0]["message"].get("annotations", [])
                    if annotations:
                        citations = OpenAIService._extract_citations_from_annotations(annotations, request.service)
                        brand_mentions = OpenAIService._extract_brand_mentions_with_context(ai_content, annotations, request.service)
                    else:
                        citations = OpenAIService._extract_citations(ai_content, request.service)
                        brand_mentions = OpenAIService._extract_brand_mentions(ai_content, request.service)
                    
                    processing_time = int((time.time() - start_time) * 1000)
                    
                    logger.info(f"📊 Extracted {len(citations)} citations and {len(brand_mentions)} brand mentions")
                    
                    return AIAnalysisResponse(
                        query_id=request.query_id,
                        model=request.model,
                        service=request.service,
                        response_text=ai_content,
                        citations=citations,
                        brand_mentions=brand_mentions,
                        processing_time_ms=processing_time,
                        token_usage=token_usage
                    )
                    
            except httpx.TimeoutException:
                logger.error(f"❌ OpenAI API timeout for query {request.query_id} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying timeout in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise Exception("OpenAI API request timed out after all retries")
            except httpx.RequestError as e:
                logger.error(f"❌ OpenAI API request error for query {request.query_id} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying request error in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise Exception(f"OpenAI API request failed after all retries: {str(e)}")
            except Exception as e:
                logger.error(f"❌ Unexpected error in OpenAI analysis for query {request.query_id} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying unexpected error in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise
    
    @staticmethod
    def _build_system_prompt(persona_description: str) -> str:
        """
        Build system prompt for AI analysis with persona context
        
        Args:
            persona_description: Description of the persona to embody
            
        Returns:
            Formatted system prompt string
        """
        return f"""You are {persona_description}.

Please answer the following question naturally and authentically from your perspective as this persona. 

Important guidelines:
1. Stay true to your persona's characteristics, preferences, and viewpoint
2. Be specific and detailed in your response
3. Mention specific brand names, products, or services when relevant
4. If you reference information from sources, please indicate where it comes from
5. Share your genuine opinions and experiences as this persona would
6. Use language and tone appropriate for your persona

Your response should feel authentic and provide valuable insights about brand perception from your unique perspective."""

    @staticmethod
    def _extract_citations(text: str, service: LLMServiceType) -> List[Citation]:
        """
        Extract citations and references from AI response text
        
        Args:
            text: The AI response text to parse
            
        Returns:
            List of Citation objects found in the text
        """
        citations = []
        
        # Pattern 1: URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+(?:\.[^\s<>"{}|\\^`[\]]+)*'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            # Clean up URL (remove trailing punctuation)
            clean_url = re.sub(r'[.,;!?]+$', '', url)
            citations.append(Citation(
                text=f"Referenced URL: {clean_url}",
                source_url=clean_url,
                service=service
            ))
        
        # Pattern 2: Source references
        source_patterns = [
            r'according to ([^,.]{1,100}?)(?:[,.]|$)',
            r'as reported by ([^,.]{1,100}?)(?:[,.]|$)', 
            r'source: ([^,.]{1,100}?)(?:[,.]|$)',
            r'based on ([^,.]{1,100}?)(?:[,.]|$)',
            r'studies show ([^,.]{1,100}?)(?:[,.]|$)',
            r'research indicates ([^,.]{1,100}?)(?:[,.]|$)',
            r'([^,.]{1,100}?) reports that',
            r'([^,.]{1,100}?) found that',
            r'([^,.]{1,100}?) study shows'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip()
                if len(clean_match) > 3:  # Filter out very short matches
                    citations.append(Citation(text=clean_match, service=service))
        
        # Pattern 3: Bracketed references
        bracket_pattern = r'\[([^\]]{1,100})\]'
        bracket_matches = re.findall(bracket_pattern, text)
        for match in bracket_matches:
            clean_match = match.strip()
            if len(clean_match) > 3:
                citations.append(Citation(text=clean_match, service=service))
        
        # Remove duplicates while preserving order
        seen_texts = set()
        unique_citations = []
        for citation in citations:
            if citation.text.lower() not in seen_texts:
                seen_texts.add(citation.text.lower())
                unique_citations.append(citation)
        
        return unique_citations
    
    @staticmethod
    def _extract_brand_mentions(text: str, service: LLMServiceType) -> List[BrandMention]:
        """
        Extract brand mentions from AI response text
        
        Args:
            text: The AI response text to parse
            
        Returns:
            List of BrandMention objects found in the text
        """
        brand_mentions = []
        
        # Common brand patterns
        brand_patterns = [
            # Tech giants
            r'\b(Apple|Google|Microsoft|Amazon|Meta|Facebook|Tesla|Netflix|Spotify|Uber|Airbnb|Twitter|TikTok|Instagram|WhatsApp|YouTube|LinkedIn|Snapchat|Discord|Slack|Zoom|Adobe|Oracle|Salesforce|IBM|Intel|AMD|NVIDIA|Samsung|Sony|LG|Huawei|Xiaomi|OnePlus|Oppo|Vivo)\b',
            
            # Automotive brands
            r'\b(Toyota|Honda|Ford|Chevrolet|BMW|Mercedes|Audi|Volkswagen|Nissan|Hyundai|Kia|Mazda|Subaru|Lexus|Acura|Infiniti|Cadillac|Lincoln|Porsche|Ferrari|Lamborghini|Maserati|Bentley|Rolls-Royce|Jaguar|Land Rover|Volvo|Peugeot|Citroën|Renault|Fiat|Alfa Romeo)\b',
            
            # Retail and consumer brands
            r'\b(Walmart|Target|Costco|Home Depot|Lowes|Best Buy|McDonalds|Starbucks|Subway|KFC|Pizza Hut|Dominos|Burger King|Taco Bell|Chipotle|Dunkin|Nike|Adidas|Under Armour|Puma|Reebok|New Balance|Lululemon|Gap|H&M|Zara|Uniqlo|Old Navy|Banana Republic)\b',
            
            # Company suffixes
            r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+(?:Inc|Corp|Corporation|Company|Ltd|LLC|Group|Holdings|Enterprises|Solutions|Technologies|Systems|Services|International|Global|Worldwide)\b'
        ]
        
        for pattern in brand_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                brand_name = match.group(1) if match.groups() else match.group(0)
                brand_name = brand_name.strip()
                
                # Skip very short matches or common words
                if len(brand_name) < 2 or brand_name.lower() in ['inc', 'corp', 'ltd', 'llc', 'co', 'the', 'and', 'or', 'of']:
                    continue
                
                # Extract context around the mention (±50 characters)
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(text), match.end() + 50)
                context = text[start_pos:end_pos].strip()
                
                # Basic sentiment analysis (simple keyword approach)
                sentiment_score = OpenAIService._analyze_sentiment(context)
                
                brand_mentions.append(BrandMention(
                    brand_name=brand_name,
                    context=context,
                    sentiment_score=sentiment_score,
                    service=service
                ))
        
        # Remove duplicates while preserving order
        seen_brands = set()
        unique_mentions = []
        for mention in brand_mentions:
            brand_key = (mention.brand_name.lower(), mention.context.lower())
            if brand_key not in seen_brands:
                seen_brands.add(brand_key)
                unique_mentions.append(mention)
        
        return unique_mentions
    
    @staticmethod
    def _analyze_sentiment(context: str) -> Optional[float]:
        """
        Basic sentiment analysis for brand mentions
        
        Args:
            context: Text context around the brand mention
            
        Returns:
            Sentiment score between -1.0 (negative) and 1.0 (positive)
        """
        context_lower = context.lower()
        
        # Positive sentiment indicators
        positive_words = [
            'love', 'like', 'enjoy', 'great', 'excellent', 'amazing', 'awesome', 
            'fantastic', 'wonderful', 'good', 'best', 'prefer', 'recommend', 
            'favorite', 'impressed', 'satisfied', 'happy', 'pleased', 'quality',
            'reliable', 'trustworthy', 'innovative', 'superior', 'outstanding'
        ]
        
        # Negative sentiment indicators  
        negative_words = [
            'hate', 'dislike', 'bad', 'terrible', 'awful', 'horrible', 'worst',
            'disappointing', 'frustrated', 'annoying', 'problem', 'issue', 
            'complaint', 'poor', 'cheap', 'unreliable', 'overpriced', 'expensive',
            'confusing', 'difficult', 'hard', 'complicated', 'slow', 'buggy'
        ]
        
        positive_count = sum(1 for word in positive_words if word in context_lower)
        negative_count = sum(1 for word in negative_words if word in context_lower)
        
        if positive_count == 0 and negative_count == 0:
            return None  # Neutral/unclear sentiment
        
        # Calculate sentiment score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return None
            
        sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Clamp to valid range
        return max(-1.0, min(1.0, sentiment_score))

    @staticmethod
    def _extract_citations_from_annotations(annotations: List[Dict[str, Any]], service: LLMServiceType) -> List[Citation]:
        """
        Extract citations from GPT-4 search preview API annotations
        Args:
            annotations: List of annotation objects from the API response
        Returns:
            List of Citation objects
        """
        citations = []
        for annotation in annotations:
            if annotation.get('type') == 'url_citation':
                url_citation = annotation.get('url_citation', {})
                citations.append(Citation(
                    text=url_citation.get('title', ''),
                    source_url=url_citation.get('url'),
                    service=service
                ))
        return citations

    @staticmethod
    def _extract_brand_mentions_with_context(text: str, annotations: List[Dict[str, Any]], service: LLMServiceType) -> List[BrandMention]:
        """
        Extract brand mentions with context from both the main text and citations
        Args:
            text: The main response text
            annotations: List of annotation objects from the API response
        Returns:
            List of BrandMention objects
        """
        brand_mentions = []
        # Extract brand mentions from main text
        main_mentions = OpenAIService._extract_brand_mentions(text, service)
        brand_mentions.extend(main_mentions)
        # Extract brand mentions from citation contexts
        for annotation in annotations:
            if annotation.get('type') == 'url_citation':
                url_citation = annotation.get('url_citation', {})
                start_idx = url_citation.get('start_index', 0)
                end_idx = url_citation.get('end_index', 0)
                context = text[start_idx:end_idx]
                citation_mentions = OpenAIService._extract_brand_mentions(context, service)
                for mention in citation_mentions:
                    # Optionally associate the source_url with the mention if needed
                    mention.source_url = url_citation.get('url')
                brand_mentions.extend(citation_mentions)
        return brand_mentions

# Service instance for dependency injection
openai_service = OpenAIService() 