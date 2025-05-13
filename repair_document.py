import sqlite3
import json
import os
import uuid
import time
from pathlib import Path

# The document ID with missing entry
target_document_id = "5192dfa061eb9db2a0889a83e7cdcc8f"

# Base paths for our storage
db_path = 'storage/database.sqlite'
print(f"Database file exists: {os.path.exists(db_path)}")
print(f"Working directory: {os.getcwd()}")
print(f"Database absolute path: {os.path.abspath(db_path)}")

# Function to convert rows to dictionaries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    # First check if document exists
    cursor.execute("SELECT * FROM documents WHERE id = ?", (target_document_id,))
    document = cursor.fetchone()
    print(f"Document found: {document is not None}")
    
    if not document:
        print(f"Creating a new document with ID: {target_document_id}")
        
        # Create document entry
        now = int(time.time())
        file_path = "storage/uploads/test_document.txt"
        
        # Create a minimal document record
        cursor.execute(
            """
            INSERT INTO documents (
                id, user_id, filename, path, content_type, size, content, meta, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                target_document_id, "default_user", "test_document.txt", file_path,
                "text/plain", 0, "This is a test document.", 
                json.dumps({"repaired": True, "description": "Test document created during repair"}),
                now, now
            )
        )
        conn.commit()
        
        # Create a test chat entry for the document
        chat_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO chat_history (
                id, document_id, user_query, system_response, meta, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id, target_document_id, 
                "What's in this test document?", 
                "This is a test document created for debugging purposes.", 
                json.dumps({"repair": True}), now, now
            )
        )
        conn.commit()
        
        print(f"Created test document with ID: {target_document_id}")
        print(f"Created test chat entry with ID: {chat_id}")
        
        # Verify both were created
        cursor.execute("SELECT * FROM documents WHERE id = ?", (target_document_id,))
        document = cursor.fetchone()
        print(f"Document entry verified: {document is not None}")
        
        cursor.execute("SELECT * FROM chat_history WHERE document_id = ?", (target_document_id,))
        chat_entries = cursor.fetchall()
        print(f"Chat entries for document: {len(chat_entries)}")
    else:
        print(f"Document already exists: {document}")
        
        # Check for chat entries
        cursor.execute("SELECT * FROM chat_history WHERE document_id = ?", (target_document_id,))
        chat_entries = cursor.fetchall()
        print(f"Found {len(chat_entries)} chat entries for this document")
        
        # If no chat entries, create one
        if len(chat_entries) == 0:
            now = int(time.time())
            chat_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO chat_history (
                    id, document_id, user_query, system_response, meta, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chat_id, target_document_id, 
                    "What's in this test document?", 
                    "This is a test document created for debugging purposes.", 
                    json.dumps({"repair": True}), now, now
                )
            )
            conn.commit()
            print(f"Created test chat entry with ID: {chat_id}")
    
    # Close connection
    conn.close()
    
    print("Database repair completed successfully.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
