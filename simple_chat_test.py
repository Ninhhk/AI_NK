import requests

# Test chat history retrieval
document_id = "05fab6f3-321c-4fb1-b4ee-c505b8209d68"
url = f"http://localhost:8000/api/documents/chat-history/{document_id}"

print(f"Testing: {url}")

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS! Chat history retrieved:")
        print(f"Keys: {list(result.keys())}")
        if 'history' in result:
            print(f"History entries: {len(result['history'])}")
            for i, entry in enumerate(result['history']):
                print(f"Entry {i+1}: {entry.get('user_query', 'N/A')[:30]}...")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
