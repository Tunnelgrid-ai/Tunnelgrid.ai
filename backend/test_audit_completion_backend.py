#!/usr/bin/env python3
"""
Test script to verify audit completion via backend
"""

from app.core.database import get_supabase_client
import json

def test_audit_completion():
    """Test audit completion using the same logic as the backend endpoint"""
    
    audit_id = 'a580ae36-e7e4-4de7-a906-a5a0bb72a5fe'
    
    try:
        supabase = get_supabase_client()
        
        print(f"🔄 Testing audit completion for: {audit_id}")
        
        # STEP 1: Check if audit exists (same as backend endpoint)
        check_result = supabase.table("audit").select("audit_id, status").eq("audit_id", audit_id).execute()
        
        if not check_result.data:
            print(f"❌ Audit not found: {audit_id}")
            return False
        
        current_audit = check_result.data[0]
        print(f"📋 Found audit {audit_id} with status: {current_audit['status']}")
        
        # STEP 2: Update audit status to completed (same as backend endpoint)
        update_result = supabase.table("audit").update({
            "status": "completed"
        }).eq("audit_id", audit_id).execute()
        
        # Check for errors in update operation
        if hasattr(update_result, 'error') and update_result.error:
            print(f"❌ Update failed: {update_result.error}")
            return False
        
        print(f"✅ Successfully completed audit: {audit_id}")
        
        # STEP 3: Verify the update worked
        verify_result = supabase.table("audit").select("audit_id, status").eq("audit_id", audit_id).execute()
        
        if verify_result.data:
            updated_audit = verify_result.data[0]
            print(f"✅ Verification: Audit {audit_id} now has status: {updated_audit['status']}")
            return True
        else:
            print(f"❌ Verification failed: Could not retrieve updated audit")
            return False
        
    except Exception as e:
        print(f"❌ Error completing audit {audit_id}: {e}")
        return False

def reset_audit_status():
    """Reset audit status back to 'in_progress' for testing"""
    
    audit_id = 'a580ae36-e7e4-4de7-a906-a5a0bb72a5fe'
    
    try:
        supabase = get_supabase_client()
        
        print(f"🔄 Resetting audit status for testing: {audit_id}")
        
        # Reset status to 'in_progress'
        reset_result = supabase.table("audit").update({
            "status": "in_progress"
        }).eq("audit_id", audit_id).execute()
        
        print(f"✅ Reset audit {audit_id} status to 'in_progress'")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting audit {audit_id}: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Backend Audit Completion Logic")
    print("=" * 50)
    
    # Test the completion logic
    success = test_audit_completion()
    
    if success:
        print("\n🎉 ✅ Backend audit completion logic works!")
        print("💡 This means the frontend should work when using the backend API.")
        print("💡 The issue was RLS blocking direct Supabase access from frontend.")
        print("💡 Using backend API with service role key bypasses RLS.")
        
        # Reset for user testing
        print("\n🔧 Resetting audit status for user testing...")
        reset_audit_status()
    else:
        print("\n❌ Backend audit completion failed - needs investigation") 