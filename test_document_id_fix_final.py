#!/usr/bin/env python3
"""
Test Document ID Fix - Final Verification
This script tests that the frontend correctly receives and assigns UUID format document IDs from the backend.
"""

import requests
import json
import sys
import os
from pathlib import Path
import re

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

API_BASE_URL = "http://localhost:8000"

def is_valid_uuid(test_string):
    """Check if a string is a valid UUID format"""
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', test_string))

def is_old_hash_format(test_string):
    """Check if a string is in old MD5 hash format"""
    return bool(re.match(r'^[a-f0-9]{32}$', test_string))

def test_single_document_analysis():
    """Test single document analysis returns proper UUID format document ID"""
    print("\n=== Testing Single Document Analysis ===")
    
    # Create a test text file
    test_content = b"This is a test document for verifying document ID format.\nThe system should return a proper UUID format document ID."
    
    files = {"file": ("test_doc.txt", test_content, "text/plain")}
    data = {
        "query_type": "qa",
        "user_query": "What is this document about?"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Single document analysis successful")
        print(f"📄 Response keys: {list(result.keys())}")
        
        # Check document_id field
        if "document_id" in result:
            document_id = result["document_id"]
            print(f"🆔 Document ID: {document_id}")
            
            if is_valid_uuid(document_id):
                print(f"✅ Valid UUID format: {document_id}")
                return True, document_id
            elif is_old_hash_format(document_id):
                print(f"🚨 OLD HASH FORMAT detected: {document_id}")
                return False, document_id
            else:
                print(f"❌ UNKNOWN FORMAT: {document_id}")
                return False, document_id
        else:
            print(f"❌ No document_id in response")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in single document analysis: {e}")
        return False, None

def test_multi_document_analysis():
    """Test multi-document analysis returns proper UUID format document ID"""
    print("\n=== Testing Multi-Document Analysis ===")
    
    # Create test files
    test_content1 = b"This is the first test document for multi-document analysis."
    test_content2 = b"This is the second test document for multi-document analysis."
    
    files = {
        "file": ("test_doc1.txt", test_content1, "text/plain"),
        "extra_files_1": ("test_doc2.txt", test_content2, "text/plain")
    }
    data = {
        "query_type": "summary"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Multi-document analysis successful")
        print(f"📄 Response keys: {list(result.keys())}")
        
        # Check for multi_document_id (priority) or document_id
        document_id = None
        if "multi_document_id" in result:
            document_id = result["multi_document_id"]
            print(f"🆔 Multi-Document ID: {document_id}")
        elif "document_id" in result:
            document_id = result["document_id"]
            print(f"🆔 Document ID: {document_id}")
        
        if document_id:
            if is_valid_uuid(document_id):
                print(f"✅ Valid UUID format: {document_id}")
                return True, document_id
            elif is_old_hash_format(document_id):
                print(f"🚨 OLD HASH FORMAT detected: {document_id}")
                return False, document_id
            else:
                print(f"❌ UNKNOWN FORMAT: {document_id}")
                return False, document_id
        else:
            print(f"❌ No document_id or multi_document_id in response")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in multi-document analysis: {e}")
        return False, None

def test_chat_history_loading(document_id):
    """Test that chat history can be loaded with the UUID document ID"""
    print(f"\n=== Testing Chat History Loading ===")
    print(f"🔍 Testing with document ID: {document_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{document_id}")
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Chat history endpoint accessible")
        print(f"📜 Chat history entries: {len(result.get('history', []))}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"⚠️ No chat history found for document {document_id} (expected for new documents)")
            return True  # This is OK for new documents
        else:
            print(f"❌ HTTP error loading chat history: {e}")
            return False
    except Exception as e:
        print(f"❌ Error loading chat history: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 Document ID Fix - Final Verification Test")
    print("=" * 50)
    
    # Test single document
    single_success, single_doc_id = test_single_document_analysis()
    
    # Test multi-document
    multi_success, multi_doc_id = test_multi_document_analysis()
    
    # Test chat history loading if we have valid document IDs
    chat_success = True
    if single_success and single_doc_id:
        chat_success = test_chat_history_loading(single_doc_id)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    if single_success:
        print(f"✅ Single Document: UUID format ID generated: {single_doc_id}")
    else:
        print(f"❌ Single Document: Failed - {single_doc_id}")
    
    if multi_success:
        print(f"✅ Multi-Document: UUID format ID generated: {multi_doc_id}")
    else:
        print(f"❌ Multi-Document: Failed - {multi_doc_id}")
    
    if chat_success:
        print(f"✅ Chat History: Loading successful")
    else:
        print(f"❌ Chat History: Loading failed")
    
    # Overall status
    all_success = single_success and multi_success and chat_success
    if all_success:
        print("\n🎉 ALL TESTS PASSED! Document ID fix is working correctly.")
        print("📋 Next steps:")
        print("   1. Clear frontend session state using the '🧹 Clear Session State' button")
        print("   2. Upload a NEW document in the frontend")
        print("   3. The frontend should now receive and use the UUID format document ID")
        print("   4. Chat history should load correctly")
    else:
        print("\n🚨 SOME TESTS FAILED! Backend may still have issues.")
        print("📋 Check the failed tests above and review the backend code.")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
