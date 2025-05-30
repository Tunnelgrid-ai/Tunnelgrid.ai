#!/usr/bin/env python3
"""
Simple test for Topics API
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes.topics import FALLBACK_TOPICS, get_groq_api_key

def test_fallback_topics():
    """Test fallback topics"""
    print("🧪 Testing fallback topics...")
    print(f"Number of fallback topics: {len(FALLBACK_TOPICS)}")
    
    for i, topic in enumerate(FALLBACK_TOPICS, 1):
        print(f"{i}. {topic['name']}")
        print(f"   {topic['description']}")
    
    return len(FALLBACK_TOPICS) == 10

def test_api_key():
    """Test API key availability"""
    print("\n🧪 Testing API key...")
    api_key = get_groq_api_key()
    
    if api_key:
        print(f"✅ API key found: {api_key[:10]}...")
        return True
    else:
        print("❌ No API key found")
        return False

def main():
    """Main test function"""
    print("🚀 Simple Topics API Test\n")
    
    # Test fallback topics
    fallback_ok = test_fallback_topics()
    print(f"Fallback topics: {'✅ PASS' if fallback_ok else '❌ FAIL'}")
    
    # Test API key
    api_key_ok = test_api_key()
    print(f"API key: {'✅ PASS' if api_key_ok else '❌ FAIL'}")
    
    print(f"\n📊 Summary:")
    print(f"The API should return {len(FALLBACK_TOPICS)} topics")
    print(f"Source will be: {'AI' if api_key_ok else 'fallback'}")

if __name__ == "__main__":
    main() 