#!/usr/bin/env python3
"""
Simple test to verify AIAnalysisRequest model fix
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app.models.analysis import AIAnalysisRequest, LLMServiceType
    
    # Test creating the request with service field
    request = AIAnalysisRequest(
        query_id="test-query-id",
        persona_description="Test persona description",
        question_text="Test question text",
        model="openai-4o",
        service=LLMServiceType.OPENAI
    )
    
    print("✅ SUCCESS: AIAnalysisRequest created successfully!")
    print(f"📋 Request data: {request.dict()}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc() 