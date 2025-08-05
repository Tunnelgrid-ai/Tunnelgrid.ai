#!/usr/bin/env python3
"""
Test Analysis Fix Script
Tests that the AIAnalysisRequest service field fix works correctly
"""

import requests
import json
import sys
import os

def test_analysis_request():
    print("🧪 Testing AIAnalysisRequest service field fix...")
    
    try:
        # Test data for a minimal analysis request
        test_data = {
            "audit_id": "72f7b6f6-ce78-41dd-a691-44d1ff8f7a01"  # Use a valid UUID format
        }
        
        print(f"📤 Sending test request to analysis endpoint...")
        print(f"📋 Request data: {json.dumps(test_data, indent=2)}")
        
        # Send request to start analysis
        response = requests.post(
            'http://127.0.0.1:8000/api/analysis/start',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Analysis request accepted!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ FAILED: Analysis request rejected")
            print(f"📋 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_ai_analysis_request_creation():
    """Test that AIAnalysisRequest can be created with service field"""
    print("\n🧪 Testing AIAnalysisRequest model creation...")
    
    try:
        # Add the backend directory to the path
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from backend.app.models.analysis import AIAnalysisRequest, LLMServiceType
        
        # Try to create an AIAnalysisRequest with the service field
        request = AIAnalysisRequest(
            query_id="test-query-id",
            persona_description="Test persona description",
            question_text="Test question text",
            model="openai-4o",
            service=LLMServiceType.OPENAI
        )
        
        print("✅ SUCCESS: AIAnalysisRequest created successfully!")
        print(f"📋 Request: {request.dict()}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR creating AIAnalysisRequest: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Analysis Fix Test Suite")
    print("=" * 40)
    
    # Test 1: Check if AIAnalysisRequest can be created
    test1_passed = test_ai_analysis_request_creation()
    
    # Test 2: Check if analysis endpoint accepts requests
    test2_passed = test_analysis_request()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"✅ AIAnalysisRequest creation: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Analysis endpoint: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.") 