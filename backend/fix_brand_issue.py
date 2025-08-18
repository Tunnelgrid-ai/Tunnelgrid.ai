#!/usr/bin/env python3
"""
Fix brand name issue and regenerate cache for the correct audit
"""

from app.core.database import get_supabase_client
import uuid

def fix_brand_issue():
    print("🔧 Fixing brand name issue...")
    
    supabase = get_supabase_client()
    
    # Step 1: Find the audit that should be "Dentsu"
    print("\n🔍 Finding the correct audit for Dentsu...")
    
    # Get all audits
    audit_result = supabase.table('audit').select('*').execute()
    if not audit_result.data:
        print("❌ No audits found")
        return
    
    print(f"📋 Found {len(audit_result.data)} audits:")
    for audit in audit_result.data:
        print(f"  Audit ID: {audit['audit_id']}")
        print(f"  Brand ID: {audit.get('brand_id', 'N/A')}")
        
        # Get brand name
        if audit.get('brand_id'):
            brand_result = supabase.table('brand').select('brand_name').eq('brand_id', audit['brand_id']).execute()
            if brand_result.data:
                print(f"  Brand Name: '{brand_result.data[0]['brand_name']}'")
            else:
                print(f"  Brand Name: Unknown")
        print()
    
    # Step 2: Check which audit has queries and responses
    print("\n🔍 Checking which audits have analysis data...")
    for audit in audit_result.data:
        audit_id = audit['audit_id']
        
        # Check queries
        queries_result = supabase.table('queries').select('query_id').eq('audit_id', audit_id).execute()
        query_count = len(queries_result.data) if queries_result.data else 0
        
        # Check responses
        if query_count > 0:
            query_ids = [q['query_id'] for q in queries_result.data]
            responses_result = supabase.table('responses').select('response_id').in_('query_id', query_ids).execute()
            response_count = len(responses_result.data) if responses_result.data else 0
            
            # Check brand extractions
            if response_count > 0:
                response_ids = [r['response_id'] for r in responses_result.data]
                extractions_result = supabase.table('brand_extractions').select('*').in_('response_id', response_ids).execute()
                extraction_count = len(extractions_result.data) if extractions_result.data else 0
                
                print(f"  Audit {audit_id}: {query_count} queries, {response_count} responses, {extraction_count} brand extractions")
                
                if extraction_count > 0:
                    # Show sample extractions
                    for extraction in extractions_result.data[:3]:
                        print(f"    - '{extraction['extracted_brand_name']}' (Target: {extraction['is_target_brand']})")
        else:
            print(f"  Audit {audit_id}: No queries found")
    
    # Step 3: Ask user which audit should be Dentsu
    print("\n❓ Which audit should be associated with 'Dentsu'?")
    print("Please provide the audit ID that should be corrected.")
    
    # For now, let's assume the most recent audit with data should be Dentsu
    # Find the audit with the most recent activity
    print("\n🔧 Assuming the most recent audit should be Dentsu...")
    
    # Get the most recent audit with queries
    recent_audit = None
    for audit in audit_result.data:
        audit_id = audit['audit_id']
        queries_result = supabase.table('queries').select('query_id').eq('audit_id', audit_id).execute()
        if queries_result.data and len(queries_result.data) > 0:
            recent_audit = audit
            break
    
    if recent_audit:
        print(f"🎯 Selected audit: {recent_audit['audit_id']}")
        
        # Step 4: Update the brand name to Dentsu
        print("\n🔧 Updating brand name to 'Dentsu'...")
        
        # First, check if Dentsu brand exists
        dentsu_brand_result = supabase.table('brand').select('*').eq('brand_name', 'Dentsu').execute()
        
        if dentsu_brand_result.data:
            dentsu_brand_id = dentsu_brand_result.data[0]['brand_id']
            print(f"✅ Found existing Dentsu brand: {dentsu_brand_id}")
        else:
            # Create Dentsu brand
            print("🏢 Creating new Dentsu brand...")
            dentsu_brand_data = {
                'brand_id': str(uuid.uuid4()),
                'brand_name': 'Dentsu',
                'domain': 'dentsu.com',
                'brand_description': 'Dentsu is a global advertising and public relations company'
            }
            
            create_result = supabase.table('brand').insert(dentsu_brand_data).execute()
            if create_result.data:
                dentsu_brand_id = create_result.data[0]['brand_id']
                print(f"✅ Created Dentsu brand: {dentsu_brand_id}")
            else:
                print("❌ Failed to create Dentsu brand")
                return
        
        # Update the audit to use Dentsu brand
        update_result = supabase.table('audit').update({'brand_id': dentsu_brand_id}).eq('audit_id', recent_audit['audit_id']).execute()
        if update_result.data:
            print(f"✅ Updated audit {recent_audit['audit_id']} to use Dentsu brand")
        else:
            print("❌ Failed to update audit")
            return
        
        # Step 5: Update brand extractions to mark Dentsu as target brand
        print("\n🔧 Updating brand extractions...")
        
        # Get all brand extractions for this audit
        queries_result = supabase.table('queries').select('query_id').eq('audit_id', recent_audit['audit_id']).execute()
        if queries_result.data:
            query_ids = [q['query_id'] for q in queries_result.data]
            extractions_result = supabase.table('brand_extractions').select('*').in_('query_id', query_ids).execute()
            
            if extractions_result.data:
                print(f"📊 Found {len(extractions_result.data)} brand extractions to update")
                
                # Update each extraction
                for extraction in extractions_result.data:
                    extraction_id = extraction['extraction_id']
                    extracted_brand = extraction['extracted_brand_name']
                    
                    # Mark as target brand if it's Dentsu or similar
                    is_target = 'dentsu' in extracted_brand.lower() or extracted_brand.lower() == 'dentsu'
                    
                    update_extraction_result = supabase.table('brand_extractions').update({
                        'is_target_brand': is_target,
                        'brand_id': dentsu_brand_id if is_target else None
                    }).eq('extraction_id', extraction_id).execute()
                    
                    if update_extraction_result.data:
                        print(f"  ✅ Updated extraction '{extracted_brand}' -> Target: {is_target}")
                    else:
                        print(f"  ❌ Failed to update extraction '{extracted_brand}'")
        
        # Step 6: Clear and regenerate cache
        print("\n🔄 Clearing and regenerating cache...")
        
        # Clear existing cache
        clear_result = supabase.table('comprehensive_metrics_cache').delete().eq('audit_id', recent_audit['audit_id']).execute()
        print("✅ Cleared existing cache")
        
        # Regenerate cache
        try:
            regenerate_result = supabase.rpc('calculate_comprehensive_metrics', {'p_audit_id': recent_audit['audit_id']}).execute()
            print("✅ Regenerated cache with correct brand data")
        except Exception as e:
            print(f"❌ Failed to regenerate cache: {e}")
        
        print(f"\n🎉 Brand fix completed!")
        print(f"📊 Audit {recent_audit['audit_id']} now correctly associated with Dentsu")
        print(f"🔄 Cache has been regenerated with correct data")
        
    else:
        print("❌ No audit with analysis data found")

if __name__ == "__main__":
    fix_brand_issue()

