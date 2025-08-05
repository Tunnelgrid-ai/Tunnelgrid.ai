#!/usr/bin/env python3
"""
Test script for studies endpoint
"""

import requests
import json

def test_studies_endpoint():
    """Test the studies endpoint"""
    
    base_url = "http://localhost:8000"
    
    # Test list studies
    print("Testing GET /api/studies...")
    try:
        response = requests.get(f"{base_url}/api/studies")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('studies', []))} studies")
            print(f"Total count: {data.get('total_count', 0)}")
            
            # Print first study if exists
            if data.get('studies'):
                study = data['studies'][0]
                print(f"First study: {study.get('study_name', 'N/A')} (ID: {study.get('study_id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_studies_endpoint() 