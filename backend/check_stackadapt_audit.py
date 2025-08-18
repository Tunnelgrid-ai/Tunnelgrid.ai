#!/usr/bin/env python3
"""
Check for StackAdapt audit and its topics
"""

from app.core.database import get_supabase_client

def check_stackadapt_audit():
    supabase = get_supabase_client()
    
    print("🔍 Looking for StackAdapt audit...")
    
    # First, find StackAdapt brand
    brand_result = supabase.table('brand').select('*').eq('brand_name', 'StackAdapt').execute()
    if not brand_result.data:
        print("❌ StackAdapt brand not found in database")
        return
    
    stackadapt_brand = brand_result.data[0]
    print(f"✅ Found StackAdapt brand: {stackadapt_brand.get('brand_id')}")
    
    # Find audits for StackAdapt
    audit_result = supabase.table('audit').select('*').eq('brand_id', stackadapt_brand.get('brand_id')).execute()
    if not audit_result.data:
        print("❌ No audits found for StackAdapt")
        return
    
    print(f"📊 Found {len(audit_result.data)} audit(s) for StackAdapt:")
    
    for audit in audit_result.data:
        audit_id = audit.get('audit_id')
        print(f"\n🔍 Audit ID: {audit_id}")
        
        # Get product name
        product_result = supabase.table('product').select('product_name').eq('product_id', audit.get('product_id')).execute()
        product_name = product_result.data[0].get('product_name') if product_result.data else 'Unknown'
        print(f"  Product: {product_name}")
        
        # Check topics for this audit
        topics_result = supabase.table('topics').select('*').eq('audit_id', audit_id).execute()
        if topics_result.data:
            print(f"  📋 Topics ({len(topics_result.data)}):")
            for topic in topics_result.data:
                print(f"    - {topic.get('topic_name', 'Unknown')} ({topic.get('topic_category', 'Unknown')})")
        else:
            print("  📋 No topics found")
        
        # Check if this is the most recent audit
        print(f"  📅 Created: {audit.get('created_at', 'Unknown')}")

if __name__ == "__main__":
    check_stackadapt_audit()
