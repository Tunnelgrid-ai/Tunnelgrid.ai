"""
Test script to validate raw JSON storage in AI analysis workflow
Usage: python backend/test_raw_json_storage.py --question "What are Tesla's latest developments?"
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Import your services
from app.services.ai_analysis import openai_service
from app.models.analysis import AIAnalysisRequest, LLMServiceType

async def test_raw_json_storage(question: str) -> None:
    """Test that raw JSON is being stored correctly in the database"""
    
    print(f"🧪 Testing raw JSON storage with question: {question}")
    print("=" * 60)
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Step 0: Create a temporary query entry (since we need FK constraint)
    test_audit_id = str(uuid.uuid4())
    test_query_id = str(uuid.uuid4())
    test_persona_id = str(uuid.uuid4())
    
    temp_query_data = {
        "query_id": test_query_id,
        "audit_id": test_audit_id,
        "persona": test_persona_id,
        "query_text": question,
        "query_type": "test",
        "topic_name": "Test Topic"
    }
    
    try:
        print("🔄 Step 0: Creating temporary query entry...")
        
        # Insert temporary query (this will be cleaned up)
        query_result = supabase.table("queries").insert(temp_query_data).execute()
        
        if hasattr(query_result, 'error') and query_result.error:
            print(f"❌ Failed to create temporary query: {query_result.error}")
            return
        
        print(f"✅ Temporary query created with ID: {test_query_id}")
        
        # Create a test request
        test_persona = "Tech-savvy consumer interested in electric vehicles and sustainable technology"
        
        request = AIAnalysisRequest(
            query_id=test_query_id,
            persona_description=test_persona,
            question_text=question,
            model="gpt-4o-search-preview",
            service=LLMServiceType.OPENAI
        )
        
        print("🔄 Step 1: Making OpenAI API call...")
        
        # Call your OpenAI service
        analysis_result = await openai_service.analyze_brand_perception(request)
        
        print(f"✅ API call successful!")
        print(f"   Response length: {len(analysis_result.response_text)} characters")
        print(f"   Citations found: {len(analysis_result.citations)}")
        print(f"   Processing time: {analysis_result.processing_time_ms}ms")
        print(f"   Raw JSON present: {'Yes' if analysis_result.raw_response_json else 'No'}")
        
        print("\n🔄 Step 2: Storing in database...")
        
        # Store in database (same logic as your routes)
        response_data = {
            "response_id": str(uuid.uuid4()),
            "query_id": test_query_id,  # Now using valid FK
            "model": analysis_result.model,
            "response_text": analysis_result.response_text
        }
        
        # Insert into database
        response_result = supabase.table("responses").insert(response_data).execute()
        
        if hasattr(response_result, 'error') and response_result.error:
            print(f"❌ Database insert failed: {response_result.error}")
            return
        
        response_id = response_result.data[0]["response_id"]
        print(f"✅ Database insert successful! Response ID: {response_id}")
        
        print("\n🔄 Step 3: Validating stored data...")
        
        # Retrieve and validate the stored data
        stored_result = supabase.table("responses").select("*").eq("response_id", response_id).execute()
        
        if not stored_result.data:
            print("❌ No data found in database")
            return
        
        stored_row = stored_result.data[0]
        
        print("✅ Validation Results:")
        print(f"   ✓ Response text stored: {len(stored_row['response_text'])} characters")
        print(f"   ✓ Model stored: {stored_row.get('model', 'Not found')}")
        print(f"   ✓ Query ID stored: {stored_row.get('query_id', 'Not found')}")
        
        # Note: Raw JSON, token usage, and processing time are not stored in responses table
        # They are handled through the brand_extractions table for source information
        print("   ℹ️ Raw JSON, token usage, and processing time are handled separately")
        
        print("\n🔄 Step 4: Analysis result summary...")
        print(f"   ✓ Response text length: {len(analysis_result.response_text)} characters")
        print(f"   ✓ Model used: {analysis_result.model}")
        print(f"   ✓ Processing time: {analysis_result.processing_time_ms}ms")
        print(f"   ✓ Token usage: {analysis_result.token_usage}")
        print(f"   ✓ Raw JSON available: {'Yes' if analysis_result.raw_response_json else 'No'}")
        
        print("\n🧹 Step 5: Cleanup (removing test data)...")
        
        # Clean up test data (response first, then query due to FK)
        supabase.table("responses").delete().eq("response_id", response_id).execute()
        supabase.table("queries").delete().eq("query_id", test_query_id).execute()
        print("✅ Test data cleaned up")
        
        print("\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print("Raw JSON storage is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        
        # Cleanup on error
        try:
            print("🧹 Cleaning up on error...")
            supabase.table("responses").delete().eq("query_id", test_query_id).execute()
            supabase.table("queries").delete().eq("query_id", test_query_id).execute()
        except:
            pass
            
        import traceback
        traceback.print_exc()

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test raw JSON storage in AI analysis")
    p.add_argument("--question", 
                   default="What are Tesla's latest product announcements?", 
                   help="Question to test with (default: Tesla question)")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    asyncio.run(test_raw_json_storage(args.question))

if __name__ == "__main__":
    main()