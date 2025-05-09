from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
from fastapi.responses import JSONResponse

from backend.slide_generation.slide_service import SlideGenerationService

router = APIRouter()

# Initialize the slide service
slide_service = SlideGenerationService(
    model_name=os.getenv("MODEL_NAME", "gemma3:1b"),
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
    documents: Optional[List[UploadFile]] = File(None)
) -> Dict[str, Any]:
    """
    Generate slides based on the given topic and optional documents.
    
    Parameters:
    - topic: The main topic for the presentation
    - num_slides: Number of slides to generate (default: 10, min: 1, max: 20)
    - model_name: Optional Ollama model name to use for generation
    - documents: Optional list of file uploads to provide additional context (PDF, DOCX, or TXT)
    
    Returns:
    - A dictionary containing an array of slides with titles and content
    """
    try:
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
                except Exception as e:                    raise HTTPException(
                        status_code=400,
                        detail=f"Error parsing document {doc.filename}: {str(e)}"
                    )
            # Combine all parsed texts into one context
            document_content = "\n\n".join(parsed_texts)
        
        result = slide_service.generate_slides(
            topic=topic,
            num_slides=num_slides,
            document_content=document_content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    - A dictionary containing the updated model name
    """
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