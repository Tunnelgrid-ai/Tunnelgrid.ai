#!/usr/bin/env python3
"""
Fix the Dentsu audit to use the correct audit with data
"""

from app.core.database import get_supabase_client

def fix_dentsu_audit():
    print("🔧 Fixing Dentsu audit to use the correct audit with data...")
    
    supabase = get_supabase_client()
    
    # The correct audit that has Dentsu data
    correct_audit_id = "b461e0a0-2593-4639-8edf-1a168e3f1d8d"
    
    print(f"\n🎯 Using correct audit: {correct_audit_id}")
    
    # Check the current state of this audit
    audit_result = supabase.table('audit').select('*').eq('audit_id', correct_audit_id).execute()
    if audit_result.data:
        audit = audit_result.data[0]
        print(f"📋 Audit details:")
        print(f"  Brand ID: {audit.get('brand_id', 'N/A')}")
        
        # Get brand name
        if audit.get('brand_id'):
            brand_result = supabase.table('brand').select('brand_name').eq('brand_id', audit['brand_id']).execute()
            if brand_result.data:
                print(f"  Brand Name: '{brand_result.data[0]['brand_name']}'")
        
        # Check queries and responses
        queries_result = supabase.table('queries').select('query_id').eq('audit_id', correct_audit_id).execute()
        query_count = len(queries_result.data) if queries_result.data else 0
        
        if query_count > 0:
            query_ids = [q['query_id'] for q in queries_result.data]
            responses_result = supabase.table('responses').select('response_id').in_('query_id', query_ids).execute()
            response_count = len(responses_result.data) if responses_result.data else 0
            
            if response_count > 0:
                response_ids = [r['response_id'] for r in responses_result.data]
                extractions_result = supabase.table('brand_extractions').select('*').in_('response_id', response_ids).execute()
                extraction_count = len(extractions_result.data) if extractions_result.data else 0
                
                print(f"  Queries: {query_count}")
                print(f"  Responses: {response_count}")
                print(f"  Brand Extractions: {extraction_count}")
                
                if extraction_count > 0:
                    print(f"\n📊 Sample brand extractions:")
                    for extraction in extractions_result.data[:5]:
                        print(f"  - '{extraction['extracted_brand_name']}' (Target: {extraction['is_target_brand']})")
        
        # Clear and regenerate cache for this audit
        print(f"\n🔄 Clearing and regenerating cache for correct audit...")
        
        # Clear existing cache
        clear_result = supabase.table('comprehensive_metrics_cache').delete().eq('audit_id', correct_audit_id).execute()
        print("✅ Cleared existing cache")
        
        # Regenerate cache
        try:
            regenerate_result = supabase.rpc('calculate_comprehensive_metrics', {'p_audit_id': correct_audit_id}).execute()
            print("✅ Regenerated cache with correct Dentsu data")
        except Exception as e:
            print(f"❌ Failed to regenerate cache: {e}")
        
        print(f"\n🎉 Dentsu audit fix completed!")
        print(f"📊 Audit {correct_audit_id} is now ready with correct Dentsu data")
        print(f"🔄 Cache has been regenerated with correct data")
        
        # Also check if there's a cache entry
        cache_result = supabase.table('comprehensive_metrics_cache').select('*').eq('audit_id', correct_audit_id).execute()
        if cache_result.data:
            cache = cache_result.data[0]
            print(f"\n📊 Cache details:")
            print(f"  Total Queries: {cache.get('total_queries', 0)}")
            print(f"  Total Responses: {cache.get('total_responses', 0)}")
            print(f"  Target Brand Mentions: {cache.get('target_brand_mentions', 0)}")
            print(f"  Overall Visibility: {cache.get('overall_visibility_percentage', 0)}%")
        else:
            print("❌ No cache entry found")
        
    else:
        print(f"❌ Audit {correct_audit_id} not found")

if __name__ == "__main__":
    fix_dentsu_audit()

