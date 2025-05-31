from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
from fastapi.responses import JSONResponse
import logging

from backend.slide_generation.slide_service import SlideGenerationService
from backend.model_management.system_prompt_manager import system_prompt_manager

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the slide service
slide_service = SlideGenerationService(
    model_name=os.getenv("MODEL_NAME", "qwen3:8b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)

class SlideContent(BaseModel):
    title_text: str
    text: Optional[str] = None
    is_title_slide: Optional[str] = None

class SlideRequest(BaseModel):
    topic: str = Field(..., description="The topic to generate slides about", example="Artificial Intelligence")
    num_slides: int = Field(default=5, ge=1, le=20, description="Number of slides to generate")
    model_name: Optional[str] = Field(None, description="The Ollama model to use")

class SlideResponse(BaseModel):
    slides: List[SlideContent]

@router.post("/generate", response_model=SlideResponse)
async def generate_slides(
    topic: str = Form(...),
    num_slides: int = Form(10),
    model_name: Optional[str] = Form(None),
    documents: Optional[List[UploadFile]] = File(None),
    system_prompt: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Generate slides based on the given topic and optional documents.
    
    Parameters:
    - topic: The main topic for the presentation
    - num_slides: Number of slides to generate (default: 10, min: 1, max: 20)
    - model_name: Optional Ollama model name to use for generation
    - documents: Optional list of file uploads to provide additional context (PDF, DOCX, or TXT)
    - system_prompt: Optional custom system prompt to use for generation
    
    Returns:
    - A dictionary containing an array of slides with titles and content
    """
    try:
        # Validate num_slides
        num_slides = max(1, min(20, num_slides))  # Ensure between 1 and 20
        
        # Set model if provided
        if model_name:
            slide_service.set_model(model_name)
            
        document_content = None
        if documents:
            parsed_texts = []
            for doc in documents:
                file_content = await doc.read()
                file_type = doc.filename.split('.')[-1].lower()
                try:
                    text = slide_service.parse_document(file_content, file_type)
                    parsed_texts.append(f"---\nDocument: {doc.filename}\n{text}")
                except Exception as e:
                    # Log the error but continue with other documents
                    logger.error(f"Error parsing document {doc.filename}: {str(e)}")
                    parsed_texts.append(f"---\nDocument: {doc.filename}\nError parsing document: {str(e)}")
            
            # Combine all parsed texts into one context
            document_content = "\n\n".join(parsed_texts)          # Call the slide generation service
        result = slide_service.generate_slides(
            topic=topic,
            num_slides=num_slides,
            document_content=document_content,
            system_prompt=system_prompt
        )
        
        # Validate the result
        if not result or "slides" not in result:
            # Create a fallback response
            fallback_slides = [
                {"title_text": "Error in Generation", "content": ["- Error generating slides", "- Please try again with a different model or topic"], "text": "- Error generating slides\n- Please try again with a different model or topic"}
            ]
            return {"slides": fallback_slides}
            
        # Ensure all slides have the required fields to match the SlideContent model
        for i, slide in enumerate(result["slides"]):
            if "title_text" not in slide:
                # Add a default title if missing
                logger.warning(f"Slide {i} missing title_text, adding default")
                slide["title_text"] = f"Slide {i + 1}"
            
            # Ensure text field exists
            if "text" not in slide and "content" in slide and isinstance(slide["content"], list):
                slide["text"] = "\n".join(slide["content"])
            elif "text" not in slide:
                slide["text"] = "No content available"
        
        return result
    except Exception as e:
        logger.exception(f"Error generating slides: {str(e)}")
        # Return a more graceful error response instead of raising an exception
        fallback_slides = [
            {"title_text": "Error in Generation", "content": ["- Error generating slides", "- Please try again with a different model or topic"], "text": "- Error generating slides\n- Please try again with a different model or topic"},
            {"title_text": "Technical Information", "content": [f"- Error: {str(e)}", "- Please check server logs for details"], "text": f"- Error: {str(e)}\n- Please check server logs for details"}
        ]
        return {"slides": fallback_slides}

@router.get("/current-model")
async def get_current_model() -> Dict[str, str]:
    """
    Get the current model being used for slide generation.
    
    Returns:
    - A dictionary containing the current model name
    """
    return {"model_name": slide_service.get_current_model()}

@router.post("/set-model")
async def set_model(model_name: str = Form(...)) -> Dict[str, str]:
    """
    Set the model to use for slide generation.
    
    Parameters:
    - model_name: The name of the Ollama model to use
    
    Returns:
    - A dictionary containing the updated model name    """
    try:
        slide_service.set_model(model_name)
        return {"model_name": model_name, "message": f"Model changed to {model_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    """
    return {"status": "healthy"}

@router.get("/system-prompt")
async def get_system_prompt() -> Dict[str, str]:
    """
    Get the current system prompt used for slide generation.
    
    Returns:
    - A dictionary containing the current system prompt
    """
    return {"system_prompt": system_prompt_manager.get_system_prompt()}

@router.post("/system-prompt")
async def set_system_prompt(system_prompt: str = Form(...)) -> Dict[str, str]:
    """
    Set the system prompt to use for slide generation.
    
    Parameters:
    - system_prompt: The system prompt to set
    
    Returns:
    - A dictionary containing the updated system prompt
    """
    try:
        system_prompt_manager.set_system_prompt(system_prompt)
        return {"system_prompt": system_prompt, "message": "System prompt updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))