from typing import Dict, Any

# Ollama Configuration
OLLAMA_CONFIG = {
    "model_name": "gemma3:1b",
    "base_url": "http://localhost:11434",
    "temperature": 0.1
}

# Document Analysis Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000

# Supported File Types
SUPPORTED_FILE_TYPES = [".pdf", ".txt", ".doc", ".docx"]

# Chat History Settings
CHAT_HISTORY_ENABLED = True
MAX_CHAT_HISTORY_ITEMS = 50

# Language Settings
FORCE_VIETNAMESE = True
LANGUAGE_DETECTION_CONFIDENCE = 0.7  # Minimum confidence for language detection 