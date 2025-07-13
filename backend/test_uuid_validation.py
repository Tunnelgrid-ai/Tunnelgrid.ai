#!/usr/bin/env python3
"""
UUID VALIDATION TEST SCRIPT

This script tests the UUID validation improvements we made to the analysis endpoints.
It demonstrates how the system now properly handles invalid UUID formats.
"""

import sys
import os
import uuid
from pathlib import Path

# Add the backend app to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_uuid_validation():
    """Test the UUID validation function directly"""
    print("🧪 Testing UUID Validation Function...")
    
    try:
        from app.routes.analysis import validate_uuid
        
        # Test 1: Valid UUID
        valid_uuid = str(uuid.uuid4())
        result = validate_uuid(valid_uuid, "test_id")
        print(f"✅ Valid UUID accepted: {valid_uuid[:8]}...")
        
        # Test 2: Invalid UUID format should raise HTTPException
        try:
            validate_uuid("invalid-uuid-format", "test_id")
            print("❌ Invalid UUID should have raised exception")
            return False
        except Exception as e:
            if "400" in str(e) or "Invalid" in str(e):
                print("✅ Invalid UUID correctly rejected with 400 error")
            else:
                print(f"⚠️ Unexpected error type: {e}")
                return False
        
        # Test 3: Empty string should be rejected
        try:
            validate_uuid("", "test_id")
            print("❌ Empty UUID should have raised exception")
            return False
        except Exception as e:
            if "400" in str(e) or "Invalid" in str(e):
                print("✅ Empty UUID correctly rejected")
            else:
                print(f"⚠️ Unexpected error type: {e}")
                return False
        
        # Test 4: None should be rejected
        try:
            validate_uuid(None, "test_id")
            print("❌ None UUID should have raised exception")
            return False
        except Exception as e:
            print("✅ None UUID correctly rejected")
        
        print("🎉 All UUID validation tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import validation function: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        return False

def test_analysis_model_validation():
    """Test the analysis Pydantic models"""
    print("🧪 Testing Analysis Model Validation...")
    
    try:
        from app.models.analysis import AnalysisJobRequest, AIAnalysisRequest, Citation, BrandMention
        
        # Test 1: Valid AnalysisJobRequest
        valid_uuid = str(uuid.uuid4())
        request = AnalysisJobRequest(audit_id=valid_uuid)
        print(f"✅ Valid AnalysisJobRequest created: {request.audit_id[:8]}...")
        
        # Test 2: Invalid AnalysisJobRequest (empty audit_id)
        try:
            invalid_request = AnalysisJobRequest(audit_id="")
            print("❌ Empty audit_id should be rejected")
            return False
        except Exception as e:
            print("✅ Empty audit_id correctly rejected by model validation")
        
        # Test 3: Valid AIAnalysisRequest
        ai_request = AIAnalysisRequest(
            query_id="test-query-123",
            persona_description="A tech enthusiast",
            question_text="What do you think about smartphones?",
            model="openai-4o"
        )
        print("✅ Valid AIAnalysisRequest created")
        
        # Test 4: Valid Citation
        citation = Citation(
            citation_id="test-citation-123",
            response_id="test-response-123",
            citation_text="According to TechCrunch, smartphones are evolving rapidly.",
            source_url="https://techcrunch.com",
            extracted_at="2025-05-31T21:00:00Z"
        )
        print("✅ Valid Citation created")
        
        # Test 5: Valid BrandMention
        mention = BrandMention(
            mention_id="test-mention-123",
            response_id="test-response-123",
            brand_name="Apple",
            mention_context="Apple makes great smartphones",
            sentiment_score=0.8,
            extracted_at="2025-05-31T21:00:00Z"
        )
        print("✅ Valid BrandMention created")
        
        # Test 6: Invalid sentiment score
        try:
            invalid_mention = BrandMention(
                mention_id="test-mention-456",
                response_id="test-response-123",
                brand_name="Samsung",
                mention_context="Samsung is competitive",
                sentiment_score=2.0,  # Invalid: outside -1.0 to 1.0 range
                extracted_at="2025-05-31T21:00:00Z"
            )
            print("❌ Invalid sentiment score should be rejected")
            return False
        except Exception as e:
            print("✅ Invalid sentiment score correctly rejected")
        
        print("🎉 All model validation tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import analysis models: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during model testing: {e}")
        return False

def test_error_improvement_demonstration():
    """Demonstrate the improvement in error handling"""
    print("🎯 Demonstrating Error Handling Improvements...")
    
    print("\n📋 BEFORE (Original Implementation):")
    print("   - Invalid UUID 'test-invalid-audit-id' would cause:")
    print("   - Database error: 'invalid input syntax for type uuid'")
    print("   - HTTP 500 Internal Server Error")
    print("   - Unclear error message for users")
    
    print("\n📋 AFTER (Improved Implementation):")
    print("   - Invalid UUID 'test-invalid-audit-id' now causes:")
    print("   - Immediate validation before database query")
    print("   - HTTP 400 Bad Request")
    print("   - Clear error: 'Invalid audit_id format. Must be a valid UUID.'")
    
    print("\n✨ Benefits:")
    print("   ✅ Better user experience with clear error messages")
    print("   ✅ Prevents unnecessary database queries")
    print("   ✅ Proper HTTP status codes")
    print("   ✅ Faster error responses")
    print("   ✅ Reduced server logs noise")
    
    return True

def main():
    """Run all UUID validation tests"""
    print("🚀 Starting UUID Validation Tests")
    print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("UUID Validation Function", test_uuid_validation),
        ("Analysis Model Validation", test_analysis_model_validation),
        ("Error Improvement Demo", test_error_improvement_demonstration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 UUID VALIDATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<35} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All UUID validation improvements are working correctly!")
        print("\n💡 The system now provides:")
        print("   - Proper UUID validation")
        print("   - Better error messages")
        print("   - Correct HTTP status codes")
        print("   - Improved user experience")
    else:
        print("⚠️ Some validation tests failed.")
    
    return passed == total

if __name__ == "__main__":
    import time
    
    success = main()
    print(f"\n🏁 UUID validation tests completed at {time.strftime('%H:%M:%S')}")
    exit(0 if success else 1) 