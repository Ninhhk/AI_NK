import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging
import re
import unicodedata
import io
import requests

from langchain_community.llms import Ollama
from PyPDF2 import PdfReader
import docx
from .pptx_generator import PowerPointGenerator

from .config import OLLAMA_CONFIG, PROMPT, OUTPUT_DIR
from backend.model_management.global_model_config import global_model_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_chinese(char: str) -> bool:
    """Check if a character is Chinese."""
    try:
        # Check specifically for Chinese range, excluding Vietnamese
        character_name = unicodedata.name(char)
        return "CJK" in character_name and not any(viet_name in character_name for viet_name in ["LATIN", "VIETNAMESE"])
    except ValueError:
        return False

def contains_chinese(text: str) -> bool:
    """Check if text contains any Chinese characters."""
    return any(is_chinese(char) for char in text)

def sanitize_text(text: str) -> str:
    """Remove unwanted characters and clean up text, preserving Vietnamese."""
    # Remove Chinese characters, but keep Vietnamese
    cleaned = "".join(char for char in text if not is_chinese(char))
    # Remove multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned)
    # Replace multiple newlines with a single one for readability
    cleaned = re.sub(r"\n+", "\n", cleaned)
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
    sanitized = re.sub(r"[<>:\"/\\|?*]", "_", name)
    # Limit to 256 characters to ensure compatibility with most filesystems
    return sanitized[:100]  # Windows and most Unix filesystems have a 255-260 character limit

class SlideGenerationService:
    def __init__(self, model_name: str = OLLAMA_CONFIG["model_name"], base_url: str = OLLAMA_CONFIG["base_url"]):
        # Check if a global model is set, and use it if available
        global_model = global_model_config.get_model()
        if global_model:
            model_name = global_model
            logger.info(f"Using globally configured model: {model_name}")
            
        self.model_name = model_name
        self.base_url = base_url
        self.llm = self._initialize_model()
        self.pptx_generator = PowerPointGenerator()
        logger.info(f"Initialized SlideGenerationService with model {model_name} at {base_url}")
        
    def _initialize_model(self) -> Ollama:
        # Check if a global model is set, and use it if available and different from current
        global_model = global_model_config.get_model()
        if global_model and global_model != self.model_name:
            self.model_name = global_model
            logger.info(f"Updating to globally configured model: {self.model_name}")
            
        return Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=OLLAMA_CONFIG["temperature"]
        )
    
    def set_model(self, model_name: str) -> None:
        """Change the model used for generation."""
        if model_name != self.model_name:
            self.model_name = model_name
            self.llm = self._initialize_model()
            
            # Update the global model configuration
            global_model_config.set_model(model_name)
            
            logger.info(f"Changed model to {model_name} and updated global config")
    
    def get_current_model(self) -> str:
        """Get the current model name."""
        # Always check global config first
        global_model = global_model_config.get_model()
        if global_model and global_model != self.model_name:
            # Update local model to match global model
            self.set_model(global_model)
            
        return self.model_name
    
    def parse_document(self, file_content: bytes, file_type: str) -> str:
        """Parse document content based on file type."""
        if file_type == "pdf":
            return self._parse_pdf(file_content)
        elif file_type == "docx":
            return self._parse_docx(file_content)
        elif file_type in ["txt", "text"]:
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
            return file_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return file_content.decode("utf-16")
            except UnicodeDecodeError:
                try:
                    return file_content.decode("cp1258")  # Vietnamese encoding
                except UnicodeDecodeError:
                    return file_content.decode("utf-8", errors="replace")
    
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
                # Log document size for debugging
                logger.debug(f"Document content length: {len(document_content)}")
                # Extract a reasonable amount of text (first 4000 characters)
                truncated_content = document_content[:4000] + "..." if len(document_content) > 4000 else document_content
                additional_context = f"Additional information from uploaded documents:\n{truncated_content}\n"
            
            # Construct the prompt, using the PROMPT template from config
            # Replace placeholders in the PROMPT template
            formatted_prompt = PROMPT.replace("{num_slides}", str(num_slides)).replace("{topic}", topic)
            
            # Add the document context at the beginning if available
            intro = additional_context + "\n" if additional_context else ""
            prompt = f"{intro}{formatted_prompt}"
            
            # Try up to 3 times to get valid response
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self._invoke_model(prompt)
                    
                    # Parse and validate JSON
                    slides_data = json.loads(response)
                    
                    # Clean and validate content
                    slides_data = validate_slide_content(slides_data)
                    
                    # Normalize slide dictionaries to use "title_text" for PPTX generator
                    for slide in slides_data:
                        # Map "title" to "title_text"
                        if "title_text" not in slide and "title" in slide:
                            slide["title_text"] = slide.pop("title")
                        # Fallback: use any other key (except "text" and "images") as title
                        if "title_text" not in slide:
                            for key in list(slide.keys()):
                                if key not in ("text", "images", "content"):
                                    slide["title_text"] = slide.pop(key)
                                    logger.debug(f"Falling back using \"{key}\" as title_text")
                                    break
                        
                        # Convert "content" list to "text" string for PowerPoint compatibility
                        if "content" in slide and isinstance(slide["content"], list) and "text" not in slide:
                            slide["text"] = "\n".join(slide["content"])
                            logger.debug(f"Converted content list to text string: {slide['text']}")
                    
                    logger.info(f"Successfully generated slides on attempt {attempt + 1}")
                    
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
        try:
            # Use the LangChain Ollama wrapper to invoke the model
            response_text = self.llm(prompt)
            
            # Clean the response text to extract valid JSON
            response_text = response_text.strip()
            
            # Remove any markdown code block markers
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            response_text = response_text.strip()
            
            # Log the cleaned response for debugging
            logger.debug(f"Cleaned response text (first 200 chars): {response_text[:200]}...")
            
            # Try to verify if it"s valid JSON
            try:
                json.loads(response_text)
            except json.JSONDecodeError as e:
                # If not valid JSON, try to extract JSON portion
                # Look for array start and end
                start_idx = response_text.find("[")
                end_idx = response_text.rfind("]")
                
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    # Extract what looks like a JSON array
                    response_text = response_text[start_idx:end_idx+1]
                    # Verify the extracted portion is valid JSON
                    json.loads(response_text)
                else:
                    # Could not extract valid JSON, log and raise
                    logger.error(f"Could not extract valid JSON: {str(e)}")
                    logger.debug(f"Response text: {response_text}")
                    raise ValueError(f"Model did not return valid JSON: {str(e)}")
                
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to invoke model: {str(e)}")
            raise Exception(f"Failed to invoke model: {str(e)}")

    def _save_slides(self, topic: str, slides_data: dict):
        """Save the generated slides as JSON and PPTX."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = _sanitize_filename(topic)
            safe_topic = safe_topic.replace(" ", "_")
            
            # Create output directory if it doesn"t exist
            output_dir = Path("output/slides")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save JSON file
            json_path = output_dir / f"{safe_topic}_{timestamp}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(slides_data, f, ensure_ascii=False, indent=2)
            
            # Generate and save PPTX file
            pptx_path = output_dir / f"{safe_topic}_{timestamp}.pptx"
            self.pptx_generator.generate_presentation(slides_data["slides"], pptx_path)
            
        except Exception as e:
            logger.error(f"Failed to save slides: {str(e)}")
            raise
