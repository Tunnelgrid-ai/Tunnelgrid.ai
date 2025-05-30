#!/usr/bin/env python3
"""
AI Brand Analysis Project Reorganization Script

This script will:
1. Clean up duplicate files and directories
2. Organize test files
3. Fix the server startup issues
4. Test the personas endpoints
"""

import os
import shutil
import subprocess
import sys
import time
import json
from pathlib import Path

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print(f"{'='*60}")

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("AI Brand Analysis Project Reorganization")
    print("This script will clean up and fix your project structure")
    
    # Get project root
    project_root = Path.cwd()
    backend_dir = project_root / "backend"
    
    print(f"Project root: {project_root}")
    print(f"Backend directory: {backend_dir}")
    
    # Step 1: Clean up duplicate files
    print_step(1, "CLEANING UP DUPLICATE FILES")
    
    # Remove old main.py if it exists
    old_main = backend_dir / "main.py"
    if old_main.exists():
        print(f"Removing duplicate main.py: {old_main}")
        old_main.unlink()
    
    # Remove duplicate venv directories
    for venv_path in [project_root / "venv", backend_dir / "venv"]:
        if venv_path.exists():
            print(f"Removing duplicate venv: {venv_path}")
            shutil.rmtree(venv_path, ignore_errors=True)
    
    # Remove __pycache__ directories
    for cache_dir in [backend_dir / "__pycache__", backend_dir / "app" / "__pycache__"]:
        if cache_dir.exists():
            print(f"Removing cache: {cache_dir}")
            shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Step 2: Organize test files
    print_step(2, "ORGANIZING TEST FILES")
    
    tests_dir = backend_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    # Move test files
    test_files = list(backend_dir.glob("test_*.py")) + list(backend_dir.glob("debug_*.py"))
    test_files.extend([
        backend_dir / "simple_test.py",
        backend_dir / "manual_server.py",
        backend_dir / "diagnose.py"
    ])
    
    for test_file in test_files:
        if test_file.exists():
            dest = tests_dir / test_file.name
            print(f"Moving {test_file.name} to tests/")
            shutil.move(str(test_file), str(dest))
    
    # Step 3: Create proper startup script
    print_step(3, "CREATING STARTUP SCRIPT")
    
    startup_script = project_root / "start_backend.py"
    startup_content = '''#!/usr/bin/env python3
"""
AI Brand Analysis Backend Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("Starting AI Brand Analysis Backend...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print(f"Working directory: {backend_dir}")
    print(f"Server will be available at: http://127.0.0.1:8000")
    print(f"API Documentation: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
'''
    
    with open(startup_script, 'w', encoding='utf-8') as f:
        f.write(startup_content)
    
    print(f"Created startup script: {startup_script}")
    
    # Step 4: Create test script
    print_step(4, "CREATING TEST SCRIPT")
    
    test_script = project_root / "test_backend.py"
    test_content = '''#!/usr/bin/env python3
"""
AI Brand Analysis Backend Test Script
"""

import requests
import json
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing AI Brand Analysis Backend...")
    print("Waiting for server to start...")
    time.sleep(5)
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Root Endpoint", f"{base_url}/"),
        ("Personas Fallback", f"{base_url}/api/personas/fallback"),
        ("OpenAPI Schema", f"{base_url}/openapi.json")
    ]
    
    for test_name, url in tests:
        try:
            print(f"\\nTesting {test_name}...")
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                if test_name == "OpenAPI Schema":
                    data = response.json()
                    paths = list(data.get('paths', {}).keys())
                    personas_paths = [p for p in paths if '/personas' in p]
                    print(f"Personas endpoints found: {personas_paths}")
                    if personas_paths:
                        print("SUCCESS: Personas endpoints are working!")
                    else:
                        print("ISSUE: Personas endpoints not found!")
                else:
                    print("SUCCESS: Endpoint working!")
            else:
                print(f"FAILED: {response.text}")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_endpoints()
'''
    
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"Created test script: {test_script}")
    
    # Step 5: Test the setup
    print_step(5, "TESTING THE SETUP")
    
    print("Checking if Python and dependencies are available...")
    
    # Test Python
    success, stdout, stderr = run_command("python --version")
    if success:
        print(f"Python: {stdout.strip()}")
    else:
        print(f"Python not found: {stderr}")
        return
    
    # Test FastAPI import
    success, stdout, stderr = run_command('python -c "import fastapi; print(f\\"FastAPI {fastapi.__version__}\\")"', cwd=backend_dir)
    if success:
        print(f"FastAPI: {stdout.strip()}")
    else:
        print(f"FastAPI not available: {stderr}")
        print("Try: pip install fastapi uvicorn")
        return
    
    # Test app import
    success, stdout, stderr = run_command('python -c "import app; print(\\"App module available\\")"', cwd=backend_dir)
    if success:
        print(f"App module: {stdout.strip()}")
    else:
        print(f"App module not available: {stderr}")
        return
    
    print("\\nPROJECT REORGANIZATION COMPLETE!")
    print("\\nNEXT STEPS:")
    print("1. Run: python start_backend.py")
    print("2. In another terminal, run: python test_backend.py")
    print("3. Check http://127.0.0.1:8000/docs for API documentation")
    print("4. Test personas endpoint: http://127.0.0.1:8000/api/personas/fallback")

if __name__ == "__main__":
    main()