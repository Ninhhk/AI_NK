print("Starting test...")

try:
    import sqlite3
    print("Imported sqlite3")
    
    # Test basic database connection
    conn = sqlite3.connect("storage/database.sqlite")
    print("Connected to database")
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT COUNT(*) as count FROM documents")
    result = cursor.fetchone()
    print(f"Documents count: {result['count']}")
    
    # Test querying chat history
    cursor.execute("SELECT COUNT(*) as count FROM chat_history")
    result = cursor.fetchone()
    print(f"Chat history count: {result['count']}")
    
    # Check if chat history has any entries
    if result['count'] > 0:
        cursor.execute("SELECT * FROM chat_history LIMIT 1")
        chat_entry = cursor.fetchone()
        print(f"First chat entry fields: {', '.join(chat_entry.keys())}")
    
    # Close connection
    conn.close()
    print("Test completed")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
