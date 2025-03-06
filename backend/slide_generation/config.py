from typing import Dict, Any
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "slides"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ollama Configuration
OLLAMA_CONFIG: Dict[str, Any] = {
    "model_name": "qwen2.5:7b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "max_tokens": 2000,
}

# Slide Generation Settings
MAX_SLIDES = 10
SLIDE_TEMPLATE = "default"  # or "modern", "classic", etc.
DEFAULT_TITLE = "Generated Presentation"

# Supported Output Formats
SUPPORTED_FORMATS = [".pptx", ".pdf"]

PROMPT = """
Generate a presentation outline for the given topic. The output should be a JSON array of slide objects.
Each slide should have a 'title' and 'content' field. The content should be in bullet points (use '-' for bullets).
Keep it concise and clear.

Example format:
[
    {"title": "Introduction", "content": ["- Key point 1", "- Key point 2"]},
    {"title": "Main Topic", "content": ["- Detail 1", "- Detail 2", "- Detail 3"]}
]

Guidelines:
1. Each bullet point should be limited to 10 words
2. Maximum 5 bullet points per slide
3. First slide should be an introduction
4. Last slide should be a summary or conclusion
5. Keep the language clear and professional
"""