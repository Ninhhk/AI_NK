import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath("."))

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    from utils.repository import DocumentRepository, ChatHistoryRepository
    
    # Test document repository
    doc_repo = DocumentRepository()
    print("Successfully imported DocumentRepository")
    
    docs = doc_repo.get_all_documents()
    print(f"Found {len(docs)} documents")
    
    # Test chat history repository
    chat_repo = ChatHistoryRepository()
    print("Successfully imported ChatHistoryRepository")
    
    # Test the method that's failing
    if hasattr(chat_repo, 'get_chat_history_by_document'):
        print("ChatHistoryRepository has get_chat_history_by_document method")
    else:
        print("WARNING: ChatHistoryRepository does NOT have get_chat_history_by_document method")
    
    # If we have any documents, try to get chat history
    if docs:
        first_doc_id = docs[0]['id']
        chat_history = chat_repo.get_chat_history_by_document(first_doc_id)
        print(f"Found {len(chat_history)} chat entries for document {first_doc_id}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
