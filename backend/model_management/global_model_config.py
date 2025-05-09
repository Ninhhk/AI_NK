"""Global model configuration manager for consistent model selection across services."""
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlobalModelConfig:
    """Singleton class to manage model configuration globally across all services."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalModelConfig, cls).__new__(cls)
            cls._instance._model_name = None
        return cls._instance
    
    def set_model(self, model_name: str) -> None:
        """Set the global model name."""
        if model_name != self._model_name:
            self._model_name = model_name
            logger.info(f"Global model changed to {model_name}")
    
    def get_model(self) -> Optional[str]:
        """Get the currently selected global model name."""
        return self._model_name

# Global singleton instance
global_model_config = GlobalModelConfig()
