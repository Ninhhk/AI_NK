#!/usr/bin/env python3
"""
Test complete end-to-end workflow: Document analysis -> Chat history retrieval
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    print("🚀 Testing Complete RAG Workflow")
    print("=" * 60)
    
    # Step 1: Analyze a document
    print("\n📤 Step 1: Analyzing a new document...")
    
    test_content = """
    This is a comprehensive test document for the RAG system.
    It contains information about artificial intelligence and machine learning.
    The document discusses various AI algorithms and their applications.
    This content will be used to test both document analysis and chat history functionality.
    """
    
    try:
        files = {'file': ('comprehensive_test.txt', test_content.encode(), 'text/plain')}
        data = {
            'query_type': 'qa',
            'user_query': 'What topics does this document cover?',
            'start_page': 0,
            'end_page': -1
        }
        
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            document_id = result.get('document_id')
            
            print(f"✅ Document analyzed successfully!")
            print(f"📋 Document ID: {document_id}")
            print(f"🔑 Response keys: {list(result.keys())}")
            print(f"💬 Chat ID: {result.get('chat_id', 'Not found')}")
            
            if document_id:
                # Step 2: Wait a moment for the chat history to be saved
                print("\n⏳ Step 2: Waiting for chat history to be saved...")
                time.sleep(1)
                
                # Step 3: Retrieve chat history
                print(f"\n📜 Step 3: Retrieving chat history for {document_id}...")
                
                chat_response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{document_id}")
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    
                    print(f"✅ Chat history retrieved successfully!")
                    print(f"📊 Chat response keys: {list(chat_result.keys())}")
                    
                    if 'history' in chat_result:
                        history = chat_result['history']
                        print(f"💭 Number of chat entries: {len(history)}")
                        
                        if history:
                            latest_entry = history[-1]  # Get the most recent entry
                            print(f"\n📝 Latest Chat Entry:")
                            print(f"   🆔 ID: {latest_entry.get('id', 'N/A')}")
                            print(f"   ❓ Query: {latest_entry.get('user_query', 'N/A')}")
                            print(f"   🤖 Response: {latest_entry.get('system_response', 'N/A')[:100]}...")
                            print(f"   ⏰ Time: {latest_entry.get('created_at', latest_entry.get('timestamp', 'N/A'))}")
                            
                            return True
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
    success = test_complete_workflow()
    
    print("\n" + "=" * 60)
    print("🏆 FINAL RESULT")
    
    if success:
        print("✅ COMPLETE SUCCESS! The RAG system is working end-to-end!")
        print("🎯 Document ID synchronization fix is fully functional!")
        print("📊 Both document analysis and chat history retrieval work correctly!")
    else:
        print("❌ Some issues remain - check the logs above")
