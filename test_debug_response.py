#!/usr/bin/env python3
"""
Debug test to see exactly what the backend is returning
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_debug_response():
    """Test to see the exact response from document analysis"""
    print("=== Debug Document Analysis Response ===")
    
    files = {
        "file": ("debug_test.txt", "This is a debug test document.", "text/plain")
    }
    
    data = {
        "query_type": "summary",
        "model_name": "qwen3:4b"
    }
    
    print("Making request to backend...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/documents/analyze", files=files, data=data)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("=== Full Response JSON ===")
            print(json.dumps(result, indent=2))
            
            print("\n=== Response Analysis ===")
            print(f"Keys in response: {list(result.keys())}")
            for key, value in result.items():
                print(f"  {key}: {type(value)} = {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_debug_response()
