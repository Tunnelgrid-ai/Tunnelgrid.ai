#!/usr/bin/env python3
"""
Check the cache structure to see what data is available
"""

from app.core.database import get_supabase_client

def check_cache_structure():
    print("🔍 Checking cache structure...")
    
    supabase = get_supabase_client()
    
    # Check the Dentsu audit cache
    audit_id = "b461e0a0-2593-4639-8edf-1a168e3f1d8d"
    
    cache_result = supabase.table('comprehensive_metrics_cache').select('*').eq('audit_id', audit_id).execute()
    if cache_result.data:
        cache = cache_result.data[0]
        print(f"\n📊 Cache structure for audit {audit_id}:")
        for key, value in cache.items():
            if key in ['persona_visibility', 'topic_visibility', 'persona_topic_matrix']:
                print(f"  {key}: {type(value)} - {str(value)[:100]}...")
            else:
                print(f"  {key}: {value}")
        
        # Check if topics and personas exist for this audit
        print(f"\n🔍 Checking topics and personas for this audit...")
        
        # Check topics
        topics_result = supabase.table('topics').select('*').eq('audit_id', audit_id).execute()
        if topics_result.data:
            print(f"  Topics found: {len(topics_result.data)}")
            for topic in topics_result.data[:3]:
                print(f"    - {topic.get('topic_name', 'Unknown')}")
        else:
            print(f"  No topics found")
        
        # Check personas
        personas_result = supabase.table('personas').select('*').eq('audit_id', audit_id).execute()
        if personas_result.data:
            print(f"  Personas found: {len(personas_result.data)}")
            for persona in personas_result.data[:3]:
                print(f"    - {persona.get('persona_type', 'Unknown')}")
        else:
            print(f"  No personas found")
        
        # Check if the cache has the required fields
        print(f"\n🔍 Checking cache completeness...")
        required_fields = ['persona_visibility', 'topic_visibility', 'persona_topic_matrix']
        for field in required_fields:
            if field in cache and cache[field]:
                print(f"  ✅ {field}: Available")
            else:
                print(f"  ❌ {field}: Missing or empty")
        
    else:
        print(f"❌ No cache found for audit {audit_id}")

if __name__ == "__main__":
    check_cache_structure()

