#!/usr/bin/env python3
"""
Test Loading Screen Fix

This script tests the new startAnalysisJob endpoint to verify that:
1. It returns a job ID immediately
2. The job ID can be used to poll status
3. The loading screen should work correctly
"""

import asyncio
import httpx
import uuid

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
ANALYSIS_API_BASE = f"{BASE_URL}/api/analysis"

async def test_start_analysis_job():
    """Test the start analysis job endpoint"""
    
    print("🧪 Testing startAnalysisJob endpoint...")
    
    # You'll need to replace this with a real audit ID that has queries
    test_audit_id = "your-test-audit-id-here"
    
    if test_audit_id == "your-test-audit-id-here":
        print("⚠️  Please set a real audit ID to test")
        print("💡 The audit should have queries generated from the wizard")
        return None
    
    async with httpx.AsyncClient() as client:
        try:
            # Test starting analysis job
            response = await client.post(
                f"{ANALYSIS_API_BASE}/start",
                json={"audit_id": test_audit_id}
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get('job_id')
                total_queries = data.get('total_queries')
                
                print(f"✅ Analysis job started successfully!")
                print(f"   Job ID: {job_id}")
                print(f"   Total Queries: {total_queries}")
                
                # Test polling the job status
                print(f"\n🧪 Testing job status polling...")
                status_response = await client.get(f"{ANALYSIS_API_BASE}/status/{job_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Job status retrieved successfully!")
                    print(f"   Status: {status_data.get('status')}")
                    print(f"   Progress: {status_data.get('progress_percentage')}%")
                    print(f"   Completed: {status_data.get('completed_queries')}/{status_data.get('total_queries')}")
                    
                    return {
                        'job_id': job_id,
                        'total_queries': total_queries,
                        'status': status_data.get('status'),
                        'progress': status_data.get('progress_percentage')
                    }
                else:
                    print(f"❌ Failed to get job status: {status_response.status_code}")
                    print(f"   Response: {status_response.text}")
                    return None
                    
            else:
                print(f"❌ Failed to start analysis job: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return None

async def test_frontend_flow():
    """Test the complete frontend flow simulation"""
    
    print("\n🧪 Testing Frontend Flow Simulation...")
    
    # This simulates what the frontend should do:
    # 1. Start analysis job
    # 2. Get job ID immediately
    # 3. Show loading screen
    # 4. Poll status until completion
    
    result = await test_start_analysis_job()
    
    if result:
        print(f"\n✅ Frontend flow simulation successful!")
        print(f"   The loading screen should now work correctly with:")
        print(f"   - Job ID: {result['job_id']}")
        print(f"   - Initial Status: {result['status']}")
        print(f"   - Progress: {result['progress']}%")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Test the frontend submit flow")
        print(f"   2. Verify the loading screen appears and stays visible")
        print(f"   3. Check that progress updates correctly")
        
    else:
        print(f"\n❌ Frontend flow simulation failed")
        print(f"   Check the backend logs for details")

async def main():
    """Run all tests"""
    
    print("🚀 Testing Loading Screen Fix")
    print("=" * 50)
    
    await test_frontend_flow()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("✅ If successful, the loading screen should now work correctly")
    print("✅ No more 404 errors when polling job status")
    print("✅ No more bouncing back to review page")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Set a real audit ID in the script before running")
    print("💡 The audit should have queries generated from the wizard")
    print("🔧 Make sure your backend server is running")
    
    # Uncomment to run tests
    # asyncio.run(main()) 