"""
Set the default global system prompt.
"""
import requests
import json
import os
import logging
import time
import traceback
import sys

# Configure logging - output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# API Base URL (can be customized via environment variable)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def set_system_prompt():
    """Set the system prompt to Vietnamese response requirement."""
    try:
        # Print startup message
        logger.info("Starting system prompt update")
        logger.info(f"Using API base URL: {API_BASE_URL}")
        
        # The system prompt we want to set
        system_prompt = "\\no_think must answer in vietnamese, phải trả lời bằng tiếng việt"
        logger.info(f"Setting system prompt to: '{system_prompt}'")
        
        # List of all system prompt endpoints
        endpoints = [
            f"{API_BASE_URL}/api/slides/system-prompt",
            f"{API_BASE_URL}/api/documents/system-prompt", 
            f"{API_BASE_URL}/api/ollama/system-prompt",
        ]
        
        # Try to set via API for all endpoints
        success_count = 0
        for endpoint in endpoints:
            try:
                logger.info(f"Trying endpoint: {endpoint}")
                response = requests.post(
                    endpoint,
                    data={"system_prompt": system_prompt}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ System prompt set successfully via API: {endpoint}")
                    try:
                        logger.info(f"Response: {response.json()}")
                    except:
                        logger.info(f"Response: {response.text}")
                    success_count += 1
                else:
                    logger.warning(f"❌ Error setting system prompt via API: {endpoint} - Status: {response.status_code}")
                    logger.warning(f"Response: {response.text}")
            except Exception as e:
                logger.error(f"❌ Failed to reach API endpoint {endpoint}: {str(e)}")
                logger.error(traceback.format_exc())
        
        logger.info(f"Successfully updated {success_count} of {len(endpoints)} endpoints")
        
        # Also update the config file directly as a backup method
        project_root = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(project_root, "backend", "model_management", "system_prompt_config.json")
        logger.info(f"Updating config file at: {config_path}")
        
        config = {
            "system_prompt": system_prompt,
            "variables": {}
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        logger.info(f"✅ System prompt config updated at {config_path}")
        logger.info("System prompt update completed")
        
    except Exception as e:
        logger.error(f"Error in set_system_prompt: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    set_system_prompt()
