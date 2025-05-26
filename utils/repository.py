import uuid
import time
import os
import logging
from typing import Optional, Dict, Any, List

from .database import DatabaseConnection, serialize_meta, deserialize_meta, Storage

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentRepository:
    """Repository for document CRUD operations"""
    
    def insert_document(
        self, 
        user_id: str, 
        filename: str, 
        path: str, 
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a new document into the database
        
        Args:
            user_id: ID of the user who owns this document
            filename: Original filename
            path: Path to the stored file
            content_type: MIME type of the file
            size: Size of the file in bytes
            meta: Additional metadata for the document
            
        Returns:
            Document record as a dictionary
        """
        doc_id = str(uuid.uuid4())
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents (
                    id, user_id, filename, path, content_type, size, meta, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id, user_id, filename, path, content_type, size, 
                    serialize_meta(meta), now, now
                )
            )
            conn.commit()
            
            # Return the created document
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            document = cursor.fetchone()
            
            # Deserialize metadata
            if document and document.get("meta"):
                document["meta"] = deserialize_meta(document["meta"])
                
            return document
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID
        
        Args:
            document_id: The document ID to retrieve
            
        Returns:
            Document record or None if not found
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
            document = cursor.fetchone()
            
            # Deserialize metadata
            if document and document.get("meta"):
                document["meta"] = deserialize_meta(document["meta"])
                
            return document
    
    def get_documents_by_user(
        self, 
        user_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get documents for a specific user
        
        Args:
            user_id: The user ID to get documents for
            limit: Maximum number of documents to return
            offset: Pagination offset
            
        Returns:
            List of document records
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM documents 
                WHERE user_id = ? 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
                """, 
                (user_id, limit, offset)
            )
            documents = cursor.fetchall()
            
            # Deserialize metadata for each document
            for doc in documents:
                if doc.get("meta"):
                    doc["meta"] = deserialize_meta(doc["meta"])
                    
            return documents
    
    def update_document_content(self, document_id: str, content: str) -> bool:
        """
        Update document text content
        
        Args:
            document_id: The document ID to update
            content: Text content of the document
            
        Returns:
            True if successful, False otherwise
        """
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE documents 
                SET content = ?, updated_at = ? 
                WHERE id = ?
                """,
                (content, now, document_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def update_document_meta(self, document_id: str, meta: Dict[str, Any]) -> bool:
        """
        Update document metadata
        
        Args:
            document_id: The document ID to update
            meta: New metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        now = int(time.time())
        
        # First get existing metadata to merge
        current_doc = self.get_document_by_id(document_id)
        if not current_doc:
            return False
            
        # Merge existing metadata with new metadata
        current_meta = current_doc.get("meta", {})
        updated_meta = {**current_meta, **meta}
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE documents 
                SET meta = ?, updated_at = ? 
                WHERE id = ?
                """,
                (serialize_meta(updated_meta), now, document_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document
        
        Args:
            document_id: The document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        # First get the document to get the file path
        document = self.get_document_by_id(document_id)
        if not document:
            return False
            
        # Delete the file first
        file_path = document.get("path")
        if file_path:
            Storage.delete_file(file_path)
            
        # Now delete the database record
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_old_documents(self, cutoff_date) -> List[Dict[str, Any]]:
        """
        Get documents older than the specified cutoff date
        
        Args:
            cutoff_date: Datetime object representing the cutoff date
            
        Returns:
            List of document records older than the cutoff date
        """
        # Convert datetime to Unix timestamp
        cutoff_timestamp = int(cutoff_date.timestamp())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM documents 
                WHERE created_at < ? 
                """, 
                (cutoff_timestamp,)
            )
            documents = cursor.fetchall()
            
            # Deserialize metadata for each document
            for doc in documents:
                if doc.get("meta"):
                    doc["meta"] = deserialize_meta(doc["meta"])
                    
            return documents
            
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents in the database
        
        Returns:
            List of all document records
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents")
            documents = cursor.fetchall()
            
            # Deserialize metadata for each document
            for doc in documents:
                if doc.get("meta"):
                    doc["meta"] = deserialize_meta(doc["meta"])
                    
            return documents
    
    def get_document_by_content_id(self, content_based_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if a document with the given content-based ID already exists for this user
        
        Args:
            content_based_id: The content-based document ID to search for
            user_id: The user ID to scope the search to
            
        Returns:
            Document record if found, None otherwise
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM documents 
                WHERE id = ? AND user_id = ?
                """,
                (content_based_id, user_id)
            )
            document = cursor.fetchone()
            
            # Deserialize metadata
            if document and document.get("meta"):
                document["meta"] = deserialize_meta(document["meta"])
                
            return document
    
    def insert_or_get_document(
        self, 
        document_id: str,
        user_id: str, 
        filename: str, 
        path: str, 
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a new document or return existing one if it already exists with the same content-based ID
        
        Args:
            document_id: Content-based document ID
            user_id: ID of the user who owns this document
            filename: Original filename
            path: Path to the stored file
            content_type: MIME type of the file
            size: Size of the file in bytes
            meta: Additional metadata for the document
            
        Returns:
            Document record as a dictionary (existing or newly created)
        """
        # First check if document already exists
        existing_doc = self.get_document_by_content_id(document_id, user_id)
        if existing_doc:
            logger.info(f"Found existing document with content-based ID: {document_id}")
            return existing_doc
        
        # Document doesn't exist, create new one
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents (
                    id, user_id, filename, path, content_type, size, meta, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id, user_id, filename, path, content_type, size,
                    serialize_meta(meta) if meta else None, now, now
                )
            )
            conn.commit()
            
            logger.info(f"Created new document with content-based ID: {document_id}")
            
            return {
                "id": document_id,
                "user_id": user_id,
                "filename": filename,
                "path": path,
                "content_type": content_type,
                "size": size,
                "meta": meta or {},
                "created_at": now,
                "updated_at": now
            }
    
class ChatHistoryRepository:
    """Repository for chat history CRUD operations"""
    
    def add_chat_entry(
        self,
        document_id: str,
        user_query: str,
        system_response: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new chat entry to the history
        
        Args:
            document_id: The document ID this chat is about
            user_query: The user's question
            system_response: The system's response
            meta: Additional metadata for the chat entry
            
        Returns:
            Created chat entry record
        """
        chat_id = str(uuid.uuid4())
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chat_history (
                    id, document_id, user_query, system_response, meta, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chat_id, document_id, user_query, system_response, 
                    serialize_meta(meta), now, now
                )
            )
            conn.commit()
            
            # Return the created chat entry
            cursor.execute("SELECT * FROM chat_history WHERE id = ?", (chat_id,))
            chat_entry = cursor.fetchone()
            
            # Deserialize metadata
            if chat_entry and chat_entry.get("meta"):
                chat_entry["meta"] = deserialize_meta(chat_entry["meta"])
                
            return chat_entry
    
    def get_chat_entry_by_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat entry by its ID
        
        Args:
            chat_id: The chat entry ID to retrieve
            
        Returns:
            Chat entry record or None if not found
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_history WHERE id = ?", (chat_id,))
            chat_entry = cursor.fetchone()
            
            # Deserialize metadata
            if chat_entry and chat_entry.get("meta"):
                chat_entry["meta"] = deserialize_meta(chat_entry["meta"])
                
            return chat_entry
    
    def get_chat_history_by_document(
        self, 
        document_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a specific document
        
        Args:
            document_id: The document ID to get history for
            limit: Maximum number of entries to return
            offset: Pagination offset
            
        Returns:
            List of chat entry records
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM chat_history 
                WHERE document_id = ? 
                ORDER BY created_at ASC 
                LIMIT ? OFFSET ?
                """, 
                (document_id, limit, offset)
            )
            chat_entries = cursor.fetchall()
            
            # Deserialize metadata for each entry
            for entry in chat_entries:
                if entry.get("meta"):
                    entry["meta"] = deserialize_meta(entry["meta"])
                    
            return chat_entries
    
    def delete_chat_entry(self, chat_id: str) -> bool:
        """
        Delete a chat entry
        
        Args:
            chat_id: The chat entry ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE id = ?", (chat_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_chat_history_by_document(self, document_id: str) -> bool:
        """
        Delete all chat history for a document
        
        Args:
            document_id: The document ID to delete history for
            
        Returns:
            True if successful, False otherwise
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE document_id = ?", (document_id,))
            conn.commit()
            return cursor.rowcount > 0