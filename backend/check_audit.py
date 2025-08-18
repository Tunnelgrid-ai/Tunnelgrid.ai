#!/usr/bin/env python3

from app.core.database import get_supabase_client
import json

def check_audit():
    supabase = get_supabase_client()
    
    # Check the specific audit
    audit_id = '09829033-7f1a-4317-8a73-80b03a099dad'
    print(f'🔍 Checking for audit: {audit_id}')
    
    result = supabase.table('audit').select('*').eq('audit_id', audit_id).execute()
    
    if result.data:
        print('✅ Audit found:')
        print(json.dumps(result.data[0], indent=2, default=str))
    else:
        print('❌ Audit not found')
    
    # Find completed audits
    print('\n🔍 Checking for completed audits...')
    completed_audits = supabase.table('audit').select('audit_id, status, created_timestamp').eq('status', 'completed').limit(5).execute()
    
    if completed_audits.data:
        print(f'✅ Found {len(completed_audits.data)} completed audit(s):')
        for audit in completed_audits.data:
            print(f'  - {audit["audit_id"]} | {audit["status"]} | {audit["created_timestamp"]}')
    else:
        print('❌ No completed audits found')
    
    # Show all audit statuses
    print('\n🔍 All audits in database:')
    all_audits = supabase.table('audit').select('audit_id, status, created_timestamp').limit(10).execute()
    
    if all_audits.data:
        print(f'📋 Found {len(all_audits.data)} audit(s):')
        for audit in all_audits.data:
            print(f'  - {audit["audit_id"]} | {audit["status"]} | {audit["created_timestamp"]}')
    else:
        print('📋 No audits found in database')

if __name__ == "__main__":
    check_audit() 