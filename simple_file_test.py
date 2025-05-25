import requests
import json

# Simple test
API_BASE_URL = "http://localhost:8000"

print("Testing simple API connection...")

try:
    # Test if server is running by trying a simple endpoint
    response = requests.get(f"{API_BASE_URL}/api/documents/system-prompt", timeout=5)
    print(f"System prompt endpoint status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Server is responding!")
    else:
        print(f"Server responded with: {response.text}")
        
except Exception as e:
    print(f"❌ Error connecting to server: {str(e)}")

print("\nTesting text file analysis...")

# Create a simple test file
test_content = "This is a test document about AI and machine learning."
with open("simple_test.txt", "w") as f:
    f.write(test_content)

try:
    with open("simple_test.txt", "rb") as f:
        files = {"file": ("simple_test.txt", f, "text/plain")}
        data = {
            "query_type": "qa",
            "user_query": "What is this document about?"
        }
        
        print("Sending analysis request...")
        response = requests.post(
            f"{API_BASE_URL}/api/documents/analyze",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Document ID: {result.get('document_id', 'Not found')}")
            print(f"Answer: {result.get('answer', 'No answer')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Clean up
import os
if os.path.exists("simple_test.txt"):
    os.remove("simple_test.txt")

print("Test completed.")
