import sqlite3
import json
import os
import sys

# Use direct path for debugging
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

# The document ID with missing chat history
document_id = "5192dfa061eb9db2a0889a83e7cdcc8f"

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    # First check if document exists
    cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
    document = cursor.fetchone()
    print(f"Document found: {document is not None}")
    
    if document:
        print(f"Document details: {json.dumps({k: str(v) for k, v in document.items()}, indent=2)}")

    # Check if chat_history table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
    table_exists = cursor.fetchone()
    print(f"Chat history table exists: {table_exists is not None}")

    # Check for foreign key constraints
    cursor.execute("PRAGMA foreign_keys")
    fk_status = cursor.fetchone()
    print(f"Foreign key status: {fk_status}")

    # Check the schema of the chat_history table
    cursor.execute("PRAGMA table_info(chat_history)")
    schema = cursor.fetchall()
    print("Chat history table schema:")
    for col in schema:
        print(f"  {col}")

    # Query all chat history entries
    cursor.execute("SELECT * FROM chat_history LIMIT 10")
    all_entries = cursor.fetchall()
    print(f"Total chat history entries in database: {len(all_entries)}")
    
    # Query for this specific document
    cursor.execute("SELECT COUNT(*) as count FROM chat_history WHERE document_id = ?", (document_id,))
    document_count = cursor.fetchone()
    print(f"Chat entries for document {document_id}: {document_count['count'] if document_count else 0}")

    # Create a test chat entry if none exists
    if document and document_count and document_count['count'] == 0:
        print("Creating a test chat entry...")
        now = int(__import__('time').time())
        chat_id = str(__import__('uuid').uuid4())
        
        cursor.execute(
            """
            INSERT INTO chat_history (
                id, document_id, user_query, system_response, meta, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id, document_id, "Test question for debugging", 
                "Test response for debugging", 
                json.dumps({"debug": True}), now, now
            )
        )
        conn.commit()
        print(f"Test chat entry created with ID: {chat_id}")
        
        # Verify it was added
        cursor.execute("SELECT * FROM chat_history WHERE id = ?", (chat_id,))
        new_entry = cursor.fetchone()
        if new_entry:
            print(f"New entry verified: {json.dumps({k: str(v) for k, v in new_entry.items()}, indent=2)}")
    
    # Close connection
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
