from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
from fastapi.responses import JSONResponse

from backend.slide_generation.slide_service import SlideGenerationService

router = APIRouter()

# Initialize the slide service
slide_service = SlideGenerationService(
    model_name=os.getenv("MODEL_NAME", "qwen2.5:7b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)

class SlideContent(BaseModel):
    title_text: str
    text: Optional[str] = None
    is_title_slide: Optional[str] = None

class SlideRequest(BaseModel):
    topic: str = Field(..., description="The topic to generate slides about", example="Artificial Intelligence")
    num_slides: int = Field(default=5, ge=1, le=20, description="Number of slides to generate")

class SlideResponse(BaseModel):
    slides: List[SlideContent]

@router.post("/generate", response_model=SlideResponse)
async def generate_slides(
    topic: str = Form(...),
    num_slides: int = Form(10),
    document: Optional[UploadFile] = None
) -> Dict[str, Any]:
    """
    Generate Vietnamese slides based on the given topic and optional document.
    
    Parameters:
    - topic: The main topic for the presentation
    - num_slides: Number of slides to generate (default: 10, min: 1, max: 20)
    - document: Optional file upload to provide additional context (PDF, DOCX, or TXT)
    
    Returns:
    - A dictionary containing an array of slides with titles and content
    """
    try:
        document_content = None
        
        if document:
            file_content = await document.read()
            file_type = document.filename.split('.')[-1].lower()
            
            try:
                document_content = slide_service.parse_document(file_content, file_type)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error parsing document: {str(e)}"
                )
        
        result = slide_service.generate_slides(
            topic=topic,
            num_slides=num_slides,
            document_content=document_content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    """
    return {"status": "healthy"}