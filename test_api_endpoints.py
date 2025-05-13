"""
Test all API endpoints for the system prompt
"""
import requests
import json
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def test_api_endpoints():
    """Test all API endpoints for the system prompt"""
    print(f"Testing API endpoints with base URL: {API_BASE_URL}")
    
    endpoints = [
        f"{API_BASE_URL}/api",
        f"{API_BASE_URL}/api/slides",
        f"{API_BASE_URL}/api/documents",
        f"{API_BASE_URL}/api/ollama",
        f"{API_BASE_URL}/api/slides/system-prompt",
        f"{API_BASE_URL}/api/documents/system-prompt",
        f"{API_BASE_URL}/api/ollama/system-prompt",
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing GET: {endpoint}")
            response = requests.get(endpoint)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text[:100]}...")
            else:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error accessing {endpoint}: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    test_api_endpoints()
