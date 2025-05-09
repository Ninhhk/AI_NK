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

class SlideRepository:
    """Repository for slide presentation CRUD operations"""
    
    def insert_slide_presentation(
        self,
        user_id: str,
        title: str,
        slide_count: int,
        content: Optional[str] = None,
        json_path: Optional[str] = None,
        pptx_path: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a new slide presentation into the database
        
        Args:
            user_id: ID of the user who owns this presentation
            title: Title of the presentation
            slide_count: Number of slides
            content: JSON content string
            json_path: Path to the stored JSON file
            pptx_path: Path to the stored PPTX file
            meta: Additional metadata for the presentation
            
        Returns:
            Slide presentation record as a dictionary
        """
        slide_id = str(uuid.uuid4())
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO slides (
                    id, user_id, title, slide_count, content, json_path, 
                    pptx_path, meta, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slide_id, user_id, title, slide_count, content, 
                    json_path, pptx_path, serialize_meta(meta), now, now
                )
            )
            conn.commit()
            
            # Return the created presentation
            cursor.execute("SELECT * FROM slides WHERE id = ?", (slide_id,))
            presentation = cursor.fetchone()
            
            # Deserialize metadata
            if presentation and presentation.get("meta"):
                presentation["meta"] = deserialize_meta(presentation["meta"])
                
            return presentation
    
    def get_slide_by_id(self, slide_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a slide presentation by its ID
        
        Args:
            slide_id: The slide presentation ID to retrieve
            
        Returns:
            Slide presentation record or None if not found
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM slides WHERE id = ?", (slide_id,))
            presentation = cursor.fetchone()
            
            # Deserialize metadata
            if presentation and presentation.get("meta"):
                presentation["meta"] = deserialize_meta(presentation["meta"])
                
            return presentation
    
    def get_slides_by_user(
        self, 
        user_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get slide presentations for a specific user
        
        Args:
            user_id: The user ID to get presentations for
            limit: Maximum number of presentations to return
            offset: Pagination offset
            
        Returns:
            List of slide presentation records
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM slides 
                WHERE user_id = ? 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
                """, 
                (user_id, limit, offset)
            )
            presentations = cursor.fetchall()
            
            # Deserialize metadata for each presentation
            for pres in presentations:
                if pres.get("meta"):
                    pres["meta"] = deserialize_meta(pres["meta"])
                    
            return presentations
    
    def update_slide_paths(
        self, 
        slide_id: str, 
        json_path: Optional[str] = None, 
        pptx_path: Optional[str] = None
    ) -> bool:
        """
        Update slide presentation file paths
        
        Args:
            slide_id: The slide presentation ID to update
            json_path: New path to the JSON file
            pptx_path: New path to the PPTX file
            
        Returns:
            True if successful, False otherwise
        """
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically based on provided arguments
            update_parts = []
            params = []
            
            if json_path is not None:
                update_parts.append("json_path = ?")
                params.append(json_path)
                
            if pptx_path is not None:
                update_parts.append("pptx_path = ?")
                params.append(pptx_path)
                
            if not update_parts:
                return False  # Nothing to update
                
            update_parts.append("updated_at = ?")
            params.append(now)
            
            params.append(slide_id)  # For WHERE clause
            
            query = f"UPDATE slides SET {', '.join(update_parts)} WHERE id = ?"
            
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_slide(self, slide_id: str) -> bool:
        """
        Delete a slide presentation
        
        Args:
            slide_id: The slide presentation ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        # First get the presentation to get the file paths
        presentation = self.get_slide_by_id(slide_id)
        if not presentation:
            return False
            
        # Delete the files first
        for path_key in ["json_path", "pptx_path"]:
            file_path = presentation.get(path_key)
            if file_path:
                Storage.delete_file(file_path)
                
        # Now delete the database record
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM slides WHERE id = ?", (slide_id,))
            conn.commit()
            return cursor.rowcount > 0

class QuizRepository:
    """Repository for quiz CRUD operations"""
    
    def insert_quiz(
        self,
        document_id: str,
        questions_count: int,
        difficulty: str,
        content: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a new quiz into the database
        
        Args:
            document_id: ID of the document this quiz is based on
            questions_count: Number of questions in the quiz
            difficulty: Difficulty level of the quiz
            content: JSON content string with quiz data
            meta: Additional metadata for the quiz
            
        Returns:
            Quiz record as a dictionary
        """
        quiz_id = str(uuid.uuid4())
        now = int(time.time())
        
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO quizzes (
                    id, document_id, questions_count, difficulty, content, 
                    meta, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    quiz_id, document_id, questions_count, difficulty, 
                    content, serialize_meta(meta), now, now
                )
            )
            conn.commit()
            
            # Return the created quiz
            cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            quiz = cursor.fetchone()
            
            # Deserialize metadata
            if quiz and quiz.get("meta"):
                quiz["meta"] = deserialize_meta(quiz["meta"])
                
            return quiz
    
    def get_quiz_by_id(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a quiz by its ID
        
        Args:
            quiz_id: The quiz ID to retrieve
            
        Returns:
            Quiz record or None if not found
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            quiz = cursor.fetchone()
            
            # Deserialize metadata
            if quiz and quiz.get("meta"):
                quiz["meta"] = deserialize_meta(quiz["meta"])
                
            return quiz
    
    def get_quizzes_by_document(
        self, 
        document_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get quizzes for a specific document
        
        Args:
            document_id: The document ID to get quizzes for
            limit: Maximum number of quizzes to return
            offset: Pagination offset
            
        Returns:
            List of quiz records
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM quizzes 
                WHERE document_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
                """, 
                (document_id, limit, offset)
            )
            quizzes = cursor.fetchall()
            
            # Deserialize metadata for each quiz
            for quiz in quizzes:
                if quiz.get("meta"):
                    quiz["meta"] = deserialize_meta(quiz["meta"])
                    
            return quizzes
    
    def delete_quiz(self, quiz_id: str) -> bool:
        """
        Delete a quiz
        
        Args:
            quiz_id: The quiz ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
            conn.commit()
            return cursor.rowcount > 0