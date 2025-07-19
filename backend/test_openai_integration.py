#!/usr/bin/env python3
"""
OpenAI Web Search Integration Test Script

This script tests the OpenAI GPT-4o search preview integration
for the brand analysis feature.
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8000/api/brands"
TEST_BRAND = {
    "brand_name": "Apple",
    "domain": "apple.com"
}

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message: str, status: str = "info"):
    """Print colored status messages"""
    color = Colors.BLUE
    if status == "success":
        color = Colors.GREEN
    elif status == "error":
        color = Colors.RED
    elif status == "warning":
        color = Colors.YELLOW
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

async def test_configuration():
    """Test basic server connectivity"""
    print_status("🔧 Testing server connectivity...", "info")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            
        if response.status_code == 200:
            print_status("✅ Server is running", "success")
            return True
        else:
            print_status(f"❌ Server connectivity test failed: {response.status_code}", "error")
            return False
            
    except Exception as e:
        print_status(f"❌ Server connectivity test error: {e}", "error")
        return False



async def test_brand_analysis():
    """Test the complete brand analysis flow"""
    print_status("🔍 Testing brand analysis with web search...", "info")
    
    try:
        # Test the analyze endpoint
        async with httpx.AsyncClient(timeout=90.0) as client:  # Longer timeout for web search
            print_status(f"   Analyzing brand: {TEST_BRAND['brand_name']}", "info")
            
            response = await client.post(
                f"{BASE_URL}/analyze",
                json=TEST_BRAND,
                headers={"Content-Type": "application/json"}
            )
            
        if response.status_code == 200:
            result = response.json()
            print_status("✅ Brand analysis completed successfully", "success")
            
            description = result.get("description", "")
            products = result.get("product", [])
            
            print_status(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}", "info")
            print_status(f"   Products ({len(products)}): {', '.join(products[:3])}{'...' if len(products) > 3 else ''}", "info")
            
            # Validate response structure
            if description and products and isinstance(products, list):
                print_status("✅ Response structure is valid", "success")
                return True
            else:
                print_status("❌ Invalid response structure", "error")
                return False
                
        else:
            error_text = response.text
            print_status(f"❌ Brand analysis failed: {response.status_code}", "error")
            print_status(f"   Error: {error_text}", "error")
            return False
            
    except httpx.TimeoutException:
        print_status("❌ Brand analysis timed out (this is expected for web search)", "warning")
        print_status("   Try increasing timeout or check OpenAI API response time", "info")
        return False
    except Exception as e:
        print_status(f"❌ Brand analysis error: {e}", "error")
        return False

async def test_logo_search():
    """Test logo search functionality"""
    print_status("🎨 Testing logo search...", "info")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/search?q={TEST_BRAND['brand_name']}")
            
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                print_status(f"✅ Logo search returned {len(results)} results", "success")
                first_result = results[0]
                print_status(f"   First result: {first_result.get('name')} ({first_result.get('domain')})", "info")
                return True
            else:
                print_status("⚠️ Logo search returned empty results", "warning")
                return False
        else:
            print_status(f"❌ Logo search failed: {response.status_code}", "error")
            return False
            
    except Exception as e:
        print_status(f"❌ Logo search error: {e}", "error")
        return False

async def main():
    """Run all tests"""
    print_status("🚀 Starting OpenAI Web Search Integration Tests", "info")
    print_status("=" * 60, "info")
    
    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{BASE_URL}/health")
    except:
        print_status("❌ Backend server is not running!", "error")
        print_status("   Please start the server with: python -m uvicorn app.main:app --reload", "info")
        return
    
    tests = [
        ("Server Connectivity", test_configuration),
        ("Brand Analysis", test_brand_analysis),
        ("Logo Search", test_logo_search)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_status(f"\n📋 Running {test_name} Test", "info")
        print_status("-" * 40, "info")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"❌ {test_name} test failed with exception: {e}", "error")
            results.append((test_name, False))
    
    # Summary
    print_status("\n📊 Test Results Summary", "info")
    print_status("=" * 60, "info")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print_status(f"   {test_name}: {status}", "success" if result else "error")
    
    print_status(f"\nOverall: {passed}/{total} tests passed", "success" if passed == total else "warning")
    
    if passed == total:
        print_status("🎉 All tests passed! OpenAI web search integration is working correctly.", "success")
    else:
        print_status("⚠️ Some tests failed. Check the error messages above.", "warning")

if __name__ == "__main__":
    asyncio.run(main()) 