#!/usr/bin/env python3
"""
Diagnostic script to identify issues with the server setup
"""

import sys
import os

print("🔍 DIAGNOSTIC REPORT")
print("=" * 50)

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

print("\n📦 CHECKING IMPORTS...")

# Test basic imports
try:
    import fastapi
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")

try:
    import pydantic
    print("✅ Pydantic imported successfully")
except ImportError as e:
    print(f"❌ Pydantic import failed: {e}")

# Test app imports
print("\n🏗️ CHECKING APP IMPORTS...")

try:
    import app
    print("✅ App module imported successfully")
except ImportError as e:
    print(f"❌ App module import failed: {e}")

try:
    from app.main import app as fastapi_app
    print("✅ FastAPI app imported successfully")
    
    # Check routes
    routes = []
    for route in fastapi_app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    print(f"📍 Total routes: {len(routes)}")
    print(f"📍 All routes: {routes}")
    
    personas_routes = [r for r in routes if '/personas' in r]
    print(f"📍 Personas routes: {personas_routes}")
    
    if personas_routes:
        print("✅ Personas routes are registered!")
    else:
        print("❌ Personas routes are NOT registered!")
        
except ImportError as e:
    print(f"❌ FastAPI app import failed: {e}")

try:
    from app.routes.personas import router as personas_router
    print(f"✅ Personas router imported successfully")
    print(f"📍 Personas router has {len(personas_router.routes)} routes")
except ImportError as e:
    print(f"❌ Personas router import failed: {e}")

print("\n🔧 RECOMMENDATIONS:")
if 'fastapi' not in sys.modules:
    print("- Install FastAPI: pip install fastapi")
if 'uvicorn' not in sys.modules:
    print("- Install Uvicorn: pip install uvicorn")
if 'app' not in sys.modules:
    print("- Check app module structure")

print("\n✅ Diagnostic complete!") 