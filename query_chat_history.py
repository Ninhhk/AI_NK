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
    cursor = conn.cursor()

    # First check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
    table_exists = cursor.fetchone()
    print(f"Chat history table exists: {table_exists is not None}")

    if table_exists:
        # Query chat history
        cursor.execute('SELECT * FROM chat_history LIMIT 5')
        rows = cursor.fetchall()

        print('Chat history count:', len(rows))
        for row in rows:
            # Convert any serialized JSON
            if 'meta' in row and row['meta']:
                try:
                    row['meta'] = json.loads(row['meta'])
                except:
                    pass
            print(json.dumps(row, indent=2))
    
    # Close connection
    conn.close()
except Exception as e:
    print(f"Error: {e}")
