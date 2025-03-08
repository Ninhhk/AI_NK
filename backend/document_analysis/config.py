from typing import Dict, Any

# Ollama Configuration
OLLAMA_CONFIG = {
    "model_name": "qwen2.5:7b",
    "base_url": "http://localhost:11434",
    "temperature": 0.1
}

# Document Analysis Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000

# Supported File Types
SUPPORTED_FILE_TYPES = [".pdf", ".txt", ".doc", ".docx"] 