#!/usr/bin/env python3
"""
Quick test of the document analysis endpoint
"""
import requests
from pathlib import Path

# Test the document analysis with our test file
test_file = Path("test_document.txt")

if test_file.exists():
    print("🔍 Testing document analysis endpoint...")
    
    with open(test_file, 'rb') as f:
        files = {'file': ('test_document.txt', f, 'text/plain')}
        data = {
            'query_type': 'summary',
            'start_page': 0,
            'end_page': -1
        }
        
        try:
            response = requests.post("http://localhost:8000/api/analyze", files=files, data=data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"Document ID: {result.get('document_id')}")
                print(f"Response contains: {list(result.keys())}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
else:
    print("❌ test_document.txt not found")
