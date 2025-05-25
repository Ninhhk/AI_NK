import requests
import json

print("=== Debugging Document Analysis Response ===")

# Create test file
with open('debug_test.txt', 'w') as f:
    f.write('This is a test document for debugging the response structure.')

print("Testing document analysis with detailed response...")

with open('debug_test.txt', 'rb') as f:
    files = {'file': ('debug_test.txt', f, 'text/plain')}
    data = {'query_type': 'qa', 'user_query': 'What is this document about?'}
    
    try:
        response = requests.post('http://localhost:8000/api/documents/analyze', files=files, data=data, timeout=30)
        print(f'Response Status: {response.status_code}')
        print(f'Response Headers: {dict(response.headers)}')
        
        if response.status_code == 200:
            result = response.json()
            print('\\n=== FULL RESPONSE STRUCTURE ===')
            print(json.dumps(result, indent=2))
            
            print('\\n=== KEY ANALYSIS ===')
            print(f'Keys in response: {list(result.keys())}')
            print(f'Document ID: {result.get("document_id", "NOT FOUND")}')
            print(f'Document IDs: {result.get("document_ids", "NOT FOUND")}')
            print(f'Multi Document ID: {result.get("multi_document_id", "NOT FOUND")}')
            print(f'Answer: {result.get("answer", "NOT FOUND")}')
            print(f'Result: {result.get("result", "NOT FOUND")}')
            
        else:
            print(f'Error Response: {response.text}')
            
    except Exception as e:
        print(f'Exception: {str(e)}')

# Clean up
import os
if os.path.exists('debug_test.txt'):
    os.remove('debug_test.txt')

print('\\nDebug test completed!')
