#!/usr/bin/env python3
"""
Test script to verify logo URL construction in brand search
"""

import asyncio
import httpx
import json
import os
from app.core.config import settings

async def test_logo_construction():
    """Test the logo URL construction logic"""
    
    # Mock brand data similar to what Logo.dev API returns
    mock_brands = [
        {"name": "Apple", "domain": "apple.com"},
        {"name": "Microsoft", "domain": "microsoft.com"},
        {"name": "Google", "domain": "google.com"},
        {"name": "Unknown Brand", "domain": "unknown.com"}
    ]
    
    api_key = settings.LOGODEV_SECRET_KEY or os.getenv("LOGODEV_SECRET_KEY")
    print(f"🔧 Using API key: {api_key}")
    
    # Test the logo URL construction logic
    formatted_brands = []
    for brand in mock_brands:
        domain = brand.get("domain", "unknown.com")
        formatted_brand = {
            "name": brand.get("name", "Unknown"),
            "domain": domain,
            # Use a reliable logo service that doesn't require authentication
            "logo": f"https://logo.clearbit.com/{domain}" if domain and domain != "unknown.com" else None
        }
        formatted_brands.append(formatted_brand)
    
    print("🎯 Formatted brands with logo URLs:")
    print(json.dumps(formatted_brands, indent=2))
    
    # Test one logo URL to see if it works
    if formatted_brands and formatted_brands[0]["logo"]:
        test_url = formatted_brands[0]["logo"]
        print(f"\n🧪 Testing logo URL: {test_url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(test_url)
                print(f"✅ Logo URL test - Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Logo image successfully retrieved ({len(response.content)} bytes)")
                else:
                    print(f"❌ Logo URL failed: {response.text}")
        except Exception as e:
            print(f"❌ Logo URL test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_logo_construction()) 