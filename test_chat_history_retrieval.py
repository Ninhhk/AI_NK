#!/usr/bin/env python3
"""
Test chat history retrieval with the document ID from our previous test
"""
import requests
import json

# Use the document ID we saw in the server logs
DOCUMENT_ID = "05fab6f3-321c-4fb1-b4ee-c505b8209d68"
API_BASE_URL = "http://localhost:8000"

def test_chat_history_retrieval():
    print(f"🔍 Testing chat history retrieval for document: {DOCUMENT_ID}")
    
    try:
        # Test the chat history endpoint
        response = requests.get(f"{API_BASE_URL}/api/documents/chat-history/{DOCUMENT_ID}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat history retrieved successfully!")
            print(f"Response keys: {list(result.keys())}")
            
            if 'history' in result:
                history = result['history']
                print(f"Number of chat entries: {len(history)}")
                
                if history:
                    print("\n📝 Chat History Entries:")
                    for i, entry in enumerate(history):
                        print(f"  Entry {i+1}:")
                        print(f"    ID: {entry.get('id', 'N/A')}")
                        print(f"    User Query: {entry.get('user_query', 'N/A')[:50]}...")
                        print(f"    Response: {entry.get('system_response', 'N/A')[:50]}...")
                        print(f"    Timestamp: {entry.get('created_at', entry.get('timestamp', 'N/A'))}")
                        print()
                    
                    return True
                else:
                    print("⚠️  Chat history is empty")
                    return False
            else:
                print("⚠️  No 'history' key in response")
                return False
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chat history: {e}")
        return False

def test_database_chat_history():
    print(f"\n🔍 Testing database chat history directly...")
    
    try:
        # Test the database API endpoint that was mentioned in the conversation summary
        response = requests.get(f"{API_BASE_URL}/api/chat-history/{DOCUMENT_ID}")
        
        print(f"Database API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Database chat history works!")
            print(f"Database response: {result}")
            return True
        else:
            print(f"Database API Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"Database API Note: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Chat History Retrieval")
    print("=" * 50)
    
    # Test both endpoints
    api_result = test_chat_history_retrieval()
    db_result = test_database_chat_history()
    
    print("\n" + "=" * 50)
    print("📊 CHAT HISTORY TEST SUMMARY")
    print(f"API Chat History:      {'✅ PASS' if api_result else '❌ FAIL'}")
    print(f"Database Chat History: {'✅ PASS' if db_result else '❌ FAIL'}")
    
    if api_result or db_result:
        print("\n🎉 Chat history retrieval is working!")
        print("✅ The document ID synchronization fix is successful!")
    else:
        print("\n⚠️  Chat history retrieval needs investigation")
