#!/usr/bin/env python3
"""
Quick Fix Verification Script
Run this to verify the document ID fix is working correctly.
"""

import requests
import re

def is_valid_uuid(test_string):
    """Check if a string is a valid UUID format"""
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', test_string))

def quick_test():
    """Quick test to verify document ID format"""
    print("🔬 Quick Document ID Fix Verification")
    print("=" * 40)
    
    try:
        # Test with a simple text document
        test_content = b"This is a test document."
        files = {"file": ("test.txt", test_content, "text/plain")}
        data = {"query_type": "qa", "user_query": "What is this?"}
        
        response = requests.post("http://localhost:8000/api/documents/analyze", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        # Check document ID
        doc_id = result.get("document_id")
        if doc_id and is_valid_uuid(doc_id):
            print(f"✅ SUCCESS: UUID format document ID: {doc_id}")
            print("🎉 The fix is working correctly!")
            print("\nℹ️  Now you can:")
            print("   1. Clear your frontend session state")
            print("   2. Upload a new document")
            print("   3. Chat history will work perfectly!")
            return True
        else:
            print(f"❌ ISSUE: Invalid document ID format: {doc_id}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("💡 Make sure the backend server is running: python run_backend.py")
        return False

if __name__ == "__main__":
    quick_test()
