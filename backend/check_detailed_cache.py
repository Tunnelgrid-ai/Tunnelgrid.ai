#!/usr/bin/env python3
"""
Check the detailed structure of persona_visibility and topic_visibility in the cache
"""

from app.core.database import get_supabase_client
import json

def check_detailed_cache():
    print("🔍 Checking detailed cache structure...")
    
    supabase = get_supabase_client()
    
    # Check the Dentsu audit cache
    audit_id = "b461e0a0-2593-4639-8edf-1a168e3f1d8d"
    
    cache_result = supabase.table('comprehensive_metrics_cache').select('*').eq('audit_id', audit_id).execute()
    if cache_result.data:
        cache = cache_result.data[0]
        
        print(f"\n📊 Detailed persona_visibility structure:")
        persona_visibility = cache.get('persona_visibility', {})
        if persona_visibility:
            print(f"  Type: {type(persona_visibility)}")
            print(f"  Keys: {list(persona_visibility.keys())}")
            print(f"  Full data: {json.dumps(persona_visibility, indent=2)}")
        else:
            print(f"  No persona_visibility data")
        
        print(f"\n📊 Detailed topic_visibility structure:")
        topic_visibility = cache.get('topic_visibility', {})
        if topic_visibility:
            print(f"  Type: {type(topic_visibility)}")
            print(f"  Keys: {list(topic_visibility.keys())}")
            print(f"  Full data: {json.dumps(topic_visibility, indent=2)}")
        else:
            print(f"  No topic_visibility data")
        
        print(f"\n📊 Detailed persona_topic_matrix structure:")
        persona_topic_matrix = cache.get('persona_topic_matrix', {})
        if persona_topic_matrix:
            print(f"  Type: {type(persona_topic_matrix)}")
            print(f"  Keys: {list(persona_topic_matrix.keys())}")
            print(f"  Full data: {json.dumps(persona_topic_matrix, indent=2)}")
        else:
            print(f"  No persona_topic_matrix data")
        
    else:
        print(f"❌ No cache found for audit {audit_id}")

if __name__ == "__main__":
    check_detailed_cache()

