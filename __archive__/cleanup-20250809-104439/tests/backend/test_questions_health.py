#!/usr/bin/env python3
import requests

def test_questions_health():
    try:
        response = requests.get('http://127.0.0.1:8000/api/questions/health')
        print(f"Status: {response.status_code}")
        print(f"Content: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_questions_health() 