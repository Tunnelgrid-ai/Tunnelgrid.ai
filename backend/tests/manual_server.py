#!/usr/bin/env python3
"""
Manual server startup script for debugging
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Manual Server Startup")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

try:
    print("📦 Importing FastAPI...")
    from fastapi import FastAPI
    
    print("📦 Importing app modules...")
    from app.main import app
    
    print("📦 Importing uvicorn...")
    import uvicorn
    
    print("✅ All imports successful!")
    print("🌐 Starting server on http://127.0.0.1:8000")
    print("🔄 Use Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the backend directory and virtual environment is activated")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 