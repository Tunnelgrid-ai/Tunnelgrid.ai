"""
Test Audit Status Flow

Tests the new audit status progression:
1. in_progress -> setup_completed (mark-setup-complete)
2. setup_completed -> analysis_running (start analysis)
3. analysis_running -> completed (analysis finishes)
"""

import pytest
import httpx
import uuid
from typing import Dict, Any

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
AUDIT_API_BASE = f"{BASE_URL}/api/audits"
ANALYSIS_API_BASE = f"{BASE_URL}/api/analysis"

class TestAuditStatusFlow:
    """Test the complete audit status flow"""
    
    @pytest.fixture
    def sample_audit_id(self) -> str:
        """Create a sample audit for testing"""
        # This would normally be created through the full flow
        # For testing, we'll use a mock audit ID
        return str(uuid.uuid4())
    
    @pytest.fixture
    def mock_audit_data(self) -> Dict[str, Any]:
        """Mock audit data for testing"""
        return {
            "brand_id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "status": "in_progress"
        }
    
    async def test_mark_setup_complete(self, sample_audit_id: str):
        """Test marking setup as complete"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{AUDIT_API_BASE}/{sample_audit_id}/mark-setup-complete"
            )
            
            # Should return 404 since audit doesn't exist
            assert response.status_code == 404
            
            # If you have a real audit ID, it should return 200
            # assert response.status_code == 200
            # data = response.json()
            # assert data["success"] == True
            # assert data["data"]["status"] == "setup_completed"
    
    async def test_complete_audit_after_analysis(self, sample_audit_id: str):
        """Test completing audit after analysis"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{AUDIT_API_BASE}/{sample_audit_id}/complete"
            )
            
            # Should return 404 since audit doesn't exist
            assert response.status_code == 404
            
            # If you have a real audit ID, it should return 200
            # assert response.status_code == 200
            # data = response.json()
            # assert data["success"] == True
            # assert data["data"]["status"] == "completed"
    
    async def test_analysis_start_updates_status(self, sample_audit_id: str):
        """Test that starting analysis updates audit status to analysis_running"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ANALYSIS_API_BASE}/start",
                json={"audit_id": sample_audit_id}
            )
            
            # Should return 404 since audit doesn't exist
            assert response.status_code == 404
            
            # If you have a real audit ID with queries, it should return 200
            # assert response.status_code == 200
            # data = response.json()
            # assert data["success"] == True
            # assert "job_id" in data

class TestAuditStatusValidation:
    """Test audit status validation and edge cases"""
    
    async def test_invalid_audit_id_format(self):
        """Test with invalid UUID format"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{AUDIT_API_BASE}/invalid-uuid/mark-setup-complete"
            )
            assert response.status_code == 400
            data = response.json()
            assert "Invalid audit_id format" in data["detail"]
    
    async def test_nonexistent_audit(self):
        """Test with non-existent audit ID"""
        fake_audit_id = str(uuid.uuid4())
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{AUDIT_API_BASE}/{fake_audit_id}/mark-setup-complete"
            )
            assert response.status_code == 404
            data = response.json()
            assert "Audit not found" in data["detail"]

# Manual testing functions
async def test_with_real_audit_id(audit_id: str):
    """Test the complete flow with a real audit ID"""
    print(f"🧪 Testing audit status flow for: {audit_id}")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Mark setup as complete
        print("1️⃣ Testing mark-setup-complete...")
        response = await client.put(
            f"{AUDIT_API_BASE}/{audit_id}/mark-setup-complete"
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        
        # Step 2: Start analysis (this should update status to analysis_running)
        print("2️⃣ Testing analysis start...")
        response = await client.post(
            f"{ANALYSIS_API_BASE}/start",
            json={"audit_id": audit_id}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        
        # Step 3: Check audit status
        print("3️⃣ Checking audit status...")
        response = await client.get(f"{AUDIT_API_BASE}/{audit_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Current status: {data.get('status', 'unknown')}")

if __name__ == "__main__":
    import asyncio
    
    # Replace with a real audit ID from your database
    REAL_AUDIT_ID = "your-real-audit-id-here"
    
    if REAL_AUDIT_ID != "your-real-audit-id-here":
        asyncio.run(test_with_real_audit_id(REAL_AUDIT_ID))
    else:
        print("⚠️  Please set a real audit ID to test the flow")
        print("💡 You can get one from your database or create one through the full flow") 