#!/usr/bin/env python3
"""
Check topics and audit details for a specific audit
"""

from app.core.database import get_supabase_client

def check_audit_topics():
    supabase = get_supabase_client()
    audit_id = 'b461e0a0-2593-4639-8edf-1a168e3f1d8d'
    
    print(f"🔍 Checking audit: {audit_id}")
    
    # Check topics for this audit
    topics_result = supabase.table('topics').select('*').eq('audit_id', audit_id).execute()
    print(f"\n📋 Topics for audit {audit_id}:")
    if topics_result.data:
        for topic in topics_result.data:
            print(f"  - {topic.get('topic_name', 'Unknown')} ({topic.get('topic_category', 'Unknown')})")
    else:
        print("  No topics found")
    
    # Check the audit details
    audit_result = supabase.table('audit').select('*').eq('audit_id', audit_id).execute()
    if audit_result.data:
        audit = audit_result.data[0]
        print(f"\n📊 Audit details:")
        print(f"  - Audit ID: {audit.get('audit_id')}")
        print(f"  - Brand ID: {audit.get('brand_id')}")
        print(f"  - Product ID: {audit.get('product_id')}")
        
        # Get brand name
        brand_result = supabase.table('brand').select('brand_name').eq('brand_id', audit.get('brand_id')).execute()
        if brand_result.data:
            print(f"  - Brand Name: {brand_result.data[0].get('brand_name')}")
        
        # Get product name
        product_result = supabase.table('product').select('product_name').eq('product_id', audit.get('product_id')).execute()
        if product_result.data:
            print(f"  - Product Name: {product_result.data[0].get('product_name')}")

if __name__ == "__main__":
    check_audit_topics()
