#!/usr/bin/env python3
"""
Test AI Analysis Fix Script
Tests that the Citation and BrandMention service field validation errors are resolved
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app.models.analysis import AIAnalysisRequest, Citation, BrandMention, LLMServiceType
    from app.services.ai_analysis import OpenAIService
    
    # Test creating Citation with service field
    citation = Citation(
        text="Test citation",
        source_url="https://example.com",
        service=LLMServiceType.OPENAI
    )
    print("✅ SUCCESS: Citation created successfully!")
    print(f"📋 Citation data: {citation.dict()}")
    
    # Test creating BrandMention with service field
    brand_mention = BrandMention(
        brand_name="Test Brand",
        context="Test context",
        sentiment_score=0.5,
        service=LLMServiceType.OPENAI
    )
    print("✅ SUCCESS: BrandMention created successfully!")
    print(f"📋 BrandMention data: {brand_mention.dict()}")
    
    # Test creating AIAnalysisRequest with service field
    request = AIAnalysisRequest(
        query_id="test-query-id",
        persona_description="Test persona",
        question_text="Test question",
        model="openai-4o",
        service=LLMServiceType.OPENAI
    )
    print("✅ SUCCESS: AIAnalysisRequest created successfully!")
    print(f"📋 Request data: {request.dict()}")
    
    print("\n🎉 All validation tests passed! The service field errors should be resolved.")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc() 