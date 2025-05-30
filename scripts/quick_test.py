#!/usr/bin/env python3
"""
Quick test to check if personas endpoints are working
"""

import requests
import json

def test_personas_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    print("Quick Test: Checking Personas Endpoints")
    print("=" * 50)
    
    # Test endpoints
    endpoints_to_test = [
        ("Server Health", f"{base_url}/health"),
        ("OpenAPI Schema", f"{base_url}/openapi.json"),
        ("Personas Fallback", f"{base_url}/api/personas/fallback"),
        ("Personas Store (should be 405/422, not 404)", f"{base_url}/api/personas/store")
    ]
    
    for test_name, url in endpoints_to_test:
        try:
            print(f"\nTesting: {test_name}")
            print(f"URL: {url}")
            
            # Use GET for all tests to see what happens
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if test_name == "OpenAPI Schema" and response.status_code == 200:
                # Check if personas endpoints are in the schema
                schema = response.json()
                paths = list(schema.get('paths', {}).keys())
                personas_paths = [p for p in paths if '/personas' in p]
                print(f"Available personas endpoints: {personas_paths}")
                
                if personas_paths:
                    print("SUCCESS: Personas endpoints found in API schema!")
                else:
                    print("ISSUE: No personas endpoints found in API schema")
                    print("Available endpoints:", paths)
            
            elif response.status_code == 404:
                print("ISSUE: 404 Not Found - endpoint doesn't exist")
            elif response.status_code == 405:
                print("GOOD: 405 Method Not Allowed - endpoint exists but wrong method")
            elif response.status_code == 422:
                print("GOOD: 422 Validation Error - endpoint exists but missing data")
            elif response.status_code == 200:
                print("SUCCESS: Endpoint working!")
                if len(response.text) < 200:
                    print(f"Response: {response.text}")
            else:
                print(f"Response: {response.status_code} - {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: Cannot connect to server. Is it running on port 8000?")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_personas_endpoints() 