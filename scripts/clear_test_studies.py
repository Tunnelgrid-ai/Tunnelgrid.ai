#!/usr/bin/env python3
"""
Clear Test Studies Script
Clears all test studies from the database to remove dummy reports
"""

import requests
import json
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def clear_test_studies():
    print("🧹 Clearing all test studies from database...")
    
    try:
        # Get all studies first
        response = requests.get('http://127.0.0.1:8000/api/studies?page_size=100')
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch studies: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return
        
        studies_data = response.json()
        studies = studies_data.get('studies', [])
        
        if not studies:
            print("✅ No studies found to clear")
            return
        
        print(f"📊 Found {len(studies)} studies")
        
        # Delete each study
        deleted_count = 0
        for study in studies:
            study_id = study.get('study_id')
            study_name = study.get('study_name', 'Unknown')
            
            print(f"🗑️ Deleting study: {study_name} ({study_id})")
            
            delete_response = requests.delete(f'http://127.0.0.1:8000/api/studies/{study_id}')
            
            if delete_response.status_code == 200:
                print(f"✅ Successfully deleted: {study_name}")
                deleted_count += 1
            else:
                print(f"❌ Failed to delete {study_name}: {delete_response.status_code}")
                print(f"❌ Response: {delete_response.text}")
        
        print(f"\n🎉 Successfully deleted {deleted_count} out of {len(studies)} studies")
        
    except Exception as e:
        print(f"❌ Error clearing studies: {e}")

def clear_by_database_query():
    """Alternative method: Clear directly from database"""
    print("🗄️ Clearing studies directly from database...")
    
    try:
        from backend.app.core.database import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Get all audits (studies)
        result = supabase.table("audit").select("*").execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"❌ Error fetching audits: {result.error}")
            return
        
        audits = result.data
        print(f"📊 Found {len(audits)} audits in database")
        
        if not audits:
            print("✅ No audits found to clear")
            return
        
        # Delete all audits
        delete_result = supabase.table("audit").delete().neq("audit_id", "").execute()
        
        if hasattr(delete_result, 'error') and delete_result.error:
            print(f"❌ Error deleting audits: {delete_result.error}")
        else:
            print(f"✅ Successfully cleared all {len(audits)} audits from database")
            
    except ImportError:
        print("❌ Could not import database modules. Make sure backend is properly set up.")
    except Exception as e:
        print(f"❌ Error clearing from database: {e}")

if __name__ == "__main__":
    print("🧹 Test Studies Cleanup Tool")
    print("=" * 40)
    
    # Try API method first
    print("\n1️⃣ Attempting to clear via API...")
    clear_test_studies()
    
    # Try database method as backup
    print("\n2️⃣ Attempting to clear via database...")
    clear_by_database_query()
    
    print("\n✅ Cleanup complete!") 