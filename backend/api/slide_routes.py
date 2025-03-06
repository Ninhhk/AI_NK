from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os

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
    request: SlideRequest = Body(
        ...,
        example={
            "topic": "Artificial Intelligence",
            "num_slides": 5
        }
    )
) -> Dict[str, Any]:
    """
    Generate Vietnamese slides based on the given topic.
    
    Parameters:
    - topic: The main topic for the presentation
    - num_slides: Number of slides to generate (default: 5, min: 1, max: 20)
    
    Returns:
    - A dictionary containing an array of slides with titles and content
    """
    try:
        result = slide_service.generate_slides(
            topic=request.topic,
            num_slides=request.num_slides
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