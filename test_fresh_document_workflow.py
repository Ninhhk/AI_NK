#!/usr/bin/env python3
"""
Complete end-to-end test demonstrating the fixed RAG system.
This script will verify that new document uploads get UUID document IDs 
and that chat history works correctly.
"""
import requests
import json
import time
import uuid
import re

API_BASE_URL = "http://localhost:8000"

def is_valid_uuid(test_string):
    """Check if a string is a valid UUID"""
    try:
        uuid.UUID(test_string)
        return True
    except ValueError:
        return False

def test_fresh_document_analysis():
    """Test complete workflow with fresh document upload"""
    print("🚀 Testing Fresh Document Analysis Workflow")
    print("=" * 60)
    
    # Create a unique test document
    timestamp = int(time.time())
    test_content = f"""
    This is a fresh test document created at {timestamp}.
    
    Content Summary:
    - Document testing the RAG system's document ID synchronization
    - Created to verify UUID format document IDs 
    - Tests chat history functionality with proper backend integration
    - Timestamp: {timestamp}
    
    Topics covered:
    - RAG system architecture
    - Document ID management
    - Chat history synchronization
    - Backend-frontend integration
    """
    
    print(f"\n📄 Step 1: Creating fresh test document (timestamp: {timestamp})")
    
    try:
        files = {'file': (f'fresh_test_{timestamp}.txt', test_content.encode(), 'text/plain')}
        data = {
            'query_type': 'qa',
            'user_query': 'What is the main purpose of this document and what timestamp was it created?',
            'start_page': 0,
            'end_page': -1
        }
        
        print("📤 Step 2: Analyzing document with QA query...")
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            document_id = result.get('document_id')
            chat_id = result.get('chat_id')
            
            print(f"✅ Document analyzed successfully!")
            print(f"📋 Document ID: {document_id}")
            print(f"💬 Chat ID: {chat_id}")
            
            # Verify document ID format
            if document_id and is_valid_uuid(document_id):
                print("✅ Document ID is in correct UUID format")
            else:
                print(f"❌ Document ID format issue: {document_id}")
                return False
            
            print(f"\n📝 Step 3: Generated response preview:")
            answer = result.get('answer', result.get('result', 'No answer found'))
            print(f"Response: {answer[:200]}...")
            
            if document_id:
                # Wait for chat history to be saved
                print("\n⏳ Step 4: Waiting for chat history to be saved...")
                time.sleep(1)
                
                # Test chat history retrieval
                print(f"📜 Step 5: Retrieving chat history for {document_id}...")
                
                chat_response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{document_id}")
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    
                    print(f"✅ Chat history retrieved successfully!")
                    print(f"📊 Response keys: {list(chat_result.keys())}")
                    
                    if 'history' in chat_result:
                        history = chat_result['history']
                        print(f"💭 Number of chat entries: {len(history)}")
                        
                        if history:
                            latest_entry = history[-1]
                            print(f"\n📝 Latest Chat Entry Details:")
                            print(f"   🆔 Chat ID: {latest_entry.get('id', 'N/A')}")
                            print(f"   📋 Document ID: {latest_entry.get('document_id', 'N/A')}")
                            print(f"   ❓ Query: {latest_entry.get('user_query', 'N/A')}")
                            print(f"   🤖 Response: {latest_entry.get('system_response', 'N/A')[:100]}...")
                            print(f"   ⏰ Created: {latest_entry.get('created_at', 'N/A')}")
                            
                            # Verify the document ID in chat history matches
                            chat_doc_id = latest_entry.get('document_id')
                            if chat_doc_id == document_id:
                                print("✅ Document ID consistency verified!")
                                return True
                            else:
                                print(f"❌ Document ID mismatch: chat={chat_doc_id}, analysis={document_id}")
                                return False
                        else:
                            print("⚠️  Chat history is empty")
                            return False
                    else:
                        print("⚠️  No 'history' key in chat response")
                        return False
                else:
                    print(f"❌ Chat history retrieval failed: {chat_response.status_code}")
                    print(f"Error: {chat_response.text}")
                    return False
            else:
                print("❌ No document_id in analysis response")
                return False
        else:
            print(f"❌ Document analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in workflow test: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing RAG System with Fresh Document Upload")
    print("This test verifies that the document ID synchronization fix is working")
    print()
    
    success = test_fresh_document_analysis()
    
    print("\n" + "=" * 60)
    print("🏆 FINAL RESULT")
    
    if success:
        print("✅ COMPLETE SUCCESS! RAG system is fully functional!")
        print("🎯 Document ID synchronization is working correctly")
        print("📊 Chat history integration is working properly") 
        print("🔄 Frontend should now work with fresh document uploads")
    else:
        print("❌ Issues detected - check the logs above")
        print("💡 Try uploading a NEW document in the frontend to test the fix")
