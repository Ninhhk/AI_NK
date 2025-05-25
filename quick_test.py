import requests
import os

print("=== File Type Handling Test ===")

# Create test file
with open('test.txt', 'w') as f:
    f.write('This is a test document about artificial intelligence and machine learning algorithms.')

print("Created test.txt file")

# Test analysis
print("Testing document analysis...")
with open('test.txt', 'rb') as f:
    files = {'file': ('test.txt', f, 'text/plain')}
    data = {'query_type': 'qa', 'user_query': 'What is this document about?'}
    
    try:
        response = requests.post('http://localhost:8000/api/documents/analyze', files=files, data=data, timeout=30)
        print(f'Response Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('SUCCESS! Text file analysis completed!')
            print(f'Document ID: {result.get("document_id", "Not found")}')
            print(f'Answer: {result.get("answer", "No answer")[:150]}...')
            
            # Test chat history if we have document ID
            if 'document_id' in result:
                doc_id = result['document_id']
                print(f'\\nTesting chat history for document {doc_id}...')
                hist_response = requests.get(f'http://localhost:8000/api/documents/chat-history/{doc_id}')
                print(f'Chat history status: {hist_response.status_code}')
                if hist_response.status_code == 200:
                    history = hist_response.json()
                    print(f'Chat history entries: {len(history.get("history", []))}')
                
        else:
            print(f'Error Response: {response.text[:300]}')
            
    except Exception as e:
        print(f'Exception occurred: {str(e)}')

# Clean up
if os.path.exists('test.txt'):
    os.remove('test.txt')
    print('Cleaned up test file')

print('Test completed!')
