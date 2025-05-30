#!/usr/bin/env python3
"""
Complete setup test for AI Brand Analysis Backend
This script will start the server and test all endpoints
"""

import os
import sys
import time
import subprocess
import requests
import json
from threading import Thread

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting server...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    os.chdir(backend_dir)
    
    # Start server
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return process

def test_endpoints():
    """Test all endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing endpoints...")
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(10)
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Root Endpoint", f"{base_url}/"),
        ("Personas Fallback", f"{base_url}/api/personas/fallback"),
        ("OpenAPI Schema", f"{base_url}/openapi.json")
    ]
    
    results = {}
    
    for test_name, url in tests:
        try:
            print(f"\n🔍 Testing {test_name}...")
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if test_name == "OpenAPI Schema":
                    paths = list(data.get('paths', {}).keys())
                    personas_paths = [p for p in paths if '/personas' in p]
                    print(f"Total paths: {len(paths)}")
                    print(f"Personas paths: {personas_paths}")
                    results[test_name] = {"status": "✅ PASS", "personas_paths": personas_paths}
                else:
                    print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                    results[test_name] = {"status": "✅ PASS", "data": data}
            else:
                print(f"❌ FAIL: {response.text}")
                results[test_name] = {"status": "❌ FAIL", "error": response.text}
                
        except Exception as e:
            print(f"❌ FAIL: {e}")
            results[test_name] = {"status": "❌ FAIL", "error": str(e)}
    
    return results

def main():
    print("🔧 AI Brand Analysis Backend - Complete Setup Test")
    print("=" * 60)
    
    # Start server
    server_process = start_server()
    
    try:
        # Test endpoints
        results = test_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            print(f"{test_name}: {result['status']}")
            if 'personas_paths' in result:
                print(f"  Personas paths found: {result['personas_paths']}")
        
        # Check if personas endpoints are working
        personas_working = any('personas' in str(result.get('personas_paths', [])) for result in results.values())
        
        if personas_working:
            print("\n🎉 SUCCESS: Personas endpoints are working!")
        else:
            print("\n❌ ISSUE: Personas endpoints are not working properly")
            
    finally:
        # Stop server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main() 