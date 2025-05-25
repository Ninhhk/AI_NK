#!/usr/bin/env python3
"""
Test script to verify the document ID synchronization fix
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_document_analysis():
    """Test document analysis and verify proper document ID handling"""
    print("=== Testing Document Analysis and Chat History Fix ===")
    
    # Test with a simple text file to simulate PDF upload
    files = {
        "file": ("test_document.txt", "This is a test document for analyzing AI search algorithms.", "text/plain")
    }
    
    data = {
        "query_type": "summary",
        "model_name": "qwen3:4b",
        "system_prompt": "must answer in vietnamese, phải trả lời bằng tiếng việt"
    }
    
    print("1. Uploading document and requesting summary...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        print("✅ Document analysis successful!")
        print(f"Result keys: {list(result.keys())}")
        
        # Check for proper document ID
        document_id = None
        if "document_id" in result:
            document_id = result["document_id"]
            print(f"📄 Got document_id: {document_id}")
        elif "multi_document_id" in result:
            document_id = result["multi_document_id"]
            print(f"📄 Got multi_document_id: {document_id}")
        elif "document_ids" in result and result["document_ids"]:
            document_id = result["document_ids"][0]
            print(f"📄 Got first document_id from list: {document_id}")
        else:
            print("❌ No document ID found in result!")
            return False
            
        # Test chat history retrieval
        print(f"2. Testing chat history retrieval for document ID: {document_id}")
        
        # Wait a moment for any backend processing
        time.sleep(1)
        
        try:
            history_response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{document_id}")
            history_response.raise_for_status()
            history_result = history_response.json()
            
            print("✅ Chat history retrieval successful!")
            print(f"Chat history entries: {len(history_result.get('history', []))}")
            
            if history_result.get('history'):
                for i, entry in enumerate(history_result['history']):
                    print(f"  Entry {i+1}: {entry.get('user_query', 'N/A')[:50]}...")
            else:
                print("  No chat history entries found (expected for summary mode)")
                
            return True
            
        except requests.exceptions.HTTPError as e:
            if "404" in str(e):
                print(f"❌ Document not found in chat history: {document_id}")
                print("This indicates the document ID synchronization is still not working properly")
            else:
                print(f"❌ Chat history retrieval failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Document analysis failed: {e}")
        return False

def test_qa_mode():
    """Test QA mode to ensure chat history is properly stored"""
    print("\n=== Testing QA Mode ===")
    
    files = {
        "file": ("test_qa.txt", "AI search algorithms include breadth-first search, depth-first search, and A* algorithm.", "text/plain")
    }
    
    data = {
        "query_type": "qa",
        "user_query": "What search algorithms are mentioned?",
        "model_name": "qwen3:4b",
        "system_prompt": "must answer in vietnamese, phải trả lời bằng tiếng việt"
    }
    
    print("1. Uploading document and asking question...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        print("✅ QA analysis successful!")
        
        # Get document ID
        document_id = None
        if "document_id" in result:
            document_id = result["document_id"]
        elif "multi_document_id" in result:
            document_id = result["multi_document_id"]
        elif "document_ids" in result and result["document_ids"]:
            document_id = result["document_ids"][0]
            
        if document_id:
            print(f"📄 Document ID: {document_id}")
            
            # Test chat history
            print("2. Checking chat history...")
            time.sleep(2)  # Wait for backend to process
            
            history_response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{document_id}")
            history_response.raise_for_status()
            history_result = history_response.json()
            
            print(f"✅ Found {len(history_result.get('history', []))} chat entries")
            
            for entry in history_result.get('history', []):
                print(f"  Q: {entry.get('user_query', '')[:50]}...")
                print(f"  A: {entry.get('system_response', '')[:50]}...")
                
            return True
        else:
            print("❌ No document ID found")
            return False
            
    except Exception as e:
        print(f"❌ QA test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing document ID synchronization fix...")
    
    # Test basic functionality
    summary_success = test_document_analysis()
    qa_success = test_qa_mode()
    
    print(f"\n=== Test Results ===")
    print(f"Summary mode: {'✅ PASS' if summary_success else '❌ FAIL'}")
    print(f"QA mode: {'✅ PASS' if qa_success else '❌ FAIL'}")
    
    if summary_success and qa_success:
        print("\n🎉 All tests passed! Document ID synchronization is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Document ID synchronization needs more work.")
