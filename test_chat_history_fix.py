#!/usr/bin/env python3
"""
Test script to verify chat history retrieval with existing document IDs
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_existing_document_chat_history():
    """Test chat history retrieval with an existing document ID"""
    print("=== Testing Chat History with Existing Document ID ===")
    
    # Use an existing document ID from our database
    existing_doc_id = "1d5d9515-896e-4f1e-9de6-44fe7fe24606"  # From most recent conversation
    
    print(f"Testing chat history retrieval for document ID: {existing_doc_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{existing_doc_id}")
        response.raise_for_status()
        result = response.json()
        
        print("✅ Chat history retrieval successful!")
        print(f"Found {len(result.get('history', []))} chat entries")
        
        for i, entry in enumerate(result.get('history', [])[:3]):  # Show first 3
            print(f"  Entry {i+1}:")
            print(f"    Q: {entry.get('user_query', 'N/A')[:60]}...")
            print(f"    A: {entry.get('system_response', 'N/A')[:60]}...")
            
        return True
        
    except requests.exceptions.HTTPError as e:
        if "404" in str(e):
            print(f"❌ Document not found: {existing_doc_id}")
        else:
            print(f"❌ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_nonexistent_document():
    """Test with a non-existent document ID"""
    print("\n=== Testing with Non-existent Document ID ===")
    
    fake_doc_id = "97a7810e107d6e29910212a0535d6dcb"  # The problematic ID from frontend
    
    print(f"Testing with fake document ID: {fake_doc_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{fake_doc_id}")
        response.raise_for_status()
        result = response.json()
        
        print("✅ Request succeeded (empty history expected)")
        print(f"Found {len(result.get('history', []))} chat entries")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"Expected 404 error: {e}")
        return True  # This is expected
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_document_analysis_with_real_pdf():
    """Test document analysis with a real PDF file from uploads"""
    print("\n=== Testing Document Analysis with Real PDF ===")
    
    # Check if we have any real PDF files in uploads
    import os
    uploads_dir = r"c:\Users\ADMIN\Test_Gen_slide\AI_NVCB\AI_NVCB\storage\uploads"
    
    if not os.path.exists(uploads_dir):
        print("❌ Uploads directory not found")
        return False
        
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in uploads directory")
        return False
        
    # Use the first PDF file found
    pdf_file = pdf_files[0]
    pdf_path = os.path.join(uploads_dir, pdf_file)
    
    print(f"Using PDF file: {pdf_file}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {"file": (pdf_file, f, "application/pdf")}
            data = {
                "query_type": "summary",
                "model_name": "qwen3:4b",
                "system_prompt": "must answer in vietnamese"
            }
            
            response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
            response.raise_for_status()
            result = response.json()
            
            print("✅ PDF analysis successful!")
            print(f"Result keys: {list(result.keys())}")
            
            # Check for document ID
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
                
            return True
            
    except Exception as e:
        print(f"❌ PDF analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing chat history functionality...")
    
    # Test with existing document
    existing_success = test_existing_document_chat_history()
    
    # Test with non-existent document
    nonexistent_success = test_nonexistent_document()
    
    # Test with real PDF
    pdf_success = test_document_analysis_with_real_pdf()
    
    print(f"\n=== Test Results ===")
    print(f"Existing document chat history: {'✅ PASS' if existing_success else '❌ FAIL'}")
    print(f"Non-existent document handling: {'✅ PASS' if nonexistent_success else '❌ FAIL'}")
    print(f"PDF document analysis: {'✅ PASS' if pdf_success else '❌ FAIL'}")
    
    if existing_success and nonexistent_success and pdf_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed.")
