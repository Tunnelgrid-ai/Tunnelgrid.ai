#!/usr/bin/env python3
"""
Test script to verify the workflow fix for brand search to setup flow
"""

import requests
import json
import time

def test_brand_search_flow():
    """Test the complete brand search to setup flow"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Brand Search to Setup Workflow")
    print("=" * 50)
    
    # Step 1: Test brand search
    print("\n1. Testing brand search...")
    search_response = requests.get(f"{base_url}/api/brand-search?q=Sohu")
    
    if search_response.status_code == 200:
        brands = search_response.json()
        print(f"✅ Found {len(brands)} brands")
        if brands:
            test_brand = brands[0]
            print(f"   Selected brand: {test_brand['name']} ({test_brand['domain']})")
        else:
            print("❌ No brands found")
            return
    else:
        print(f"❌ Brand search failed: {search_response.status_code}")
        return
    
    # Step 2: Test brand creation
    print("\n2. Testing brand creation...")
    create_data = {
        "brand_name": test_brand["name"],
        "domain": test_brand["domain"]
    }
    
    create_response = requests.post(
        f"{base_url}/api/brands/create",
        json=create_data,
        headers={"Content-Type": "application/json"}
    )
    
    if create_response.status_code == 200:
        create_result = create_response.json()
        brand_id = create_result.get("data", {}).get("brand_id")
        print(f"✅ Brand created with ID: {brand_id}")
    else:
        print(f"❌ Brand creation failed: {create_response.status_code}")
        print(f"   Response: {create_response.text}")
        return
    
    # Step 3: Test brand analysis
    print("\n3. Testing brand analysis...")
    analyze_data = {
        "brand_name": test_brand["name"],
        "domain": test_brand["domain"]
    }
    
    analyze_response = requests.post(
        f"{base_url}/api/brands/analyze",
        json=analyze_data,
        headers={"Content-Type": "application/json"}
    )
    
    if analyze_response.status_code == 200:
        analyze_result = analyze_response.json()
        description = analyze_result.get("description", "")
        products = analyze_result.get("product", [])
        print(f"✅ Brand analysis completed")
        print(f"   Description length: {len(description)} chars")
        print(f"   Products found: {len(products)}")
    else:
        print(f"❌ Brand analysis failed: {analyze_response.status_code}")
        print(f"   Response: {analyze_response.text}")
        return
    
    # Step 4: Test brand update
    print("\n4. Testing brand update...")
    update_data = {
        "brand_name": test_brand["name"],
        "brand_description": description,
        "product": products
    }
    
    update_response = requests.post(
        f"{base_url}/api/brands/update",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if update_response.status_code == 200:
        print("✅ Brand updated successfully")
    else:
        print(f"❌ Brand update failed: {update_response.status_code}")
        print(f"   Response: {update_response.text}")
        return
    
    print("\n✅ All backend API tests passed!")
    print("\n📝 Next steps:")
    print("1. Open the frontend application")
    print("2. Search for 'Sohu' in the brand search")
    print("3. Select the brand and click 'Go'")
    print("4. Verify you're taken to the brand setup wizard (not analysis screen)")
    print("5. Complete the setup flow normally")

if __name__ == "__main__":
    try:
        test_brand_search_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 