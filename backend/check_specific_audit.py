#!/usr/bin/env python3
"""
Check specific audit and brand data
"""

from app.core.database import get_supabase_client

def check_specific_audit():
    print("🔍 Checking specific audit data...")
    
    supabase = get_supabase_client()
    
    # Check the most recent audit
    try:
        audit_result = supabase.table('audit').select('*').order('updated_at', desc=True).limit(1).execute()
        if audit_result.data:
            audit = audit_result.data[0]
            print(f"\n📋 Most recent audit:")
            print(f"  Audit ID: {audit['audit_id']}")
            print(f"  Brand ID: {audit.get('brand_id', 'N/A')}")
            print(f"  Updated: {audit.get('updated_at', 'N/A')}")
            
            # Get the brand details
            if audit.get('brand_id'):
                brand_result = supabase.table('brand').select('*').eq('brand_id', audit['brand_id']).execute()
                if brand_result.data:
                    brand = brand_result.data[0]
                    print(f"\n🏢 Associated brand:")
                    print(f"  Brand ID: {brand['brand_id']}")
                    print(f"  Brand Name: '{brand['brand_name']}'")
                    print(f"  Domain: {brand.get('domain', 'N/A')}")
                    print(f"  Description: {brand.get('brand_description', 'N/A')}")
                else:
                    print(f"\n❌ No brand found for brand_id: {audit['brand_id']}")
            
            # Check brand extractions for this audit
            print(f"\n🔍 Checking brand extractions for this audit...")
            # Get queries for this audit
            queries_result = supabase.table('queries').select('query_id').eq('audit_id', audit['audit_id']).execute()
            if queries_result.data:
                query_ids = [q['query_id'] for q in queries_result.data]
                print(f"  Found {len(query_ids)} queries for this audit")
                
                # Get responses for these queries
                responses_result = supabase.table('responses').select('response_id').in_('query_id', query_ids).execute()
                if responses_result.data:
                    response_ids = [r['response_id'] for r in responses_result.data]
                    print(f"  Found {len(response_ids)} responses for these queries")
                    
                    # Get brand extractions for these responses
                    extractions_result = supabase.table('brand_extractions').select('*').in_('response_id', response_ids).execute()
                    if extractions_result.data:
                        print(f"  Found {len(extractions_result.data)} brand extractions:")
                        for extraction in extractions_result.data[:5]:
                            print(f"    - '{extraction['extracted_brand_name']}' (Target: {extraction['is_target_brand']})")
                    else:
                        print(f"  No brand extractions found")
                else:
                    print(f"  No responses found")
            else:
                print(f"  No queries found for this audit")
                
                # Check if there are any brand extractions at all
                print(f"\n🔍 Checking all brand extractions...")
                all_extractions = supabase.table('brand_extractions').select('*').limit(10).execute()
                if all_extractions.data:
                    print(f"  Found {len(all_extractions.data)} total brand extractions:")
                    for extraction in all_extractions.data[:5]:
                        print(f"    - '{extraction['extracted_brand_name']}' (Target: {extraction['is_target_brand']})")
                        print(f"      Query ID: {extraction.get('query_id', 'N/A')}")
                        
                        # Get the audit for this query
                        query_result = supabase.table('queries').select('audit_id').eq('query_id', extraction['query_id']).execute()
                        if query_result.data:
                            query_audit_id = query_result.data[0]['audit_id']
                            print(f"      Audit ID: {query_audit_id}")
                            
                            # Get the brand for this audit
                            audit_result = supabase.table('audit').select('brand_id').eq('audit_id', query_audit_id).execute()
                            if audit_result.data:
                                audit_brand_id = audit_result.data[0]['brand_id']
                                brand_result = supabase.table('brand').select('brand_name').eq('brand_id', audit_brand_id).execute()
                                if brand_result.data:
                                    print(f"      Expected Brand: '{brand_result.data[0]['brand_name']}'")
                                else:
                                    print(f"      Expected Brand: Unknown (brand_id: {audit_brand_id})")
                else:
                    print(f"  No brand extractions found in database")
        else:
            print(f"❌ No audits found")
    except Exception as e:
        print(f"❌ Error checking audit: {e}")

if __name__ == "__main__":
    check_specific_audit()
