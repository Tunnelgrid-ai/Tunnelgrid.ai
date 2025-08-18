"""
Fix the trigger function issue that's causing the 'audit_id' field error
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def fix_trigger_function():
    """Fix the invalidate_metrics_cache function to handle tables without audit_id"""
    
    print("🔧 Fixing trigger function issue...")
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Read the SQL fix
    with open("scripts/fix_trigger_function.sql", "r") as f:
        sql_fix = f.read()
    
    try:
        print("📝 Executing trigger function fix...")
        
        # Execute the SQL fix
        result = supabase.rpc("exec_sql", {"sql": sql_fix}).execute()
        
        print("✅ Trigger function fixed successfully!")
        print("🎯 The analysis should now work without the 'audit_id' field error")
        
    except Exception as e:
        print(f"❌ Failed to execute SQL fix: {e}")
        print("\n📋 Manual Fix Required:")
        print("1. Go to your Supabase SQL Editor")
        print("2. Copy and paste the contents of scripts/fix_trigger_function.sql")
        print("3. Execute the SQL")
        print("4. Try running the analysis again")

if __name__ == "__main__":
    fix_trigger_function()

