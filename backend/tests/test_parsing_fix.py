#!/usr/bin/env python3
"""
Test the parsing fix
"""

import sys
import os
sys.path.append('.')

from app.routes.topics import parse_topics_from_response

def test_parsing_fix():
    print("🧪 Testing Parsing Fix...")
    
    # Test 1: Object format (json_object response)
    object_format = '''
    {
       "topics": [
          {
             "name": "iPhone Design Appeal",
             "description": "Consumer perception of iPhone's aesthetic design"
          },
          {
             "name": "Pricing Strategy",
             "description": "Consumer opinions on iPhone pricing"
          }
       ]
    }
    '''
    
    print("\n📋 Testing object format...")
    result1 = parse_topics_from_response(object_format)
    print(f"Object format: {'✅ PASS' if result1 and len(result1) == 2 else '❌ FAIL'}")
    if result1:
        print(f"  Found {len(result1)} topics")
        print(f"  First topic: {result1[0]['name']}")
    
    # Test 2: Array format (without response_format)
    array_format = '''
    [
      {
        "name": "iPhone Design Appeal",
        "description": "Consumer perception of iPhone's aesthetic design"
      },
      {
        "name": "Pricing Strategy", 
        "description": "Consumer opinions on iPhone pricing"
      }
    ]
    '''
    
    print("\n📋 Testing array format...")
    result2 = parse_topics_from_response(array_format)
    print(f"Array format: {'✅ PASS' if result2 and len(result2) == 2 else '❌ FAIL'}")
    if result2:
        print(f"  Found {len(result2)} topics")
        print(f"  First topic: {result2[0]['name']}")
    
    print(f"\n🎯 Overall result: {'✅ ALL TESTS PASS' if result1 and result2 else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    test_parsing_fix() 