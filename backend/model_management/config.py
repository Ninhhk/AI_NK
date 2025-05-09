"""Model configuration module."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Ollama API base URL
OLLAMA_API_BASE_URL = "http://localhost:11434"

# Maximum allowed parallel downloads
MAX_PARALLEL_DOWNLOADS = 3

class ModelInfo(BaseModel):
    """Model information."""
    name: str
    modified_at: str
    size: int
    digest: str
    details: Optional[Dict[str, Any]] = None

class ModelDownloadProgress(BaseModel):
    """Model download progress information."""
    model: str
    digest: Optional[str] = None
    pull_progress: Optional[int] = None  # 0-1000 (per mille for precision)
    done: bool = False
    error: Optional[str] = None
