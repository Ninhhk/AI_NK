from fastapi import APIRouter, File, UploadFile, Form
from typing import Dict, Any

from .document_service import DocumentAnalysisService
from .config import OLLAMA_CONFIG

router = APIRouter()
document_service = DocumentAnalysisService(
    model_name=OLLAMA_CONFIG["model_name"],
    base_url=OLLAMA_CONFIG["base_url"]
)

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query_type: str = Form(...),
    user_query: str = Form(None),
    start_page: int = Form(0),
    end_page: int = Form(-1),
) -> Dict[str, Any]:
    """
    Analyze a document based on the query type.
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

@router.get("/chat-history/{document_id}")
async def get_chat_history(document_id: str) -> Dict[str, Any]:
    """
    Retrieve chat history for a specific document.
    """
    chat_history = document_service.get_chat_history(document_id)
    return {"history": chat_history}

@router.post("/generate-quiz")
async def generate_quiz(
    file: UploadFile = File(...),
    num_questions: int = Form(5),
    difficulty: str = Form("medium"),
    start_page: int = Form(0),
    end_page: int = Form(-1),
) -> Dict[str, Any]:
    """
    Generate a quiz from a document.
    """
    file_content = await file.read()
    
    result = document_service.generate_quiz(
        file_content=file_content,
        num_questions=num_questions,
        difficulty=difficulty,
        start_page=start_page,
        end_page=end_page,
    )
    
    return result 