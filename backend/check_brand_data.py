#!/usr/bin/env python3
"""
Check brand extraction data in the database
"""

from app.core.database import get_supabase_client

def check_brand_data():
    print("🔍 Checking brand extraction data...")
    
    supabase = get_supabase_client()
    
    # Check brand extractions
    try:
        result = supabase.table('brand_extractions').select('*').limit(10).execute()
        print(f"\n📊 Found {len(result.data)} brand extractions:")
        for i, extraction in enumerate(result.data[:5]):
            print(f"  {i+1}. Brand: '{extraction['extracted_brand_name']}'")
            print(f"     Target: {extraction['is_target_brand']}")
            print(f"     Sentiment: {extraction.get('sentiment_label', 'N/A')}")
            print(f"     Response ID: {extraction.get('response_id', 'N/A')}")
            print()
    except Exception as e:
        print(f"❌ Error checking brand extractions: {e}")
    
    # Check brand table structure
    try:
        brand_result = supabase.table('brand').select('*').limit(1).execute()
        if brand_result.data:
            print(f"\n🏢 Brand table structure:")
            brand = brand_result.data[0]
            for key, value in brand.items():
                print(f"  {key}: {value}")
            print()
    except Exception as e:
        print(f"❌ Error checking brand table: {e}")
    
    # Check audit data with brand info
    try:
        audit_result = supabase.table('audit').select('*, brand:brand_id(*)').limit(5).execute()
        print(f"\n📋 Found {len(audit_result.data)} audits:")
        for audit in audit_result.data:
            print(f"  Audit ID: {audit['audit_id']}")
            print(f"  Brand ID: {audit.get('brand_id', 'N/A')}")
            if audit.get('brand'):
                print(f"  Brand Name: '{audit['brand'].get('name', 'N/A')}'")
                print(f"  Brand Website: {audit['brand'].get('website', 'N/A')}")
            print()
    except Exception as e:
        print(f"❌ Error checking audits: {e}")

if __name__ == "__main__":
    check_brand_data()
