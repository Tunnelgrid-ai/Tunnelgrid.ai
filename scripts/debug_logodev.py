#!/usr/bin/env python3
"""
Debug script to test Logo.dev API key and identify the issue
"""

import os
import httpx
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

async def test_logodev_api():
    """Test Logo.dev API with different authentication methods"""
    
    api_key = os.getenv("LOGODEV_SECRET_KEY")
    print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")
    
    if api_key:
        # Mask API key for security (show first 10 and last 4 characters)
        if len(api_key) > 14:
            masked_key = api_key[:10] + "..." + api_key[-4:]
        else:
            masked_key = api_key[:4] + "..." + api_key[-2:]
        print(f"🔑 API Key (masked): {masked_key}")
    else:
        print("❌ No LOGODEV_SECRET_KEY found in environment variables")
        return
    
    # Test different authentication methods
    test_cases = [
        {
            "name": "Bearer Token with Colon (Correct format)",
            "headers": {"Authorization": f"Bearer: {api_key}"},
            "description": "Using Bearer: token in Authorization header (Logo.dev format)"
        },
        {
            "name": "Bearer Token (Old method)",
            "headers": {"Authorization": f"Bearer {api_key}"},
            "description": "Using Bearer token in Authorization header"
        },
        {
            "name": "API Key Header",
            "headers": {"X-API-Key": api_key},
            "description": "Using X-API-Key header"
        },
        {
            "name": "Authorization with API key",
            "headers": {"Authorization": api_key},
            "description": "Using API key directly in Authorization header"
        },
        {
            "name": "Query parameter",
            "headers": {},
            "url_suffix": f"&token={api_key}",
            "description": "Using API key as query parameter"
        }
    ]
    
    base_url = "https://api.logo.dev/search?q=apple"
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        try:
            url = base_url + test_case.get('url_suffix', '')
            headers = test_case['headers']
            
            timeout = httpx.Timeout(10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS! This authentication method works.")
                    try:
                        data = response.json()
                        print(f"   Response: {len(data)} results found")
                        if data and len(data) > 0:
                            print(f"   First result: {data[0].get('name', 'Unknown')}")
                        return test_case  # Return successful method
                    except:
                        print("   ✅ SUCCESS! But response is not JSON")
                        return test_case
                        
                elif response.status_code == 401:
                    print("   ❌ 401 Unauthorized - API key issue")
                    
                elif response.status_code == 403:
                    print("   ❌ 403 Forbidden - Authentication method issue")
                    
                else:
                    print(f"   ⚠️  Unexpected status: {response.status_code}")
                    
                # Print response body for debugging
                try:
                    response_text = response.text[:200]
                    print(f"   Response: {response_text}...")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🔍 All authentication methods failed. Possible issues:")
    print("   1. API key is invalid or expired")
    print("   2. Logo.dev API endpoint has changed")
    print("   3. Logo.dev requires different authentication")
    print("   4. Network connectivity issues")
    
    return None

async def test_alternative_endpoints():
    """Test alternative Logo.dev endpoints"""
    
    api_key = os.getenv("LOGODEV_SECRET_KEY")
    if not api_key:
        return
        
    endpoints = [
        "https://api.logo.dev/search?q=apple",
        "https://logo.dev/api/search?q=apple",
        "https://api.logodev.com/search?q=apple",
    ]
    
    print("\n🌐 Testing alternative endpoints...")
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing endpoint: {endpoint}")
        
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            timeout = httpx.Timeout(10.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(endpoint, headers=headers)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ This endpoint works!")
                    return endpoint
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Testing Logo.dev API Authentication")
    print("=" * 50)
    
    # Test current authentication method
    successful_method = asyncio.run(test_logodev_api())
    
    if not successful_method:
        # Test alternative endpoints
        working_endpoint = asyncio.run(test_alternative_endpoints())
        
        if not working_endpoint:
            print("\n💡 Troubleshooting suggestions:")
            print("   1. Check your Logo.dev dashboard for the correct API key format")
            print("   2. Verify your API key hasn't expired")
            print("   3. Check Logo.dev documentation for any recent changes")
            print("   4. Try regenerating your API key")
    else:
        print(f"\n🎉 Found working authentication method: {successful_method['name']}")
        print("💡 Update your backend code to use this method!") 