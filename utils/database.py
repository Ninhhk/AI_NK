import sqlite3
import os
import json
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Base paths for our storage
BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DB_PATH = STORAGE_DIR / "database.sqlite"
# Log the actual absolute path for debugging
print(f"Database path: {DB_PATH.absolute()}")
UPLOAD_DIR = STORAGE_DIR / "uploads"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def dict_factory(cursor, row):
    """Convert SQLite row to dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DatabaseConnection:
    """Context manager for database connections"""
    
    def __init__(self):
        self.conn = None
    def __enter__(self):
        # Create tables if they don't exist
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = dict_factory
        
        # Enable foreign keys and verify they're ON
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()
        if fk_status and fk_status['foreign_keys'] != 1:
            print(f"Warning: Foreign keys not enabled: {fk_status}")
        
        # Create schema if needed
        self._create_schema()
        return self.conn
    
    def _create_schema(self):
        """Create database schema if not exists"""
        cursor = self.conn.cursor()
        
        # Documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            content_type TEXT,
            size INTEGER,
            content TEXT,
            hash TEXT,
            meta TEXT,
            created_at INTEGER,
            updated_at INTEGER
        )
        """)
        
        # Chat messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            system_response TEXT,
            meta TEXT,
            created_at INTEGER,
            updated_at INTEGER,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """)
        
        # Slides history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS slides (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            slide_count INTEGER,
            content TEXT,
            json_path TEXT,
            pptx_path TEXT,
            meta TEXT,
            created_at INTEGER,
            updated_at INTEGER
        )
        """)
        
        # Quiz history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            questions_count INTEGER,
            difficulty TEXT,
            content TEXT,
            meta TEXT,
            created_at INTEGER,
            updated_at INTEGER,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """)
        
        # Commit schema changes
        self.conn.commit()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

class Storage:
    """File storage management"""
    
    @staticmethod
    def upload_file(file_content: bytes, filename: str) -> Tuple[str, str]:
        """
        Save uploaded file to storage directory
        
        Args:
            file_content: Raw bytes of the file
            filename: Original filename
            
        Returns:
            Tuple of (file_id, file_path)
        """
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Create safe filename with ID prefix
        safe_filename = f"{file_id}_{filename.replace(' ', '_')}"
        path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save file
        with open(path, "wb") as f:
            f.write(file_content)
            
        return file_id, path
    
    @staticmethod
    def get_file_path(path: str) -> str:
        """Get full path to a file in storage"""
        return path
    @staticmethod
    def read_file(path: str) -> bytes:
        """Read file contents from storage"""
        with open(path, "rb") as f:
            return f.read()
            
    @staticmethod
    def delete_file(path: str) -> bool:
        """Delete a file from storage"""
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception:
            return False
            
    @staticmethod
    def vacuum_database() -> bool:
        """
        Perform SQLite VACUUM operation to optimize database and reclaim disk space
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("VACUUM")
                return True
        except Exception as e:
            print(f"Error during database vacuum: {e}")
            return False

def serialize_meta(meta_dict: Dict) -> str:
    """Serialize metadata dictionary for storage"""
    if meta_dict is None:
        return "{}"
    return json.dumps(meta_dict)

def deserialize_meta(meta_str: str) -> Dict:
    """Deserialize metadata string from storage"""
    if not meta_str:
        return {}
    try:
        return json.loads(meta_str)
    except Exception:
        return {}