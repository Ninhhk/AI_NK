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
import time

from langchain_community.llms import Ollama
from PyPDF2 import PdfReader
import docx
from .pptx_generator import PowerPointGenerator

from .config import OLLAMA_CONFIG, PROMPT, OUTPUT_DIR
from backend.model_management.global_model_config import global_model_config
from backend.model_management.system_prompt_manager import system_prompt_manager

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
    for i, slide in enumerate(slides_data):
        cleaned_slide = {}
        
        # Ensure there's a title field
        if "title" not in slide and "title_text" not in slide:
            cleaned_slide["title_text"] = f"Slide {i + 1}"
        
        # Process all other fields
        for key, value in slide.items():
            if isinstance(value, str):
                if contains_chinese(value):
                    logger.warning(f"Found Chinese characters in {key}, cleaning...")
                    value = sanitize_text(value)
                cleaned_slide[key] = value
            else:
                cleaned_slide[key] = value
        
        # Convert "title" to "title_text" if needed
        if "title" in cleaned_slide and "title_text" not in cleaned_slide:
            cleaned_slide["title_text"] = cleaned_slide.pop("title")
            
        # Ensure content exists
        if "content" not in cleaned_slide:
            cleaned_slide["content"] = ["- No content available"]
            
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
    
    def generate_slides(self, topic: str, num_slides: int, document_content: Optional[str] = None, system_prompt: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """Generate slides for a given topic.
        
        Args:
            topic: The topic to generate slides about
            num_slides: Number of slides to generate
            document_content: Optional content from uploaded document to use as context
            system_prompt: Optional custom system prompt to override the default
            
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
            
            # Try up to 3 times with increasing timeout/different approaches
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Add a slight delay between attempts
                    if attempt > 0:
                        time.sleep(1)  # Wait 1 second between retries
                    
                    # On later attempts, try to be more explicit about requiring valid JSON
                    if attempt > 0:
                        # Add a stronger reminder to provide valid JSON
                        enhanced_prompt = prompt + f"\n\nIMPORTANT: Your response must be ONLY a valid JSON array. No explanations, no additional text. ONLY valid JSON array like: [{{'title': 'Title', 'content': ['- Point 1', '- Point 2']}}]"
                        response = self._invoke_model(enhanced_prompt, system_prompt)
                    else:
                        response = self._invoke_model(prompt, system_prompt)
                    
                    # Parse and validate JSON - catch potential issues early
                    try:
                        slides_data = json.loads(response)
                    except json.JSONDecodeError as json_error:
                        logger.error(f"JSON decode error: {str(json_error)}")
                        if attempt == max_attempts - 1:
                            # On last attempt, create a fallback array
                            slides_data = [
                                {"title": "Error in Generation", "content": ["- Error generating slides", "- Please try again with a different model or topic"]},
                                {"title": "Topic Information", "content": [f"- Topic: {topic}", "- The AI model could not generate proper content"]}
                            ]
                        else:
                            # Try next attempt
                            raise
                    
                    # Handle empty array
                    if not slides_data or len(slides_data) == 0:
                        if attempt == max_attempts - 1:
                            slides_data = [
                                {"title": "Error in Generation", "content": ["- Error generating slides", "- Please try again with a different model or topic"]}
                            ]
                        else:
                            raise ValueError("Model returned empty slides array")
                    
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
                            
                            # If still no title, add a default one
                            if "title_text" not in slide:
                                slide["title_text"] = f"Slide {slides_data.index(slide) + 1}"
                        
                        # Convert "content" list to "text" string for PowerPoint compatibility
                        if "content" in slide and isinstance(slide["content"], list) and "text" not in slide:
                            slide["text"] = "\n".join(slide["content"])
                            logger.debug(f"Converted content list to text string: {slide['text']}")
                        
                        # Ensure each slide has content
                        if "content" not in slide and "text" not in slide:
                            slide["content"] = ["- No content available"]
                            slide["text"] = "- No content available"
                    
                    logger.info(f"Successfully generated slides on attempt {attempt + 1}")
                    
                    # Save the slides without returning the path
                    try:
                        self._save_slides(topic, {"slides": slides_data})
                    except Exception as save_error:
                        logger.error(f"Error saving slides: {str(save_error)}")
                        # Continue even if saving fails
                    
                    # Return only the slides data
                    return {"slides": slides_data}
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_attempts - 1:
                        # On last attempt failure, return simple fallback slides
                        fallback_slides = [
                            {"title_text": "Error in Generation", "content": ["- Error generating slides", "- Please try again with a different model or topic"], "text": "- Error generating slides\n- Please try again with a different model or topic"},
                            {"title_text": "Topic Information", "content": [f"- Topic: {topic}", "- The AI model encountered issues"], "text": f"- Topic: {topic}\n- The AI model encountered issues"}
                        ]
                        
                        # Try to save these fallback slides
                        try:
                            self._save_slides(topic, {"slides": fallback_slides})
                        except:
                            pass
                            
                        # Return fallback slides
                        return {"slides": fallback_slides}
                    continue
        except Exception as e:
            logger.error(f"Error in generate_slides: {str(e)}", exc_info=True)
            # Return minimal fallback slides instead of raising
            fallback_slides = [
                {"title_text": "Error in Generation", "content": ["- Error generating slides", "- Please try again with a different model or topic"], "text": "- Error generating slides\n- Please try again with a different model or topic"}
            ]
            return {"slides": fallback_slides}

    def _invoke_model(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Invoke the Ollama model with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            system_prompt: Optional custom system prompt to override the default
        
        Returns:
            Model response as a string
        """
        try:
            # Apply system prompt if available, otherwise use the default
            if system_prompt is not None:
                # Use the provided system prompt
                final_prompt = system_prompt_manager.apply_system_prompt(prompt, variables={"topic": "presentation"})
                logger.debug("Using provided system prompt")
            else:
                # Use the default system prompt from the manager
                final_prompt = system_prompt_manager.apply_system_prompt(prompt, variables={"topic": "presentation"})
                logger.debug("Using default system prompt")
            
            # Use the LangChain Ollama wrapper to invoke the model
            response_text = self.llm(final_prompt)
            
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
            
            # Advanced JSON extraction and cleaning
            try:
                # First try with the cleaned text as is
                json.loads(response_text)
            except json.JSONDecodeError:
                # More aggressive JSON extraction
                try:
                    # Look for array start and end
                    start_idx = response_text.find("[")
                    end_idx = response_text.rfind("]")
                    
                    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                        # Extract what looks like a JSON array
                        extracted_json = response_text[start_idx:end_idx+1]
                        
                        # Try to parse the extracted JSON
                        try:
                            json.loads(extracted_json)
                            response_text = extracted_json
                        except json.JSONDecodeError:
                            # Try to fix common JSON issues
                            fixed_json = self._fix_json_format(extracted_json)
                            json.loads(fixed_json)  # Validate it parses correctly
                            response_text = fixed_json
                    else:
                        # If we can't find proper array markers, try to reconstruct a basic array
                        logger.warning("Couldn't find proper JSON array markers, attempting to fix format")
                        response_text = self._fix_json_format(response_text)
                        try:
                            json.loads(response_text)  # Validate the fixed format
                        except json.JSONDecodeError:
                            # Last resort: return a minimal valid slide array
                            logger.error("Failed to fix JSON format, returning fallback content")
                            return '[{"title": "Error in Generation", "content": ["- Error in slide generation", "- Please try again with a different model or topic"]}]'
                except Exception as json_fix_error:
                    # Log detailed debug info
                    logger.error(f"Could not fix JSON format: {str(json_fix_error)}")
                    logger.debug(f"Raw response text: {response_text}")
                    
                    # Create a fallback array with an error slide if everything else fails
                    logger.warning("Creating fallback slide content")
                    return '[{"title": "Error in Generation", "content": ["- Error in slide generation", "- Please try again with a different model or topic"]}]'
            
            # Extra validation - make sure we have an array with at least one object
            try:
                parsed_data = json.loads(response_text)
                if not isinstance(parsed_data, list) or len(parsed_data) == 0:
                    logger.warning("Response is not a proper array or is empty, creating fallback")
                    return '[{"title": "Error in Generation", "content": ["- Error in slide generation", "- Please try again with a different model or topic"]}]'
                
                # Validate that all slides have at least one of title or content
                for slide in parsed_data:
                    if not isinstance(slide, dict):
                        continue
                    if not ('title' in slide or 'title_text' in slide or 'content' in slide):
                        logger.warning(f"Found invalid slide without title or content: {slide}")
            except:
                # If any validation fails, use the fallback
                return '[{"title": "Error in Generation", "content": ["- Error in slide generation", "- Please try again with a different model or topic"]}]'
            
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to invoke model: {str(e)}")
            # Return a minimal valid JSON array as fallback instead of raising an exception
            return '[{"title": "Error in Generation", "content": ["- Error in slide generation", "- Please try again with a different model or topic"]}]'
    
    def _fix_json_format(self, text: str) -> str:
        """Attempt to fix common JSON formatting issues in model output."""
        # Replace single quotes with double quotes for JSON compatibility
        text = text.replace("'", '"')
        
        # Look for slide-like structures and convert to proper JSON
        if '[' not in text and '{' in text:
            # Find all individual slide objects
            slide_objects = []
            open_braces = 0
            start_idx = -1
            
            for i, char in enumerate(text):
                if char == '{' and open_braces == 0:
                    start_idx = i
                    open_braces += 1
                elif char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                    if open_braces == 0 and start_idx != -1:
                        slide_objects.append(text[start_idx:i+1])
                        start_idx = -1
            
            # If we found slide objects, wrap them in an array
            if slide_objects:
                return '[' + ','.join(slide_objects) + ']'
            
        # If text contains unbalanced quotes, try to fix them
        quote_count = text.count('"')
        if quote_count % 2 != 0:
            # Find and fix unbalanced quotes
            in_quotes = False
            new_text = []
            
            for char in text:
                if char == '"':
                    in_quotes = not in_quotes
                new_text.append(char)
            
            # If we ended up with an open quote, close it
            if in_quotes:
                new_text.append('"')
                
            text = ''.join(new_text)
        
        # If there's no array wrapper, add it
        if not text.strip().startswith('['):
            text = '[' + text.strip()
        if not text.strip().endswith(']'):
            text = text.strip() + ']'
            
        return text

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
