import requests

def test_api():
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Server health: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is running!")
            print(response.json())
        else:
            print("❌ Server issues")
    except:
        print("❌ Cannot connect to server")

test_api() 