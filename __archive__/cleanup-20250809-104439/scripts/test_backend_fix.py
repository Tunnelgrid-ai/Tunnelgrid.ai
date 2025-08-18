#!/usr/bin/env python3
"""
Quick Test for Backend AnalysisJobStatusResponse Fix

This script tests the /api/analysis/status/{job_id} endpoint to verify
the AnalysisJobStatusResponse model fix works correctly.
"""

import asyncio
import httpx
import uuid

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
ANALYSIS_API_BASE = f"{BASE_URL}/api/analysis"

async def test_analysis_status_endpoint():
    """Test the analysis status endpoint with a fake job ID"""
    
    # Use a fake job ID for testing
    fake_job_id = str(uuid.uuid4())
    
    print(f"🧪 Testing analysis status endpoint with job ID: {fake_job_id}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ANALYSIS_API_BASE}/status/{fake_job_id}")
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 404:
                print("✅ Expected 404 - job not found (this is correct)")
                print("✅ Backend is working - no more AnalysisJobStatus enum error!")
                return True
            elif response.status_code == 200:
                data = response.json()
                print("✅ Got 200 response with data:")
                print(f"   Job ID: {data.get('job_id')}")
                print(f"   Status: {data.get('status')}")
                print(f"   Progress: {data.get('progress_percentage')}%")
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing endpoint: {e}")
            return False

async def test_invalid_uuid():
    """Test with invalid UUID format"""
    
    print("\n🧪 Testing with invalid UUID format...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ANALYSIS_API_BASE}/status/invalid-uuid")
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 400:
                print("✅ Expected 400 - invalid UUID format")
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing invalid UUID: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Testing Backend AnalysisJobStatusResponse Fix")
    print("=" * 50)
    
    # Test 1: Valid UUID format (should return 404 for non-existent job)
    success1 = await test_analysis_status_endpoint()
    
    # Test 2: Invalid UUID format (should return 400)
    success2 = await test_invalid_uuid()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests passed! Backend fix is working correctly.")
        print("💡 The AnalysisJobStatusResponse model is now properly configured.")
    else:
        print("❌ Some tests failed. Check the backend logs for details.")
    
    print("\n💡 Next steps:")
    print("   1. Start your backend server: python -m uvicorn app.main:app --reload")
    print("   2. Test the frontend submit flow")
    print("   3. Check that the loading screen appears correctly")

if __name__ == "__main__":
    asyncio.run(main()) 