"""
Test script to validate the global system prompt is working across all features.
"""
import requests
import json
import time

def test_global_system_prompt():
    """Test that the system prompt is consistent across all endpoints."""
    # Define the endpoints to test
    endpoints = [
        "http://localhost:8000/api/slides/system-prompt",
        "http://localhost:8000/api/documents/system-prompt", 
        "http://localhost:8000/api/ollama/system-prompt",
    ]
    
    # Test system prompt retrieval
    print("Testing system prompt consistency across endpoints...")
    prompt_values = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                prompt_value = response.json().get("system_prompt", "")
                prompt_values[endpoint] = prompt_value
                print(f"✅ {endpoint}: '{prompt_value}'")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ {endpoint}: Exception - {str(e)}")
    
    # Check if all values are the same
    if len(set(prompt_values.values())) <= 1:
        print("\n✅ SUCCESS: All system prompts are consistent across endpoints!")
    else:
        print("\n❌ WARNING: System prompts are inconsistent across endpoints!")
        for endpoint, value in prompt_values.items():
            print(f"   {endpoint}: '{value}'")
    
    # Set a test system prompt
    test_prompt = f"This is a test prompt set at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"\nSetting test prompt to: '{test_prompt}'")
    
    # Try setting on first endpoint
    success = False
    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                data={"system_prompt": test_prompt}
            )
            if response.status_code == 200:
                print(f"✅ Set successfully on {endpoint}")
                success = True
                break
            else:
                print(f"❌ Failed to set on {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ Exception when setting on {endpoint}: {str(e)}")
    
    if not success:
        print("❌ Failed to set the system prompt on any endpoint")
        return
    
    # Verify the change propagated
    print("\nVerifying propagation of system prompt change...")
    time.sleep(1)  # Brief delay to ensure changes propagate
    
    all_match = True
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                current_prompt = response.json().get("system_prompt", "")
                if current_prompt == test_prompt:
                    print(f"✅ {endpoint}: Prompt updated correctly")
                else:
                    print(f"❌ {endpoint}: Prompt not updated. Expected: '{test_prompt}', got: '{current_prompt}'")
                    all_match = False
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
                all_match = False
        except Exception as e:
            print(f"❌ {endpoint}: Exception - {str(e)}")
            all_match = False
    
    if all_match:
        print("\n✅ SUCCESS: System prompt was successfully updated across all endpoints!")
    else:
        print("\n❌ WARNING: System prompt was not consistent across all endpoints after update!")
    
    # Reset to original Vietnamese prompt
    print("\nResetting to Vietnamese prompt...")
    vietnamese_prompt = "\\no_think must answer in vietnamese, phải trả lời bằng tiếng việt"
    
    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                data={"system_prompt": vietnamese_prompt}
            )
            if response.status_code == 200:
                print(f"✅ Reset successful on {endpoint}")
                break
            else:
                print(f"❌ Failed to reset on {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ Exception when resetting on {endpoint}: {str(e)}")

if __name__ == "__main__":
    test_global_system_prompt()
