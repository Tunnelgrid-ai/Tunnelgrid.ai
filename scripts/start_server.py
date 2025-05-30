#!/usr/bin/env python3
"""
Simple server startup script for AI Brand Analysis
This script starts the FastAPI application from the correct directory
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting AI Brand Analysis Backend...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, 'backend')
    
    # Check if backend directory exists
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return 1
    
    # Change to backend directory and start server
    try:
        os.chdir(backend_dir)
        print(f"📂 Changed to directory: {backend_dir}")
        
        # Start the server
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
        print(f"🎯 Running: {' '.join(cmd)}")
        
        # Start the server process
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 