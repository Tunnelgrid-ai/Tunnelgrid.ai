#!/usr/bin/env python3
"""
Clear Questions Test Script
Clears all questions from the database to test with fresh data
"""

import requests
import json

def clear_questions():
    print("🧹 Attempting to clear all questions from database...")
    
    try:
        # Try to call a clear endpoint if it exists
        response = requests.delete('http://127.0.0.1:8000/api/questions/clear-all')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully cleared questions")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed to clear questions: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error clearing questions: {e}")

if __name__ == "__main__":
    clear_questions() 