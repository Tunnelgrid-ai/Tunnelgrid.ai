#!/usr/bin/env python3
"""
Standalone Brand Extraction Test
Tests the brand extraction functionality in isolation without codebase dependencies
"""

import json
import asyncio
import httpx
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class BrandExtraction:
    """Simple model for brand extraction results"""
    extracted_brand_name: str
    source_domain: Optional[str]
    source_url: str
    article_title: Optional[str]
    sentiment_label: str  # "positive", "negative", "neutral"
    context_snippet: Optional[str]
    position_in_article: Optional[int]
    is_target_brand: bool

@dataclass
class BrandExtractionResponse:
    """Response model for brand extraction"""
    success: bool
    extractions: List[BrandExtraction]
    error_message: Optional[str] = None

class StandaloneBrandExtractor:
    """Standalone brand extraction service for testing"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    @staticmethod
    def _build_extraction_system_prompt() -> str:
        """Build system prompt for brand extraction"""
        return """You are an expert brand analysis AI. Your task is to extract brand mentions from article content and analyze sentiment.

INSTRUCTIONS:
1. Find ALL brand mentions in the provided content
2. Extract the exact brand name as it appears
3. Determine sentiment: "positive", "negative", or "neutral"
4. Include context snippet (1-2 sentences around the brand mention)
5. Estimate position in article (character index if possible)
6. Extract source information

OUTPUT FORMAT (JSON):
{
    "extractions": [
        {
            "extracted_brand_name": "Tesla",
            "source_domain": "techcrunch.com",
            "source_url": "https://techcrunch.com/article",
            "article_title": "Electric Vehicle Market Analysis",
            "sentiment_label": "positive",
            "context_snippet": "Tesla continues to lead the electric vehicle market with innovative technology.",
            "position_in_article": 450,
            "is_target_brand": true
        }
    ]
}

IMPORTANT:
- Only output valid JSON
- Use exact brand names as they appear
- Sentiment must be: "positive", "negative", or "neutral"
- Include ALL brands found, not just the target brand"""
    
    @staticmethod
    def _build_extraction_user_prompt(content: str, citations: List[Dict], audit_brand_name: str) -> str:
        """Build user prompt with content and citations"""
        # Format citations for easier parsing
        citations_text = ""
        if citations:
            citations_text = "\n\nSOURCE CITATIONS:\n"
            for i, citation in enumerate(citations, 1):
                citations_text += f"{i}. URL: {citation.get('source_url', 'N/A')}\n"
                citations_text += f"   Title: {citation.get('title', 'N/A')}\n"
                citations_text += f"   Domain: {citation.get('source_url', '').replace('https://', '').replace('http://', '').split('/')[0] if citation.get('source_url') else 'N/A'}\n"
                citations_text += f"   Text: {citation.get('text', 'N/A')}\n\n"
        
        return f"""TARGET BRAND: {audit_brand_name}

CONTENT TO ANALYZE:
{content}
{citations_text}

Extract all brand mentions and analyze sentiment. Pay special attention to "{audit_brand_name}" and mark it as target brand when found."""
    
    async def extract_brands_from_content(
        self, 
        content: str, 
        citations: List[Dict[str, Any]], 
        audit_brand_name: str
    ) -> BrandExtractionResponse:
        """Extract brands from content using OpenAI API"""
        try:
            system_prompt = self._build_extraction_system_prompt()
            user_prompt = self._build_extraction_user_prompt(content, citations, audit_brand_name)
            
            # Debug: Log prompts
            logger.debug(f"🔍 System prompt length: {len(system_prompt)} chars")
            logger.debug(f"🔍 User prompt length: {len(user_prompt)} chars")
            logger.debug(f"🔍 User prompt preview: {user_prompt[:300]}...")
            
            # Make API call to OpenAI
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                    logger.error(f"❌ {error_msg}")
                    return BrandExtractionResponse(success=False, extractions=[], error_message=error_msg)
                
                response_data = response.json()
                extraction_content = response_data["choices"][0]["message"]["content"]
                
                # Debug: Log the actual response content
                logger.debug(f"🔍 Brand extraction raw response: {extraction_content[:500]}...")
                
                # Check if response is empty or not JSON
                if not extraction_content or not extraction_content.strip():
                    logger.warning(f"⚠️ OpenAI returned empty content for brand extraction")
                    return BrandExtractionResponse(success=False, extractions=[], error_message="Empty response from OpenAI")
                
                # Parse JSON response (handle markdown wrapper)
                try:
                    # Remove markdown code block wrapper if present
                    clean_content = extraction_content.strip()
                    if clean_content.startswith("```json"):
                        clean_content = clean_content[7:]  # Remove ```json
                    if clean_content.endswith("```"):
                        clean_content = clean_content[:-3]  # Remove closing ```
                    clean_content = clean_content.strip()
                    
                    logger.debug(f"🔧 Cleaned JSON content: {clean_content[:200]}...")
                    extraction_result = json.loads(clean_content)
                    extractions = []
                    
                    # Process extractions
                    for item in extraction_result.get("extractions", []):
                        # Check if this is the target brand
                        extracted_name = item.get("extracted_brand_name", "").lower()
                        is_target = audit_brand_name.lower() in extracted_name or extracted_name in audit_brand_name.lower()
                        
                        extraction = BrandExtraction(
                            extracted_brand_name=item.get("extracted_brand_name", ""),
                            source_domain=item.get("source_domain"),
                            source_url=item.get("source_url", ""),
                            article_title=item.get("article_title"),
                            sentiment_label=item.get("sentiment_label", "neutral"),
                            context_snippet=item.get("context_snippet"),
                            position_in_article=item.get("position_in_article"),
                            is_target_brand=is_target
                        )
                        extractions.append(extraction)
                    
                    logger.info(f"✅ Successfully extracted {len(extractions)} brand mentions")
                    return BrandExtractionResponse(success=True, extractions=extractions)
                
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parsing failed. Content: '{extraction_content[:200]}...'")
                    logger.error(f"❌ JSON Error: {str(e)}")
                    
                    # Try to extract any potential JSON from the response
                    try:
                        import re
                        json_match = re.search(r'\{.*\}', extraction_content, re.DOTALL)
                        if json_match:
                            potential_json = json_match.group(0)
                            logger.debug(f"🔧 Attempting to parse extracted JSON: {potential_json[:200]}...")
                            extraction_result = json.loads(potential_json)
                            # Process the result same as above...
                            return BrandExtractionResponse(success=True, extractions=[])
                        else:
                            error_msg = f"No JSON found in response: {extraction_content[:200]}..."
                            return BrandExtractionResponse(success=False, extractions=[], error_message=error_msg)
                    except Exception as recovery_error:
                        error_msg = f"Failed to recover JSON: {str(recovery_error)}"
                        return BrandExtractionResponse(success=False, extractions=[], error_message=error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error in brand extraction: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return BrandExtractionResponse(success=False, extractions=[], error_message=error_msg)

async def test_brand_extraction():
    """Test the brand extraction functionality"""
    print("🧪 Testing Standalone Brand Extraction...")
    
    # Initialize extractor
    try:
        extractor = StandaloneBrandExtractor()
        print("✅ Extractor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return
    
    # Test data - simulate content from an API response
    test_content = """
    Tesla continues to dominate the electric vehicle market with its innovative approach to sustainable transportation. 
    The company's latest Model Y has received positive reviews from automotive experts. However, competitors like 
    Ford and General Motors are catching up with their own electric offerings. BMW's new electric series has also 
    gained significant traction in the luxury segment. Volkswagen Group is investing heavily in electric infrastructure, 
    while Toyota remains focused on hybrid technology. The electric vehicle market is becoming increasingly competitive.
    """
    
    test_citations = [
        {
            "text": "Tesla Model Y receives excellent safety ratings from NHTSA",
            "source_url": "https://techcrunch.com/tesla-model-y-safety",
            "title": "Tesla Model Y Safety Analysis"
        },
        {
            "text": "Ford announces major investment in electric vehicle production",
            "source_url": "https://reuters.com/ford-electric-investment",
            "title": "Ford's Electric Future"
        },
        {
            "text": "BMW electric vehicle sales surge in Q3",
            "source_url": "https://bloomberg.com/bmw-electric-sales",
            "title": "BMW Electric Vehicle Report"
        }
    ]
    
    target_brand = "Tesla"
    
    print(f"\n📊 Test Parameters:")
    print(f"Target Brand: {target_brand}")
    print(f"Content Length: {len(test_content)} characters")
    print(f"Citations Count: {len(test_citations)}")
    
    # Run extraction
    print(f"\n🔄 Running brand extraction...")
    result = await extractor.extract_brands_from_content(
        content=test_content,
        citations=test_citations,
        audit_brand_name=target_brand
    )
    
    # Display results
    print(f"\n📋 Results:")
    print(f"Success: {result.success}")
    
    if result.success:
        print(f"Total Extractions: {len(result.extractions)}")
        
        for i, extraction in enumerate(result.extractions, 1):
            print(f"\n{i}. Brand: {extraction.extracted_brand_name}")
            print(f"   Sentiment: {extraction.sentiment_label}")
            print(f"   Is Target Brand: {extraction.is_target_brand}")
            print(f"   Source URL: {extraction.source_url}")
            print(f"   Article Title: {extraction.article_title}")
            print(f"   Context: {extraction.context_snippet[:100] if extraction.context_snippet else 'N/A'}...")
            print(f"   Position: {extraction.position_in_article}")
    else:
        print(f"❌ Error: {result.error_message}")

def main():
    """Main function to run the test"""
    print("=" * 60)
    print("🚀 STANDALONE BRAND EXTRACTION TEST")
    print("=" * 60)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please set your OpenAI API key in the .env file")
        return
    
    # Run async test
    asyncio.run(test_brand_extraction())
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
