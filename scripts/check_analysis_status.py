"""
Check the current analysis status for a specific audit
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend directory
load_dotenv("backend/.env")

def check_analysis_status(audit_id: str):
    """Check the current analysis status for a specific audit"""
    
    print(f"🔍 Checking analysis status for audit: {audit_id}")
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    try:
        # Check analysis job status
        job_result = supabase.table("analysis_jobs").select("*").eq("audit_id", audit_id).execute()
        
        if not job_result.data:
            print("❌ No analysis job found for this audit")
            return
        
        job = job_result.data[0]
        
        print(f"📊 Analysis Job Status:")
        print(f"   Job ID: {job['job_id']}")
        print(f"   Status: {job['status']}")
        print(f"   Total Queries: {job['total_queries']}")
        print(f"   Completed Queries: {job['completed_queries']}")
        print(f"   Failed Queries: {job['failed_queries']}")
        print(f"   Progress: {job['progress_percentage']:.1f}%")
        
        if job['error_message']:
            print(f"   Error: {job['error_message']}")
        
        if job['status'] == 'completed':
            print("✅ Analysis is completed! You can view the report now.")
        elif job['status'] == 'running':
            print("⏳ Analysis is still running. Please wait for completion.")
        elif job['status'] == 'failed':
            print("❌ Analysis failed. Check the error message above.")
        elif job['status'] == 'partial_failure':
            print("⚠️ Analysis completed with partial failures.")
        
        # Check if there are any responses
        queries_result = supabase.table("queries").select("query_id").eq("audit_id", audit_id).execute()
        if queries_result.data:
            query_ids = [q["query_id"] for q in queries_result.data]
            responses_result = supabase.table("responses").select("response_id").in_("query_id", query_ids).execute()
            print(f"   Responses generated: {len(responses_result.data)}")
        
    except Exception as e:
        print(f"❌ Error checking analysis status: {e}")

if __name__ == "__main__":
    # Use the audit ID from the error message
    audit_id = "91e7128e-77b0-4233-a7a6-9a96b990e106"
    check_analysis_status(audit_id)
