#!/usr/bin/env python3
"""
Debug script to test imports and identify issues
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🔍 Debugging imports...")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

try:
    print("\n1. Testing app module import...")
    import app
    print("✅ app module imported successfully")
    
    print("\n2. Testing app.main import...")
    import app.main
    print("✅ app.main imported successfully")
    
    print("\n3. Testing personas router import...")
    from app.routes.personas import router as personas_router
    print(f"✅ personas router imported successfully")
    print(f"Personas router has {len(personas_router.routes)} routes")
    
    print("\n4. Testing main app creation...")
    from app.main import app as main_app
    print("✅ main app imported successfully")
    
    # Test if personas routes are included
    all_routes = []
    for route in main_app.routes:
        if hasattr(route, 'path'):
            all_routes.append(route.path)
    
    personas_routes = [route for route in all_routes if '/personas' in route]
    print(f"\n5. Routes in main app:")
    print(f"Total routes: {len(all_routes)}")
    print(f"All routes: {all_routes}")
    print(f"Personas routes: {personas_routes}")
    
    if personas_routes:
        print("✅ Personas routes are properly registered!")
    else:
        print("❌ Personas routes are NOT registered!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc() 