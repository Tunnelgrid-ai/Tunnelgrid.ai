#!/usr/bin/env python3
"""
Test script for Topics API functionality
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes.topics import get_fallback_topics, generate_topics, TopicsGenerateRequest
from fastapi import Request
from unittest.mock import Mock

async def test_fallback_topics():
    """Test the fallback topics endpoint"""
    print("🧪 Testing fallback topics...")
    
    try:
        response = await get_fallback_topics()
        print(f"✅ Fallback topics response:")
        print(f"   Success: {response.success}")
        print(f"   Source: {response.source}")
        print(f"   Number of topics: {len(response.topics)}")
        
        for i, topic in enumerate(response.topics, 1):
            print(f"   {i}. {topic.name}")
            print(f"      {topic.description}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing fallback topics: {e}")
        return False

async def test_generate_topics():
    """Test the generate topics endpoint"""
    print("\n🧪 Testing generate topics...")
    
    try:
        # Create a mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        
        # Create test data
        test_data = TopicsGenerateRequest(
            brandName="Apple",
            brandDomain="apple.com",
            productName="iPhone",
            industry="Technology",
            additionalContext="Smartphone market analysis"
        )
        
        response = await generate_topics(mock_request, test_data)
        print(f"✅ Generate topics response:")
        print(f"   Success: {response.success}")
        print(f"   Source: {response.source}")
        print(f"   Number of topics: {len(response.topics)}")
        print(f"   Processing time: {response.processingTime}ms")
        
        if response.reason:
            print(f"   Reason: {response.reason}")
        
        for i, topic in enumerate(response.topics, 1):
            print(f"   {i}. {topic.name}")
            print(f"      {topic.description}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing generate topics: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Topics API Tests\n")
    
    # Test fallback topics
    fallback_success = await test_fallback_topics()
    
    # Test generate topics
    generate_success = await test_generate_topics()
    
    print(f"\n📊 Test Results:")
    print(f"   Fallback topics: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    print(f"   Generate topics: {'✅ PASS' if generate_success else '❌ FAIL'}")
    
    if fallback_success and generate_success:
        print("\n🎉 All tests passed! The topics API should return 10 topics.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 