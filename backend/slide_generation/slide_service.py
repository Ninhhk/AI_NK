import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging
import re
import unicodedata
import io

from langchain_community.llms import Ollama
from PyPDF2 import PdfReader
import docx
from .pptx_generator import PowerPointGenerator

from .config import OLLAMA_CONFIG, PROMPT, OUTPUT_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_chinese(char: str) -> bool:
    """Check if a character is Chinese."""
    try:
        return 'CJK' in unicodedata.name(char)
    except ValueError:
        return False

def contains_chinese(text: str) -> bool:
    """Check if text contains any Chinese characters."""
    return any(is_chinese(char) for char in text)

def sanitize_text(text: str) -> str:
    """Remove Chinese characters and clean up text."""
    # Remove Chinese characters
    cleaned = ''.join(char for char in text if not is_chinese(char))
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Remove multiple newlines
    cleaned = re.sub(r'\n+', '\\n', cleaned)
    return cleaned.strip()

def validate_slide_content(slides_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and clean slide content."""
    cleaned_slides = []
    for slide in slides_data:
        cleaned_slide = {}
        for key, value in slide.items():
            if isinstance(value, str):
                if contains_chinese(value):
                    logger.warning(f"Found Chinese characters in {key}, cleaning...")
                    value = sanitize_text(value)
                cleaned_slide[key] = value
            else:
                cleaned_slide[key] = value
        cleaned_slides.append(cleaned_slide)
    return cleaned_slides

def _sanitize_filename(name: str) -> str:
    # Remove invalid characters and truncate if too long
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Limit to 256 characters to ensure compatibility with most filesystems
    return sanitized[:100]  # Windows and most Unix filesystems have a 255-260 character limit

class SlideGenerationService:
    def __init__(self, model_name: str = OLLAMA_CONFIG["model_name"], base_url: str = OLLAMA_CONFIG["base_url"]):
        self.model_name = model_name
        self.base_url = base_url
        self.llm = self._initialize_model()
        self.pptx_generator = PowerPointGenerator()
        logger.info(f"Initialized SlideGenerationService with model {model_name} at {base_url}")
        
    def _initialize_model(self) -> Ollama:
        return Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=OLLAMA_CONFIG["temperature"]
        )
    
    def parse_document(self, file_content: bytes, file_type: str) -> str:
        """Parse document content based on file type."""
        if file_type == 'pdf':
            return self._parse_pdf(file_content)
        elif file_type == 'docx':
            return self._parse_docx(file_content)
        elif file_type in ['txt', 'text']:
            return self._parse_txt(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _parse_pdf(self, file_content: bytes) -> str:
        """Extract text from a PDF file."""
        with io.BytesIO(file_content) as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Some pages might not have extractable text
                    text += page_text + "\n\n"
            return text

    def _parse_docx(self, file_content: bytes) -> str:
        """Extract text from a DOCX file."""
        with io.BytesIO(file_content) as f:
            doc = docx.Document(f)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
            return text

    def _parse_txt(self, file_content: bytes) -> str:
        """Extract text from a TXT file."""
        # Try to decode with UTF-8 first, fall back to other encodings if needed
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('utf-16')
            except UnicodeDecodeError:
                try:
                    return file_content.decode('cp1258')  # Vietnamese encoding
                except UnicodeDecodeError:
                    return file_content.decode('utf-8', errors='replace')
    
    def generate_slides(self, topic: str, num_slides: int, document_content: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """Generate slides for a given topic.
        
        Args:
            topic: The topic to generate slides about
            num_slides: Number of slides to generate
            document_content: Optional content from uploaded document to use as context
            
        Returns:
            Dictionary containing the generated slides
        """
        try:
            logger.info(f"Generating {num_slides} slides about topic: {topic}")
            
            # Add document content to the prompt if available
            additional_context = ""
            if document_content and document_content.strip():
                # Extract a reasonable amount of text (first 4000 characters)
                truncated_content = document_content[:4000] + "..." if len(document_content) > 4000 else document_content
                additional_context = f"""
Use information from the following document to enhance the slides:
---
{truncated_content}
---
Reference this document content when creating the slides. Use relevant facts, figures, and information from the document.
"""
            
            prompt = f"""Generate {num_slides} Vietnamese slides about {topic}. Your response MUST be a valid JSON array with the following structure:

[
    {{
        "is_title_slide": "yes",
        "title_text": "Title of the presentation"
    }},
    {{
        "title_text": "Title of slide 1",
        "text": "Content of slide 1 with bullet points"
    }},
    {{
        "title_text": "Title of slide 2", 
        "text": "Content of slide 2 with bullet points"
    }}
]

{additional_context}

RULES:
1. You MUST create exactly {num_slides} slides total (including title slide)
2. The response must be valid JSON
3. No text should precede or follow the JSON array
4. The first slide must be a title slide with is_title_slide="yes"
5. Each subsequent slide must have title_text and text fields
6. Content should be concise and use bullet points
7. No markdown formatting or explanatory text
8. Maximum 5 bullet points per slide
9. Each bullet point should be limited to 10 words
10. Use \\n for line breaks in text content
11. DO NOT use any Chinese characters
12. Use only Vietnamese or English characters

Example response:
[
    {{
        "is_title_slide": "yes",
        "title_text": "Giới thiệu về AI"
    }},
    {{
        "title_text": "AI là gì?",
        "text": "• Định nghĩa: AI là trí tuệ nhân tạo\\n• Điểm chính:\\n  - Máy học từ kinh nghiệm\\n  - Tự cải thiện\\n  - Hiểu ngôn ngữ tự nhiên"
    }}
]"""

            # Try up to 3 times to get valid response
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self._invoke_model(prompt)
                    
                    # Parse and validate JSON
                    slides_data = json.loads(response)
                    
                    # Clean and validate content
                    slides_data = validate_slide_content(slides_data)
                    
                    # Check for any remaining Chinese characters
                    json_str = json.dumps(slides_data, ensure_ascii=False)
                    if contains_chinese(json_str):
                        logger.warning(f"Attempt {attempt + 1}: Found Chinese characters after cleaning, retrying...")
                        continue
                    
                    logger.info(f"Successfully generated clean slides on attempt {attempt + 1}")
                    
                    # Save the slides without returning the path
                    self._save_slides(topic, {"slides": slides_data})
                    
                    # Return only the slides data
                    return {"slides": slides_data}
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_attempts - 1:
                        raise
                    continue
                    
        except Exception as e:
            logger.error(f"Error in generate_slides: {str(e)}", exc_info=True)
            raise

    def _invoke_model(self, prompt: str) -> str:
        """Invoke the Ollama model with the given prompt."""
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API returned status {response.status_code}")
                
            response_data = response.json()
            response_text = response_data["response"]
            
            # Clean the response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Clean any Chinese characters from the response
            response_text = sanitize_text(response_text)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to call Ollama API: {str(e)}")
            raise

    def _save_slides(self, topic: str, slides_data: dict):
        """Save the generated slides as JSON and PPTX."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = _sanitize_filename(topic)
            safe_topic = safe_topic.replace(' ', '_')
            
            # Create output directory if it doesn't exist
            output_dir = Path("output/slides")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save JSON file
            json_path = output_dir / f"{safe_topic}_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(slides_data, f, ensure_ascii=False, indent=2)
            
            # Generate and save PPTX file
            pptx_path = output_dir / f"{safe_topic}_{timestamp}.pptx"
            self.pptx_generator.generate_presentation(slides_data["slides"], pptx_path)
            
        except Exception as e:
            logger.error(f"Failed to save slides: {str(e)}")
            raise