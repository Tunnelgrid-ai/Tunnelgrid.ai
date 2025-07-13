#!/usr/bin/env python3
"""
Live UUID Validation Test
Tests the running server to verify error handling improvements
"""

import requests
import uuid
import json

def test_invalid_uuid():
    """Test that invalid UUID returns 400"""
    print("🧪 Testing invalid UUID format...")
    
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/analysis/start',
            json={'audit_id': 'invalid-uuid-format'},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✅ SUCCESS: Invalid UUID correctly returns 400")
            return True
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_valid_uuid_not_found():
    """Test that valid UUID but non-existent audit returns 404"""
    print("\n🧪 Testing valid UUID but non-existent audit...")
    
    try:
        fake_uuid = str(uuid.uuid4())
        response = requests.post(
            'http://127.0.0.1:8000/api/analysis/start',
            json={'audit_id': fake_uuid},
            timeout=5
        )
        
        print(f"UUID: {fake_uuid}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("✅ SUCCESS: Valid UUID not found correctly returns 404")
            return True
        else:
            print(f"❌ FAIL: Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_status_endpoint():
    """Test status endpoint UUID validation"""
    print("\n🧪 Testing status endpoint UUID validation...")
    
    try:
        response = requests.get(
            'http://127.0.0.1:8000/api/analysis/status/invalid-uuid-format',
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✅ SUCCESS: Status endpoint correctly validates UUID")
            return True
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 Testing Live UUID Validation")
    print("="*50)
    
    tests = [
        ("Invalid UUID Format", test_invalid_uuid),
        ("Valid UUID Not Found", test_valid_uuid_not_found), 
        ("Status Endpoint Validation", test_status_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All UUID validation improvements are working!")
        print("\n✨ Benefits confirmed:")
        print("   - HTTP 400 for invalid UUID format")
        print("   - HTTP 404 for valid UUID but not found")
        print("   - Clear error messages")
        print("   - No more database exceptions")
    else:
        print("⚠️ Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 