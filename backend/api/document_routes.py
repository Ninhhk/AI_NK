from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional, Dict, Any
import os

from backend.document_analysis.document_service import DocumentAnalysisService

router = APIRouter()

# Initialize the document service
document_service = DocumentAnalysisService(
    model_name=os.getenv("MODEL_NAME", "qwen2.5:7b"),
    ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query_type: str = Form("summary"),
    user_query: Optional[str] = Form(None),
    start_page: int = Form(0),
    end_page: int = Form(-1),
) -> Dict[str, Any]:
    """
    Analyze a document using the document analysis service.
    Query type can be either 'summary' or 'qa'.
    """
    file_content = await file.read()
    
    result = document_service.analyze_document(
        file_content=file_content,
        query_type=query_type,
        user_query=user_query,
        start_page=start_page,
        end_page=end_page,
    )
    
    return result

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    """
    return {"status": "healthy"} 