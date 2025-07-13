#!/usr/bin/env python3

from app.core.database import get_supabase_client
import json

def check_audit():
    supabase = get_supabase_client()
    
    # Check if the specific audit exists
    audit_id = 'a580ae36-e7e4-4de7-a906-a5a0bb72a5fe'
    print(f'🔍 Checking for audit: {audit_id}')
    
    result = supabase.table('audit').select('*').eq('audit_id', audit_id).execute()
    
    if result.data:
        print('✅ Audit found:')
        print(json.dumps(result.data[0], indent=2, default=str))
        return True
    else:
        print('❌ Audit not found')
        print('🔍 Checking all audits in database...')
        
        all_audits = supabase.table('audit').select('audit_id, status, created_timestamp').execute()
        
        if all_audits.data:
            print(f'📋 Found {len(all_audits.data)} audit(s):')
            for audit in all_audits.data[:10]:  # Show first 10
                print(f'  - {audit["audit_id"]} | {audit["status"]} | {audit["created_timestamp"]}')
        else:
            print('📋 No audits found in database')
        return False

if __name__ == "__main__":
    check_audit() 