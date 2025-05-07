from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any, List
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.document_analysis.document_service import DocumentAnalysisService
from backend.document_analysis.config import OLLAMA_CONFIG

router = APIRouter()

# Initialize the document service
document_service = DocumentAnalysisService(
    model_name=OLLAMA_CONFIG["model_name"],
    base_url=OLLAMA_CONFIG["base_url"],
    temperature=OLLAMA_CONFIG["temperature"]
)

@router.post("/analyze")
async def analyze_document(
    query_type: str = Form(...),
    user_query: Optional[str] = Form(None),
    start_page: int = Form(0),
    end_page: int = Form(-1),
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = None,
    extra_files_1: Optional[UploadFile] = File(None),
    extra_files_2: Optional[UploadFile] = File(None),
    extra_files_3: Optional[UploadFile] = File(None),
    extra_files_4: Optional[UploadFile] = File(None),
    extra_files_5: Optional[UploadFile] = File(None),
) -> Dict[str, Any]:
    """
    Analyze one or multiple documents using the document analysis service.
    Query type can be either 'summary' or 'qa'.
    """
    # Gather all files from different parameters
    all_files = []
    
    # Add main file if provided
    if file:
        all_files.append(file)
        logger.debug(f"Added file from 'file' parameter: {file.filename}")
    
    # Add files from the 'files' list if provided
    if files:
        for f in files:
            all_files.append(f)
            logger.debug(f"Added file from 'files' parameter: {f.filename}")
    
    # Add extra files if provided (for multi-file upload support)
    extra_files = [extra_files_1, extra_files_2, extra_files_3, extra_files_4, extra_files_5]
    for i, extra_file in enumerate(extra_files):
        if extra_file:
            all_files.append(extra_file)
            logger.debug(f"Added file from 'extra_files_{i+1}' parameter: {extra_file.filename}")
    
    # Debug information
    logger.debug(f"Total files collected: {len(all_files)}")
    for i, f in enumerate(all_files):
        logger.debug(f"File {i+1}: {f.filename}")
    
    if not all_files:
        logger.warning("No files provided for document analysis")
        return {"result": "No files provided. Please upload at least one document for analysis."}
    
    logger.info(f"Processing {len(all_files)} files for analysis")
    file_contents = []
    filenames = []  # Store filenames for better output formatting
    
    for f in all_files:
        try:
            # Reset the file position to the beginning before reading
            await f.seek(0)
            file_content = await f.read()
            file_contents.append(file_content)
            filenames.append(f.filename)
            logger.debug(f"Successfully read file: {f.filename} ({len(file_content)} bytes)")
        except Exception as e:
            logger.error(f"Error processing file {f.filename}: {str(e)}")
            logger.error(traceback.format_exc())
            return {"result": f"Error processing file {f.filename}: {str(e)}"}
    
    try:
        if len(file_contents) == 1:
            # For single file, use the original method
            logger.info("Using single-file analysis method")
            result = document_service.analyze_document(
                file_content=file_contents[0],
                query_type=query_type,
                user_query=user_query,
                start_page=start_page,
                end_page=end_page,
            )
        else:
            # For multiple files, use the multi-document analysis method
            logger.info(f"Using multi-file analysis method for {len(file_contents)} files")
            result = document_service.analyze_multiple_documents(
                file_contents=file_contents,
                filenames=filenames,
                query_type=query_type,
                user_query=user_query,
                start_page=start_page,
                end_page=end_page,
            )
        
        # Add debug information to result for troubleshooting if needed
        if 'debug' not in result and len(file_contents) > 1:
            result['debug'] = {
                'file_count': len(file_contents),
                'filenames': filenames
            }
        
        return result
    except Exception as e:
        logger.error(f"Error during document analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return {"result": f"Error analyzing documents: {str(e)}"}

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
    Generate a quiz from a document using the document analysis service.
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

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    """
    return {"status": "healthy"}