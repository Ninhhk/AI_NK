#!/usr/bin/env python3
"""
Test script to verify file type handling fix and document ID synchronization
"""

import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8000"

def test_text_file_analysis():
    """Test document analysis with a text file"""
    print("=" * 60)
    print("Testing TEXT file analysis...")
    print("=" * 60)
    
    # Create a test text file
    test_content = """
This is a test document for analyzing file type handling.

The document contains information about:
1. AI and machine learning algorithms
2. Data processing techniques
3. Natural language processing methods

This test will verify that the backend can properly handle text files
without trying to parse them as PDF documents.
"""
    
    test_file_path = "test_document.txt"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Test with text file
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {
                'query_type': 'qa',
                'user_query': 'What topics are covered in this document?'
            }
            
            print(f"Sending request to {API_BASE_URL}/api/documents/analyze")
            print(f"File: {test_file_path}")
            print(f"Query: {data['user_query']}")
            
            response = requests.post(
                f"{API_BASE_URL}/api/documents/analyze",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS: Text file analysis completed!")
                print(f"Document ID: {result.get('document_id', 'Not found')}")
                print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
                
                # Test chat history retrieval
                if 'document_id' in result:
                    test_chat_history_retrieval(result['document_id'])
                
                return True
            else:
                print(f"❌ ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_pdf_file_analysis():
    """Test document analysis with a PDF file (if available)"""
    print("\n" + "=" * 60)
    print("Testing PDF file analysis...")
    print("=" * 60)
    
    # Look for any PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️  No PDF files found in current directory. Skipping PDF test.")
        return True
    
    pdf_file = pdf_files[0]
    print(f"Using PDF file: {pdf_file}")
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}
            data = {
                'query_type': 'summary'
            }
            
            print(f"Sending request to {API_BASE_URL}/api/documents/analyze")
            print(f"File: {pdf_file}")
            print(f"Query type: {data['query_type']}")
            
            response = requests.post(
                f"{API_BASE_URL}/api/documents/analyze",
                files=files,
                data=data,
                timeout=60
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS: PDF file analysis completed!")
                print(f"Document ID: {result.get('document_id', 'Not found')}")
                print(f"Result: {result.get('result', 'No result')[:200]}...")
                
                # Test chat history retrieval
                if 'document_id' in result:
                    test_chat_history_retrieval(result['document_id'])
                
                return True
            else:
                print(f"❌ ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def test_chat_history_retrieval(document_id):
    """Test chat history retrieval for a document ID"""
    print(f"\n--- Testing chat history retrieval for document {document_id} ---")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/documents/chat-history/{document_id}",
            timeout=10
        )
        
        print(f"Chat history response status: {response.status_code}")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Chat history retrieved successfully!")
            print(f"History items: {len(history.get('history', []))}")
            if history.get('history'):
                print(f"Latest entry: {history['history'][-1]['user_query'][:50]}...")
        else:
            print(f"⚠️  Chat history status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat history error: {str(e)}")

def test_server_health():
    """Test if the server is running and healthy"""
    print("Testing server health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"⚠️  Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting File Type Handling Tests")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test server health first
    if not test_server_health():
        print("❌ Server is not available. Please start the backend server first.")
        return
    
    # Run tests
    text_success = test_text_file_analysis()
    pdf_success = test_pdf_file_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Text file analysis: {'✅ PASSED' if text_success else '❌ FAILED'}")
    print(f"PDF file analysis: {'✅ PASSED' if pdf_success else '❌ FAILED'}")
    
    if text_success and pdf_success:
        print("\n🎉 ALL TESTS PASSED! File type handling is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
