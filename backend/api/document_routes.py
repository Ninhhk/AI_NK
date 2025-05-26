from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging
import traceback
import uuid
import hashlib

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.document_analysis.document_service import DocumentAnalysisService
from backend.document_analysis.config import OLLAMA_CONFIG
from utils.repository import DocumentRepository, ChatHistoryRepository
from utils.database import Storage
from backend.model_management.system_prompt_manager import system_prompt_manager

router = APIRouter()

# Initialize the document service
document_service = DocumentAnalysisService(
    model_name=OLLAMA_CONFIG["model_name"],
    base_url=OLLAMA_CONFIG["base_url"],
    temperature=OLLAMA_CONFIG["temperature"]
)

# Initialize repositories
document_repo = DocumentRepository()
chat_history_repo = ChatHistoryRepository()

# Simple user dependency for now - in production you'd have proper auth
def get_current_user():
    return {"id": "default_user"}

def generate_content_based_document_id(file_content: bytes, filename: str) -> str:
    """
    Generate a consistent UUID-format document ID based on file content and name.
    This ensures the same file gets the same ID across different sessions.
    """
    # Create a hash from file content and filename for uniqueness
    content_hash = hashlib.md5(file_content + filename.encode()).hexdigest()
    
    # Convert the hash into a UUID namespace format for consistency
    # Use the first 32 characters of the hash to create a deterministic UUID
    uuid_str = f"{content_hash[:8]}-{content_hash[8:12]}-{content_hash[12:16]}-{content_hash[16:20]}-{content_hash[20:32]}"
    return uuid_str

def generate_multi_document_id(file_contents: List[bytes], filenames: List[str]) -> str:
    """
    Generate a consistent UUID-format ID for multi-document analysis.
    This ensures the same set of documents gets the same multi-document ID.
    """
    # Create a combined hash from all file contents and names
    combined_content = b"".join(file_contents)
    combined_names = "|".join(sorted(filenames))  # Sort to ensure consistent order
    
    combined_hash = hashlib.md5(combined_content + combined_names.encode()).hexdigest()
    
    # Convert to UUID format
    uuid_str = f"{combined_hash[:8]}-{combined_hash[8:12]}-{combined_hash[12:16]}-{combined_hash[16:20]}-{combined_hash[20:32]}"
    return uuid_str

@router.post("/analyze")
async def analyze_document(
    query_type: str = Form(...),
    user_query: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = None,
    extra_files_1: Optional[UploadFile] = File(None),
    extra_files_2: Optional[UploadFile] = File(None),
    extra_files_3: Optional[UploadFile] = File(None),
    extra_files_4: Optional[UploadFile] = File(None),
    extra_files_5: Optional[UploadFile] = File(None),
    model_name: Optional[str] = Form(None),
    system_prompt: Optional[str] = Form(None),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze one or multiple documents using the document analysis service.
    Query type can be either 'summary' or 'qa'.
    
    Parameters:
    - query_type: Type of analysis ('summary' or 'qa')
    - user_query: User question (required for QA mode)
    - start_page: The page to start from (0-based)
    - end_page: The page to end at (-1 for all pages)
    - file: Main file to analyze
    - files: List of files to analyze
    - extra_files_1-5: Additional files to analyze
    - model_name: Optional Ollama model name to use for analysis
    - system_prompt: Optional custom system prompt to control AI behavior
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
      # Set model if provided
    if model_name:
        document_service.set_model(model_name)
        logger.info(f"Using model {model_name} for document analysis")
    
    logger.info(f"Processing {len(all_files)} files for analysis")
    file_contents = []
    filenames = []  # Store filenames for better output formatting
    document_ids = []  # Store document IDs for database reference
    
    for f in all_files:
        try:
            # Reset the file position to the beginning before reading
            await f.seek(0)
            file_content = await f.read()
            
            # Generate content-based document ID
            content_based_id = generate_content_based_document_id(file_content, f.filename)
            
            # Save file to storage system
            file_id, file_path = Storage.upload_file(file_content, f.filename)
            
            # Insert or get existing document record in database
            document = document_repo.insert_or_get_document(
                document_id=content_based_id,
                user_id=current_user["id"],
                filename=f.filename,
                path=file_path,
                content_type=f.content_type,
                size=len(file_content),
                meta={
                    "original_filename": f.filename,
                    "content_type": f.content_type,
                    "content_based_id": True,  # Flag to indicate this uses content-based ID
                }
            )
            
            # Add to processing lists
            file_contents.append(file_content)
            filenames.append(f.filename)
            document_ids.append(document["id"])
            
            logger.debug(f"Successfully processed file: {f.filename} ({len(file_content)} bytes), ID: {document['id']}")
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
                system_prompt=system_prompt,            )
            # Store in chat history if it's a QA query
            if query_type == "qa" and user_query:
                chat_entry = chat_history_repo.add_chat_entry(
                    document_id=document_ids[0],
                    user_query=user_query,
                    system_response=result.get("result", ""),
                    meta={
                        "query_type": query_type
                    }
                )
                # Add chat history ID to result
                result["chat_id"] = chat_entry["id"]
                logger.debug(f"Added chat history entry: document_id={document_ids[0]}, user_query='{user_query[:50]}...'")
                logger.debug(f"Chat entry added with ID: {chat_entry['id']}")
            
            # Override the document_id in result with the database document ID
            result["document_id"] = document_ids[0]
            logger.debug(f"Set result document_id to database ID: {document_ids[0]}")
        else:
            # For multiple files, use the multi-document analysis method
            logger.info(f"Using multi-file analysis method for {len(file_contents)} files")
            result = document_service.analyze_multiple_documents(
                file_contents=file_contents,
                filenames=filenames,
                query_type=query_type,
                user_query=user_query,
                system_prompt=system_prompt,
            )
              # Store in chat history with references to all documents
            if query_type == "qa" and user_query:
                # Generate content-based multi-document ID
                multi_doc_id = generate_multi_document_id(file_contents, filenames)
                
                # Create a placeholder document record for multi-document analysis
                combined_filenames = ', '.join(filenames)
                placeholder_document = document_repo.insert_or_get_document(
                    document_id=multi_doc_id,
                    user_id=current_user["id"],
                    filename=f"Combined: {combined_filenames[:100]}{'...' if len(combined_filenames) > 100 else ''}",
                    path="",  # No physical path for this virtual document
                    content_type="multi/document",
                    size=0,  # No physical size
                    meta={
                        "is_multi_document": True,
                        "document_ids": document_ids,
                        "document_names": filenames,
                        "content_based_id": True,  # Flag to indicate this uses content-based ID
                    }
                )
                  # Use the actual document ID from the placeholder record
                chat_entry = chat_history_repo.add_chat_entry(
                    document_id=placeholder_document["id"],
                    user_query=user_query,
                    system_response=result.get("result", ""),
                    meta={
                        "query_type": query_type,
                        "document_ids": document_ids,
                        "document_names": filenames
                    }
                )                # Add chat history ID to result
                result["chat_id"] = chat_entry["id"]
                # Add placeholder document ID to result
                result["multi_document_id"] = placeholder_document["id"]
            else:
                # For non-QA operations, create a proper placeholder document as well
                multi_doc_id = generate_multi_document_id(file_contents, filenames)
                
                combined_filenames = ', '.join(filenames)
                placeholder_document = document_repo.insert_or_get_document(
                    document_id=multi_doc_id,
                    user_id=current_user["id"],
                    filename=f"Summary: {combined_filenames[:100]}{'...' if len(combined_filenames) > 100 else ''}",
                    path="",  # No physical path for this virtual document
                    content_type="multi/document",
                    size=0,  # No physical size
                    meta={
                        "is_multi_document": True,
                        "is_summary_only": True,
                        "document_ids": document_ids,
                        "document_names": filenames,
                        "content_based_id": True,  # Flag to indicate this uses content-based ID
                    }
                )
                # Use the actual document ID from the placeholder record
                result["multi_document_id"] = placeholder_document["id"]
                # Use the actual document ID from the placeholder record
                result["multi_document_id"] = placeholder_document["id"]
        
        # Add document IDs to result for frontend reference
        result["document_ids"] = document_ids
        
        # Add debug information to result for troubleshooting if needed
        if 'debug' not in result and len(file_contents) > 1:
            result['debug'] = {
                'file_count': len(file_contents),
                'filenames': filenames,
                'document_ids': document_ids
            }
        
        return result
    except Exception as e:
        logger.error(f"Error during document analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return {"result": f"Error analyzing documents: {str(e)}"}

@router.get("/chat-history/{document_id}")
async def get_chat_history(document_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Retrieve chat history for a specific document from database.
    """
    try:
        # Check if document exists first
        document = document_repo.get_document_by_id(document_id)
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return {
                "history": [],
                "document_id": document_id,
                "count": 0,
                "error": "Document not found"
            }
            
        # Check if it's a regular document ID or a multi-document ID
        if document_id.startswith("multi_"):
            # For multi-document chats, retrieve directly by the combined ID
            chat_history = chat_history_repo.get_chat_history_by_document(document_id, limit, offset)
        else:
            # For single documents, get history associated with this document
            chat_history = chat_history_repo.get_chat_history_by_document(document_id, limit, offset)
            
        # Check if this is a multi-document placeholder
        is_multi_document = document and document.get("meta", {}).get("is_multi_document", False)
        
        # Log the chat history for debugging
        logger.debug(f"Retrieved {len(chat_history)} chat entries for document_id: {document_id}")
        if chat_history:
            logger.debug(f"First chat entry: {chat_history[0]}")
        else:
            logger.debug("No chat entries found")
        
        # Convert 'created_at' to 'timestamp' for frontend compatibility
        for entry in chat_history:
            if 'created_at' in entry and 'timestamp' not in entry:
                entry['timestamp'] = entry['created_at']
        
        return {
            "history": chat_history,
            "document_id": document_id,
            "count": len(chat_history),
            "is_multi_document": is_multi_document
        }
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        logger.error(traceback.format_exc())
        # Return empty result instead of raising an exception
        return {
            "history": [],
            "document_id": document_id,
            "count": 0,
            "error": f"Error retrieving chat history: {str(e)}"
        }

@router.get("/documents")
async def get_documents(
    limit: int = 100, 
    offset: int = 0,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve a list of documents for the current user.
    """
    try:
        documents = document_repo.get_documents_by_user(current_user["id"], limit, offset)
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve a specific document by ID.
    """
    try:
        document = document_repo.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Check if user has access to this document
        if document["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
            
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a document and its associated chat history.
    """
    try:
        document = document_repo.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Check if user has access to this document
        if document["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this document")
        
        # Delete associated chat history
        chat_history_repo.delete_chat_history_by_document(document_id)
        
        # Delete the document
        success = document_repo.delete_document(document_id)
        
        return {"success": success, "message": "Document and associated chat history deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.post("/generate-quiz")
async def generate_quiz(
    file: UploadFile = File(...),
    num_questions: int = Form(5),
    difficulty: str = Form("medium"),
    model_name: Optional[str] = Form(None),
    system_prompt: Optional[str] = Form(None),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a quiz from a document using the document analysis service.
    
    Parameters:
    - file: The document to analyze
    - num_questions: Number of questions to generate
    - difficulty: The difficulty level ("easy", "medium", "hard")
    - start_page: The page to start from (0-based)
    - end_page: The page to end at (-1 for all pages)
    - model_name: Optional Ollama model name to use for generation
    - system_prompt: Optional custom system prompt to control AI behavior
    """
    try:
        file_content = await file.read()
        
        # Set model if provided
        if model_name:
            document_service.set_model(model_name)
        
        # Save file to storage system
        file_id, file_path = Storage.upload_file(file_content, file.filename)
        
        # Insert document record in database
        document = document_repo.insert_document(
            user_id=current_user["id"],
            filename=file.filename,
            path=file_path,
            content_type=file.content_type,
            size=len(file_content),
            meta={
                "original_filename": file.filename,
                "content_type": file.content_type,                "purpose": "quiz_generation"
            }
        )
        
        result = document_service.generate_quiz(
            file_content=file_content,
            num_questions=num_questions,
            difficulty=difficulty,
            system_prompt=system_prompt,
        )
        
        # Add document ID to result for frontend reference
        result["document_id"] = document["id"]
        
        # Update document metadata with quiz results
        document_repo.update_document_meta(document["id"], {
            "quiz": {
                "num_questions": num_questions,
                "difficulty": difficulty
            }
        })
        
        return result
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        logger.error(traceback.format_exc())
        return {"result": f"Error generating quiz: {str(e)}"}

@router.post("/generate-quiz-multiple")
async def generate_quiz_multiple(
    num_questions: int = Form(5),
    difficulty: str = Form("medium"),
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = None,
    extra_files_1: Optional[UploadFile] = File(None),
    extra_files_2: Optional[UploadFile] = File(None),
    extra_files_3: Optional[UploadFile] = File(None),
    extra_files_4: Optional[UploadFile] = File(None),
    extra_files_5: Optional[UploadFile] = File(None),
    model_name: Optional[str] = Form(None),
    system_prompt: Optional[str] = Form(None),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a quiz from multiple documents using the document analysis service.
    
    Parameters:
    - num_questions: Number of questions to generate
    - difficulty: The difficulty level ("easy", "medium", "hard")
    - file: Main file to analyze
    - files: List of files to analyze
    - extra_files_1-5: Additional files to analyze
    - model_name: Optional Ollama model name to use for generation
    - system_prompt: Optional custom system prompt to control AI behavior
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
    logger.debug(f"Total files collected for quiz generation: {len(all_files)}")
    for i, f in enumerate(all_files):
        logger.debug(f"Quiz file {i+1}: {f.filename}")
    
    if len(all_files) < 2:
        logger.warning("Not enough files provided for multi-document quiz generation")
        return {"result": "Vui lòng cung cấp ít nhất hai tài liệu để tạo bài trắc nghiệm từ nhiều tài liệu."}
    
    try:
        # Set model if provided
        if model_name:
            document_service.set_model(model_name)
            logger.info(f"Using model {model_name} for quiz generation")
        
        # Process files
        file_contents = []
        filenames = []
        document_ids = []
        
        for f in all_files:
            try:
                # Reset the file position to the beginning before reading
                await f.seek(0)
                file_content = await f.read()
                
                # Generate content-based document ID
                content_based_id = generate_content_based_document_id(file_content, f.filename)
                
                # Save file to storage system
                file_id, file_path = Storage.upload_file(file_content, f.filename)
                
                # Insert or get existing document record in database
                document = document_repo.insert_or_get_document(
                    document_id=content_based_id,
                    user_id=current_user["id"],
                    filename=f.filename,
                    path=file_path,
                    content_type=f.content_type,
                    size=len(file_content),
                    meta={
                        "original_filename": f.filename,
                        "content_type": f.content_type,
                        "content_based_id": True,
                        "purpose": "quiz_generation"
                    }
                )
                
                # Add to processing lists
                file_contents.append(file_content)
                filenames.append(f.filename)
                document_ids.append(document["id"])
                
                logger.debug(f"Successfully processed file for quiz: {f.filename} ({len(file_content)} bytes), ID: {document['id']}")
            except Exception as e:
                logger.error(f"Error processing file {f.filename}: {str(e)}")
                logger.error(traceback.format_exc())
                return {"result": f"Error processing file {f.filename}: {str(e)}"}
        
        # Generate multi-document quiz
        logger.info(f"Generating quiz from {len(file_contents)} documents")
        result = document_service.generate_quiz_multiple(
            file_contents=file_contents,
            filenames=filenames,
            num_questions=num_questions,
            difficulty=difficulty,
            system_prompt=system_prompt,
        )
        
        # Create a placeholder document record for the multi-document quiz
        multi_doc_id = generate_multi_document_id(file_contents, filenames)
        combined_filenames = ', '.join(filenames)
        placeholder_document = document_repo.insert_or_get_document(
            document_id=multi_doc_id,
            user_id=current_user["id"],
            filename=f"Quiz: {combined_filenames[:100]}{'...' if len(combined_filenames) > 100 else ''}",
            path="",  # No physical path for this virtual document
            content_type="multi/document",
            size=0,  # No physical size
            meta={
                "is_multi_document": True,
                "document_ids": document_ids,
                "document_names": filenames,
                "content_based_id": True,
                "purpose": "quiz_generation",
                "quiz": {
                    "num_questions": num_questions,
                    "difficulty": difficulty
                }
            }
        )
        
        # Add document IDs to result for frontend reference
        result["document_ids"] = document_ids
        result["multi_document_id"] = placeholder_document["id"]
        
        return result
    except Exception as e:
        logger.error(f"Error generating multi-document quiz: {str(e)}")
        logger.error(traceback.format_exc())
        return {"result": f"Error generating multi-document quiz: {str(e)}"}

@router.get("/current-model")
async def get_current_model() -> Dict[str, str]:
    """
    Get the current model being used for document analysis.
    
    Returns:
    - A dictionary containing the current model name
    """
    return {"model_name": document_service.get_current_model()}

@router.post("/set-model")
async def set_model(model_name: str = Form(...)) -> Dict[str, str]:
    """
    Set the model to use for document analysis.
    
    Parameters:
    - model_name: The name of the Ollama model to use
    
    Returns:
    - A dictionary containing the updated model name
    """
    try:
        document_service.set_model(model_name)
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
    Get the current system prompt used for document analysis.
    
    Returns:
    - A dictionary containing the current system prompt
    """
    return {"system_prompt": system_prompt_manager.get_system_prompt()}

@router.post("/system-prompt")
async def set_system_prompt(system_prompt: str = Form(...)) -> Dict[str, str]:
    """
    Set the system prompt to use for document analysis.
    
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

@router.post("/chat-history/{document_id}/initialize")
async def initialize_chat_history(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Initialize chat history for a document.
    This endpoint can be called when starting a new conversation with a document.
    """
    try:
        # Check if document exists
        document = document_repo.get_document_by_id(document_id)
        if not document:
            logger.warning(f"Document not found during chat history initialization: {document_id}")
            return {
                "success": False,
                "document_id": document_id,
                "error": "Document not found"
            }
            
        # No need to actually do anything, we'll create history entries as needed
        # This endpoint mainly serves as a check that the document exists
        
        logger.info(f"Chat history initialized for document: {document_id}")
        return {
            "success": True,
            "document_id": document_id,
            "message": "Chat history initialized"
        }
    except Exception as e:
        logger.error(f"Error initializing chat history: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "document_id": document_id,
            "error": f"Error initializing chat history: {str(e)}"
        }

@router.post("/chat-history/{document_id}/add")
async def add_chat_history_entry(
    document_id: str,
    message: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Add a new entry to the chat history for a document.
    """
    try:
        # Check if document exists
        document = document_repo.get_document_by_id(document_id)
        if not document:
            logger.warning(f"Document not found when adding chat message: {document_id}")
            return {
                "success": False,
                "document_id": document_id,
                "error": "Document not found"
            }
        
        # Add the chat entry
        user_query = message.get("user_query", "")
        system_response = message.get("system_response", "")
        
        # Validate required fields
        if not user_query or not system_response:
            return {
                "success": False,
                "document_id": document_id,
                "error": "Both user_query and system_response are required"
            }
        
        # Add metadata from the message if present
        meta = message.get("meta", {})
        
        # Add to history
        chat_entry = chat_history_repo.add_chat_entry(
            document_id=document_id,
            user_query=user_query,
            system_response=system_response,
            meta=meta
        )
        
        logger.info(f"Added chat entry for document: {document_id}")
        return {
            "success": True,
            "document_id": document_id,
            "chat_entry": chat_entry
        }
    except Exception as e:
        logger.error(f"Error adding chat entry: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "document_id": document_id,
            "error": f"Error adding chat entry: {str(e)}"
        }