#!/usr/bin/env python3

import requests
import json
import time
import os

# Test the file type handling fix
def test_text_file_analysis():
    """Test document analysis with a text file to verify file type handling fix."""
    
    # Create a test text file
    test_file_path = "test_document.txt"
    test_content = """This is a test document for the RAG system.

The document contains multiple paragraphs to test the text processing capabilities.

Key topics include:
- Document analysis
- File type handling
- Text processing
- RAG system functionality

This should be processed correctly by the enhanced document service that can handle both PDF and text files.
"""
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Test document analysis endpoint
        url = "http://localhost:8000/api/analyze-document"
        
        print("Testing text file analysis...")
        print(f"Uploading: {test_file_path}")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            data = {
                'analysis_type': 'summary',
                'include_quiz': 'false'
            }
            
            response = requests.post(url, files=files, data=data)
            
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== SUCCESS: Document Analysis Response ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check if document_id is present
            if 'document_id' in result:
                document_id = result['document_id']
                print(f"\n✅ Document ID found: {document_id}")
                
                # Test chat history retrieval with the document ID
                print(f"\nTesting chat history retrieval for document: {document_id}")
                chat_url = f"http://localhost:8000/api/chat-history/{document_id}"
                chat_response = requests.get(chat_url)
                
                print(f"Chat History Status: {chat_response.status_code}")
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    print("✅ Chat history retrieval successful")
                    print(f"Chat history items: {len(chat_data.get('chat_history', []))}")
                else:
                    print(f"❌ Chat history retrieval failed: {chat_response.text}")
                    
            else:
                print("❌ No document_id in response")
                
        else:
            print(f"❌ Document analysis failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"\nCleaned up: {test_file_path}")

if __name__ == "__main__":
    test_text_file_analysis()
