import sqlite3
import json
import os

# Check if database file exists
db_path = 'storage/database.sqlite'
print(f"Database file exists: {os.path.exists(db_path)}")
print(f"Working directory: {os.getcwd()}")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cursor = conn.cursor()    # First check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
    table_exists = cursor.fetchone()
    print(f"Chat history table exists: {table_exists is not None}")

    if table_exists:
        # Query chat history from chat_history table
        cursor.execute('SELECT id, document_id, user_query, system_response, created_at FROM chat_history ORDER BY created_at DESC LIMIT 10')
        rows = cursor.fetchall()

        print('Chat history count:', len(rows))
        print('\n--- RECENT CHAT HISTORY ---')
        for i, row in enumerate(rows, 1):
            print(f"\n=== Conversation {i} ===")
            print(f"ID: {row['id']}")
            print(f"Document ID: {row['document_id']}")
            print(f"Created: {row['created_at']}")
            print(f"User Query: {row['user_query']}")
            print(f"AI Response: {row['system_response'][:200]}..." if len(row['system_response']) > 200 else f"AI Response: {row['system_response']}")
            print("-" * 50)
    
    # Close connection
    conn.close()
except Exception as e:
    print(f"Error: {e}")
