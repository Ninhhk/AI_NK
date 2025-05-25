"""
System prompt management for AI models.
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class SystemPromptManager:
    """
    Manages system prompts for AI models.
    Provides functionality to get, set, and apply system prompts to model inputs.
    """
      # Default system prompt if none is set
    DEFAULT_SYSTEM_PROMPT = """\\no_think must answer in vietnamese, phải trả lời bằng tiếng việt"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the system prompt manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses the default path.
        """
        if config_path is None:
            # Use default location
            self.config_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            self.config_path = self.config_dir / "system_prompt_config.json"
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent
        
        # Ensure the directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "system_prompt": self.DEFAULT_SYSTEM_PROMPT,
                    "variables": {}
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading system prompt config: {str(e)}")
            # Return default config if loading fails
            return {
                "system_prompt": self.DEFAULT_SYSTEM_PROMPT,
                "variables": {}
            }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving system prompt config: {str(e)}")
    
    def get_system_prompt(self) -> str:
        """Get the current system prompt."""
        return self.config.get("system_prompt", self.DEFAULT_SYSTEM_PROMPT)
    
    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        self.config["system_prompt"] = prompt
        self._save_config(self.config)
    
    def apply_system_prompt(self, prompt: str, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Apply the system prompt to the user prompt.
        
        Args:
            prompt: The user prompt
            variables: Optional variables to replace in the system prompt
        
        Returns:
            The combined prompt with system instructions
        """
        system_prompt = self.get_system_prompt()
        
        # Create default variables dictionary if not provided
        if variables is None:
            variables = {}
        
        # Add some default variables if they don't exist
        default_variables = {
            "topic": "presentation",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "custom_instructions": ""
        }
        
        # Only add default variables if they're not already specified
        for key, value in default_variables.items():
            if key not in variables:
                variables[key] = value
        
        # If custom_instructions are provided, prepend them to the system prompt
        if variables.get("custom_instructions"):
            custom_instructions = variables.get("custom_instructions")
            system_prompt = f"{custom_instructions}\n\n{system_prompt}"
            logger.debug(f"Added custom instructions ({len(str(custom_instructions))} chars) to system prompt")
          # Replace variables in the system prompt
        for key, value in variables.items():
            system_prompt = system_prompt.replace(f"{{{{{key}}}}}", str(value))
        
        # Combine system prompt with user prompt - put system prompt at beginning for emphasis
        combined_prompt = f"{system_prompt}\n\n{prompt}"
        logger.debug(f"Applied system prompt with {len(variables)} variables")
        
        return combined_prompt

# Create a global instance for application-wide use
system_prompt_manager = SystemPromptManager()