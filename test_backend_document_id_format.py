#!/usr/bin/env python3
"""
Test to verify the backend is consistently generating UUID format document IDs
"""
import requests
import json
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

def is_hash_format(test_string):
    """Check if a string looks like an MD5 hash (32 hex characters)"""
    return bool(re.match(r'^[a-f0-9]{32}$', test_string))

def test_backend_document_ids():
    """Test that backend consistently generates UUID format document IDs"""
    print("🧪 Testing Backend Document ID Format")
    print("=" * 50)
    
    test_content = """
    This is a test document to verify document ID generation.
    The backend should consistently generate UUID format document IDs.
    """
    
    # Test multiple times to ensure consistency
    for i in range(3):
        print(f"\n📤 Test {i+1}: Analyzing document...")
        
        try:
            files = {'file': (f'test_doc_{i+1}.txt', test_content.encode(), 'text/plain')}
            data = {
                'query_type': 'qa',
                'user_query': f'What is this document about? (Test {i+1})',
                'start_page': 0,
                'end_page': -1
            }
            
            response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                document_id = result.get('document_id')
                
                print(f"📋 Document ID: {document_id}")
                
                if document_id:
                    if is_valid_uuid(document_id):
                        print("✅ Valid UUID format")
                    elif is_hash_format(document_id):
                        print("❌ Hash format (OLD - should be UUID)")
                        return False
                    else:
                        print(f"⚠️  Unknown format: {document_id}")
                        return False
                else:
                    print("❌ No document_id in response")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error in test {i+1}: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🏆 RESULT: All tests passed!")
    print("✅ Backend consistently generates UUID format document IDs")
    return True

if __name__ == "__main__":
    success = test_backend_document_ids()
    if not success:
        print("\n❌ Backend document ID generation needs to be fixed!")
        exit(1)
    else:
        print("\n🎯 Backend is working correctly!")
