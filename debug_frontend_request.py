#!/usr/bin/env python3
"""
Debug script to capture and analyze the frontend request
"""

import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import requests

class DebugRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/questions/generate':
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print("🔍 INTERCEPTED FRONTEND REQUEST:")
            print("="*60)
            print(f"Path: {self.path}")
            print(f"Headers: {dict(self.headers)}")
            print(f"Body Length: {content_length}")
            
            try:
                request_json = json.loads(post_data.decode('utf-8'))
                print("📋 REQUEST JSON:")
                print(json.dumps(request_json, indent=2))
                
                # Compare with working Postman request
                print("\n🔍 ANALYSIS:")
                print(f"Brand Name: {request_json.get('brandName', 'MISSING')}")
                print(f"Product Name: {request_json.get('productName', 'MISSING')}")
                print(f"Audit ID: {request_json.get('auditId', 'MISSING')}")
                print(f"Topics Count: {len(request_json.get('topics', []))}")
                print(f"Personas Count: {len(request_json.get('personas', []))}")
                
                if request_json.get('personas'):
                    print("\n👥 PERSONAS:")
                    for i, persona in enumerate(request_json['personas']):
                        print(f"  {i+1}. {persona.get('name', 'NO_NAME')} (ID: {persona.get('id', 'NO_ID')})")
                
                if request_json.get('topics'):
                    print("\n📚 TOPICS:")
                    for i, topic in enumerate(request_json['topics']):
                        print(f"  {i+1}. {topic.get('name', 'NO_NAME')} (ID: {topic.get('id', 'NO_ID')})")
                
                # Forward to real backend
                print("\n📤 Forwarding to real backend...")
                response = requests.post(
                    "http://localhost:8000/api/questions/generate",
                    json=request_json,
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                print(f"📋 Backend Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"✅ Success: {response_data.get('success')}")
                    print(f"📊 Questions Count: {len(response_data.get('questions', []))}")
                    print(f"📊 Source: {response_data.get('source')}")
                    
                    if response_data.get('source') == 'fallback':
                        print(f"⚠️ FALLBACK REASON: {response_data.get('reason')}")
                    
                    # Return the response to frontend
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(response.content)
                else:
                    print(f"❌ Backend Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    
                    self.send_response(response.status_code)
                    self.end_headers()
                    self.wfile.write(response.content)
                
            except Exception as e:
                print(f"❌ Error processing request: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"error": "Debug proxy error"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def start_debug_proxy():
    print("🔍 Starting debug proxy on http://localhost:8001")
    print("📋 Configure frontend to use http://localhost:8001 instead of http://localhost:8000")
    print("⏹️ Press Ctrl+C to stop")
    
    server = HTTPServer(('localhost', 8001), DebugRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Debug proxy stopped")
        server.shutdown()

if __name__ == "__main__":
    start_debug_proxy() 