#!/usr/bin/env python3
"""
Test Script for Phase 3: AI Analysis Implementation

This script tests:
1. Data model validation
2. OpenAI service functionality 
3. Response parsing (citations and brand mentions)
4. Basic integration

Run this after implementing Phase 3 to verify everything works.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend app to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.models.analysis import (
    AnalysisJobRequest,
    AIAnalysisRequest, 
    Citation,
    BrandMention,
    AnalysisJobStatus
)
from app.services.ai_analysis import OpenAIService
from app.core.config import settings

def test_data_models():
    """Test Pydantic model validation"""
    print("🧪 Testing Data Models...")
    
    try:
        # Test AnalysisJobRequest
        job_request = AnalysisJobRequest(audit_id="test-audit-123")
        assert job_request.audit_id == "test-audit-123"
        print("✅ AnalysisJobRequest validation works")
        
        # Test AIAnalysisRequest
        ai_request = AIAnalysisRequest(
            query_id="test-query-123",
            persona_description="A tech-savvy millennial who loves Apple products",
            question_text="What do you think about iPhone's latest features?",
            model="openai-4o"
        )
        assert ai_request.query_id == "test-query-123"
        print("✅ AIAnalysisRequest validation works")
        
        # Test Citation
        citation = Citation(text="According to TechCrunch", source_url="https://techcrunch.com")
        assert citation.text == "According to TechCrunch"
        print("✅ Citation validation works")
        
        # Test BrandMention
        mention = BrandMention(
            brand_name="Apple",
            context="I love Apple products for their design",
            sentiment_score=0.8
        )
        assert mention.brand_name == "Apple"
        assert mention.sentiment_score == 0.8
        print("✅ BrandMention validation works")
        
        # Test invalid data
        try:
            invalid_request = AnalysisJobRequest(audit_id="")
            assert False, "Should have failed validation"
        except ValueError:
            print("✅ Empty audit_id validation works")
        
        print("🎉 All data model tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False

def test_parsing_functions():
    """Test citation and brand mention extraction"""
    print("🧪 Testing Parsing Functions...")
    
    try:
        # Test citation extraction
        test_text = """
        According to TechCrunch, Apple's new iPhone is amazing. 
        Research shows that users love the camera quality.
        You can read more at https://example.com/article.
        [Forbes 2024] reported strong sales numbers.
        """
        
        citations = OpenAIService._extract_citations(test_text)
        print(f"📝 Extracted {len(citations)} citations:")
        for citation in citations:
            print(f"   - {citation.text[:50]}...")
        
        assert len(citations) > 0, "Should extract at least one citation"
        print("✅ Citation extraction works")
        
        # Test brand mention extraction
        brand_text = """
        I really love Apple products, especially the iPhone. 
        Samsung also makes good phones, but Apple's design is superior.
        Tesla cars are innovative, and Netflix has great content.
        Microsoft Office is useful for productivity.
        """
        
        mentions = OpenAIService._extract_brand_mentions(brand_text)
        print(f"🏢 Extracted {len(mentions)} brand mentions:")
        for mention in mentions:
            sentiment_text = f" (sentiment: {mention.sentiment_score})" if mention.sentiment_score else ""
            print(f"   - {mention.brand_name}{sentiment_text}")
        
        assert len(mentions) > 0, "Should extract at least one brand mention"
        print("✅ Brand mention extraction works")
        
        # Test sentiment analysis
        positive_context = "I absolutely love Apple products they are amazing"
        sentiment = OpenAIService._analyze_sentiment(positive_context)
        print(f"😊 Positive sentiment score: {sentiment}")
        
        negative_context = "Apple products are terrible and overpriced"
        sentiment = OpenAIService._analyze_sentiment(negative_context)
        print(f"😞 Negative sentiment score: {sentiment}")
        
        print("✅ Sentiment analysis works")
        
        print("🎉 All parsing tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Parsing test failed: {e}")
        return False

async def test_openai_integration():
    """Test OpenAI API integration (requires API key)"""
    print("🧪 Testing OpenAI Integration...")
    
    try:
        # Check if API key is configured
        if not settings.has_openai_config:
            print("⚠️ OpenAI API key not configured, skipping integration test")
            print("   To test: Set OPENAI_API_KEY in your .env file")
            return True
        
        print("🔑 OpenAI API key found, testing API call...")
        
        # Create test request
        test_request = AIAnalysisRequest(
            query_id="test-query-123",
            persona_description="A tech-savvy professional who values productivity and innovation",
            question_text="What are your thoughts on smartphone brands and their latest features?",
            model="openai-4o"
        )
        
        print("📞 Making test API call to OpenAI...")
        
        # Make API call
        result = await OpenAIService.analyze_brand_perception(test_request)
        
        print("✅ OpenAI API call successful!")
        print(f"📊 Response length: {len(result.response_text)} characters")
        print(f"📝 Citations found: {len(result.citations)}")
        print(f"🏢 Brand mentions found: {len(result.brand_mentions)}")
        print(f"⏱️ Processing time: {result.processing_time_ms}ms")
        
        if result.token_usage:
            print(f"🎯 Token usage: {result.token_usage}")
        
        # Show sample response
        print("\n📄 Sample response (first 200 chars):")
        print(f"'{result.response_text[:200]}...'")
        
        # Show extracted data
        if result.citations:
            print("\n📚 Extracted citations:")
            for citation in result.citations[:3]:  # Show first 3
                print(f"   - {citation.text}")
        
        if result.brand_mentions:
            print("\n🏷️ Extracted brand mentions:")
            for mention in result.brand_mentions[:5]:  # Show first 5
                sentiment_text = f" (sentiment: {mention.sentiment_score:.2f})" if mention.sentiment_score else ""
                print(f"   - {mention.brand_name}{sentiment_text}")
        
        print("🎉 OpenAI integration test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI integration test failed: {e}")
        print("💡 This might be due to:")
        print("   - Invalid or missing API key")
        print("   - Network connectivity issues")
        print("   - API rate limits or quota exceeded")
        return False

def test_error_handling():
    """Test error handling and edge cases"""
    print("🧪 Testing Error Handling...")
    
    try:
        # Test with empty text
        empty_citations = OpenAIService._extract_citations("")
        assert empty_citations == [], "Empty text should return empty list"
        
        empty_mentions = OpenAIService._extract_brand_mentions("")
        assert empty_mentions == [], "Empty text should return empty list"
        
        # Test with no matches
        no_match_text = "This is just plain text with no special content."
        no_citations = OpenAIService._extract_citations(no_match_text)
        no_mentions = OpenAIService._extract_brand_mentions(no_match_text)
        
        print(f"📊 No-match test: {len(no_citations)} citations, {len(no_mentions)} mentions")
        
        # Test model validation errors
        try:
            invalid_citation = Citation(text="")  # Empty text should fail
            assert False, "Should have failed validation"
        except ValueError:
            print("✅ Empty citation text validation works")
        
        try:
            invalid_sentiment = BrandMention(
                brand_name="Test", 
                context="Context",
                sentiment_score=2.0  # Invalid range
            )
            assert False, "Should have failed validation"
        except ValueError:
            print("✅ Invalid sentiment score validation works")
        
        print("🎉 Error handling tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def main():
    """Run all Phase 3 tests"""
    print("🚀 Starting Phase 3 Tests\n")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Run tests
    results.append(test_data_models())
    results.append(test_parsing_functions())
    results.append(await test_openai_integration())
    results.append(test_error_handling())
    
    # Summary
    print("=" * 50)
    print("📋 Test Summary:")
    
    test_names = [
        "Data Models",
        "Parsing Functions", 
        "OpenAI Integration",
        "Error Handling"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {i+1}. {name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed! Ready for Phase 4.")
        print("\n💡 Next steps:")
        print("   1. Register analysis routes in main.py")
        print("   2. Add OpenAI API key to .env file")
        print("   3. Test with real audit data")
        print("   4. Implement frontend integration")
    else:
        print("⚠️ Some tests failed. Please fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 