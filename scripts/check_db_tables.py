#!/usr/bin/env python3
"""
Check database tables
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import get_supabase_client

def check_tables():
    """Check what tables exist in the database"""
    print("🔍 Checking database tables...")
    
    try:
        supabase = get_supabase_client()
        
        # Try to query each table to see if it exists
        tables_to_check = [
            'audit', 'brands', 'products', 'personas', 'topics', 'questions',
            'user_studies', 'study_progress_snapshots', 'study_shares', 'study_templates'
        ]
        
        print("📊 Checking table existence:")
        existing_tables = []
        
        for table in tables_to_check:
            try:
                # Try to select from the table
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table}")
                existing_tables.append(table)
            except Exception as e:
                if "does not exist" in str(e) or "42P01" in str(e):
                    print(f"  ❌ {table} (does not exist)")
                else:
                    print(f"  ⚠️ {table} (error: {str(e)[:50]}...)")
        
        print(f"\n📈 Summary: {len(existing_tables)} out of {len(tables_to_check)} tables exist")
        
        # Check if study management tables exist
        study_tables = ['user_studies', 'study_progress_snapshots', 'study_shares', 'study_templates']
        missing_study_tables = [table for table in study_tables if table not in existing_tables]
        
        if missing_study_tables:
            print(f"\n❌ Missing study management tables: {', '.join(missing_study_tables)}")
        else:
            print(f"\n✅ All study management tables exist")
            
        # Check if core tables exist
        core_tables = ['audit', 'brands']
        missing_core_tables = [table for table in core_tables if table not in existing_tables]
        
        if missing_core_tables:
            print(f"❌ Missing core tables: {', '.join(missing_core_tables)}")
        else:
            print(f"✅ All core tables exist")
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    check_tables() 