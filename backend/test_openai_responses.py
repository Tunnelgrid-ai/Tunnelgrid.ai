#!/usr/bin/env python3
"""
Test script for OpenAI Responses API with web search capabilities.

This script demonstrates how to use the OpenAIResponsesAPI class to get
responses with web search citations.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.openai_basic_api import OpenAIResponsesAPI, get_openai_response_with_citations


async def test_basic_usage():
    """Test basic usage of the OpenAI Responses API."""
    print("🚀 Testing OpenAI Responses API with Web Search")
    print("=" * 50)
    
    # Example 1: Basic question with web search
    system_prompt = """You are a helpful AI assistant with access to real-time web search. 
    When answering questions, use web search to find current information and provide citations 
    for your sources. Always be accurate and up-to-date."""
    
    user_prompt = "What are the latest developments in AI technology as of 2024?"
    
    print(f"\n📝 System Prompt: {system_prompt}")
    print(f"❓ User Question: {user_prompt}")
    print("\n⏳ Getting response with web search...")
    
    try:
        # Method 1: Using the convenience function
        result = await get_openai_response_with_citations(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            assistant_name="AI Research Assistant"
        )
        
        if result["success"]:
            print("✅ Success!")
            print(f"\n📄 Response:")
            print(result["response"])
            print(f"\n📚 Citations found: {len(result['citations'])}")
            
            for i, citation in enumerate(result['citations'], 1):
                print(f"\n  Citation {i}:")
                print(f"    File ID: {citation['file_id']}")
                print(f"    Quote: {citation['quote'][:100]}...")
                print(f"    Position: {citation['start_index']}-{citation['end_index']}")
            
            # Cleanup
            client = OpenAIResponsesAPI()
            cleanup_result = await client.cleanup_resources(
                thread_id=result['thread_id'],
                assistant_id=result['assistant_id']
            )
            print(f"\n🧹 Cleanup: {cleanup_result}")
            
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


async def test_brand_analysis_example():
    """Test with a brand analysis example."""
    print("\n\n🏢 Testing Brand Analysis Example")
    print("=" * 50)
    
    system_prompt = """You are an expert brand analyst with access to real-time web search. 
    Analyze brands and companies using current information from the web. 
    Provide detailed insights with proper citations for all claims."""
    
    user_prompt = "Analyze the current market position and recent developments of Tesla (TSLA) in 2024."
    
    print(f"\n📝 System Prompt: {system_prompt}")
    print(f"❓ User Question: {user_prompt}")
    print("\n⏳ Getting brand analysis with web search...")
    
    try:
        # Method 2: Using the class directly
        client = OpenAIResponsesAPI()
        
        result = await client.get_response_with_web_search(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            assistant_name="Brand Analysis Expert",
            max_retries=5,
            polling_interval=2.0
        )
        
        if result["success"]:
            print("✅ Success!")
            print(f"\n📄 Brand Analysis:")
            print(result["response"])
            print(f"\n📚 Sources: {len(result['citations'])} citations")
            
            # Cleanup
            await client.cleanup_resources(
                thread_id=result['thread_id'],
                assistant_id=result['assistant_id']
            )
            
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


async def test_error_handling():
    """Test error handling with invalid configuration."""
    print("\n\n⚠️ Testing Error Handling")
    print("=" * 50)
    
    # Temporarily remove API key to test error handling
    original_key = os.environ.get("OPENAI_API_KEY")
    if original_key:
        os.environ["OPENAI_API_KEY"] = "invalid_key"
    
    try:
        client = OpenAIResponsesAPI()
        result = await client.get_response_with_web_search(
            system_prompt="Test",
            user_prompt="Test question"
        )
        
        if not result["success"]:
            print("✅ Error handling working correctly")
            print(f"Error: {result['error']}")
        else:
            print("❌ Error handling failed - should have failed with invalid key")
            
    except Exception as e:
        print(f"✅ Exception caught: {str(e)}")
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


async def main():
    """Main test function."""
    print("🧪 OpenAI Responses API Test Suite")
    print("=" * 60)
    
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key in the .env file or environment.")
        return
    
    # Run tests
    await test_basic_usage()
    await test_brand_analysis_example()
    await test_error_handling()
    
    print("\n\n🎉 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())
