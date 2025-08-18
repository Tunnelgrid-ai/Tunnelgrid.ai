#!/usr/bin/env python3
"""
Quick Manual Testing Script for Audit Flow

This script allows you to test the audit status flow manually
without going through the entire end-to-end process.

Usage:
    python scripts/test_audit_flow.py --audit-id YOUR_AUDIT_ID
    python scripts/test_audit_flow.py --create-test-audit
"""

import asyncio
import httpx
import uuid
import argparse
import json
from typing import Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
AUDIT_API_BASE = f"{BASE_URL}/api/audits"
ANALYSIS_API_BASE = f"{BASE_URL}/api/analysis"

class AuditFlowTester:
    """Manual tester for audit status flow"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def close(self):
        await self.client.aclose()
    
    async def create_test_audit(self) -> Optional[str]:
        """Create a test audit for testing"""
        print("🔧 Creating test audit...")
        
        try:
            # Create test brand first
            brand_data = {
                "brand_name": f"Test Brand {uuid.uuid4().hex[:8]}",
                "domain": "test-brand.com",
                "description": "Test brand for audit flow testing"
            }
            
            brand_response = await self.client.post(
                f"{BASE_URL}/api/brands/create",
                json=brand_data
            )
            
            if brand_response.status_code != 200:
                print(f"❌ Failed to create brand: {brand_response.text}")
                return None
            
            brand_result = brand_response.json()
            brand_id = brand_result.get("data", {}).get("brand_id")
            
            if not brand_id:
                print("❌ No brand_id in response")
                return None
            
            # Create test product
            product_data = {
                "brand_id": brand_id,
                "product_name": "Test Product"
            }
            
            product_response = await self.client.post(
                f"{BASE_URL}/api/products/create",
                json=product_data
            )
            
            if product_response.status_code != 200:
                print(f"❌ Failed to create product: {product_response.text}")
                return None
            
            product_result = product_response.json()
            product_id = product_result.get("data", {}).get("product_id")
            
            if not product_id:
                print("❌ No product_id in response")
                return None
            
            # Create audit
            audit_data = {
                "brand_id": brand_id,
                "product_id": product_id,
                "user_id": "72f7b6f6-ce78-41dd-a691-44d1ff8f7a01"  # Dev user ID
            }
            
            audit_response = await self.client.post(
                f"{AUDIT_API_BASE}/create",
                json=audit_data
            )
            
            if audit_response.status_code != 200:
                print(f"❌ Failed to create audit: {audit_response.text}")
                return None
            
            audit_result = audit_response.json()
            audit_id = audit_result.get("data", {}).get("audit_id")
            
            if audit_id:
                print(f"✅ Created test audit: {audit_id}")
                return audit_id
            else:
                print("❌ No audit_id in response")
                return None
                
        except Exception as e:
            print(f"💥 Error creating test audit: {e}")
            return None
    
    async def test_mark_setup_complete(self, audit_id: str) -> bool:
        """Test marking setup as complete"""
        print(f"1️⃣ Testing mark-setup-complete for audit: {audit_id}")
        
        try:
            response = await self.client.put(
                f"{AUDIT_API_BASE}/{audit_id}/mark-setup-complete"
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('message', 'Unknown')}")
                print(f"   📊 Status: {data.get('data', {}).get('status', 'unknown')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   💥 Error: {e}")
            return False
    
    async def test_start_analysis(self, audit_id: str) -> Optional[str]:
        """Test starting analysis (requires queries to exist)"""
        print(f"2️⃣ Testing analysis start for audit: {audit_id}")
        
        try:
            response = await self.client.post(
                f"{ANALYSIS_API_BASE}/start",
                json={"audit_id": audit_id}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                print(f"   ✅ Success: {data.get('message', 'Unknown')}")
                print(f"   📊 Job ID: {job_id}")
                print(f"   📊 Total Queries: {data.get('total_queries', 0)}")
                return job_id
            else:
                print(f"   ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"   💥 Error: {e}")
            return None
    
    async def test_complete_audit(self, audit_id: str) -> bool:
        """Test completing audit after analysis"""
        print(f"3️⃣ Testing complete-audit for audit: {audit_id}")
        
        try:
            response = await self.client.put(
                f"{AUDIT_API_BASE}/{audit_id}/complete"
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data.get('message', 'Unknown')}")
                print(f"   📊 Status: {data.get('data', {}).get('status', 'unknown')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   💥 Error: {e}")
            return False
    
    async def get_audit_status(self, audit_id: str) -> Optional[dict]:
        """Get current audit status"""
        try:
            response = await self.client.get(f"{AUDIT_API_BASE}/{audit_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get audit status: {response.text}")
                return None
                
        except Exception as e:
            print(f"💥 Error getting audit status: {e}")
            return None
    
    async def test_complete_flow(self, audit_id: str):
        """Test the complete audit status flow"""
        print(f"🧪 Testing complete audit flow for: {audit_id}")
        print("=" * 60)
        
        # Step 1: Mark setup as complete
        setup_success = await self.test_mark_setup_complete(audit_id)
        if not setup_success:
            print("❌ Setup completion failed, stopping test")
            return
        
        print()
        
        # Step 2: Start analysis (this will update status to analysis_running)
        job_id = await self.test_start_analysis(audit_id)
        if not job_id:
            print("⚠️  Analysis start failed (this is expected if no queries exist)")
            print("   You can still test the complete-audit endpoint manually")
        
        print()
        
        # Step 3: Check current status
        print("📊 Checking current audit status...")
        status_data = await self.get_audit_status(audit_id)
        if status_data:
            current_status = status_data.get("status", "unknown")
            print(f"   Current status: {current_status}")
        
        print()
        
        # Step 4: Test complete audit (this would normally be called by backend)
        print("💡 Note: The complete-audit endpoint is normally called by the backend")
        print("   when analysis finishes. You can test it manually here:")
        await self.test_complete_audit(audit_id)
        
        print()
        print("✅ Audit flow test completed!")

async def main():
    parser = argparse.ArgumentParser(description="Test audit status flow")
    parser.add_argument("--audit-id", help="Audit ID to test with")
    parser.add_argument("--create-test-audit", action="store_true", help="Create a test audit")
    parser.add_argument("--test-flow", action="store_true", help="Test the complete flow")
    
    args = parser.parse_args()
    
    tester = AuditFlowTester()
    
    try:
        if args.create_test_audit:
            audit_id = await tester.create_test_audit()
            if audit_id:
                print(f"\n🎉 Test audit created: {audit_id}")
                print(f"💡 Use this ID to test the flow: --audit-id {audit_id}")
            else:
                print("❌ Failed to create test audit")
            return
        
        if not args.audit_id:
            print("❌ Please provide an audit ID with --audit-id or use --create-test-audit")
            return
        
        if args.test_flow:
            await tester.test_complete_flow(args.audit_id)
        else:
            # Test individual endpoints
            print("🧪 Testing individual endpoints...")
            await tester.test_mark_setup_complete(args.audit_id)
            print()
            await tester.test_start_analysis(args.audit_id)
            print()
            await tester.test_complete_audit(args.audit_id)
    
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main()) 