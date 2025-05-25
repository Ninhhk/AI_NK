import sqlite3
import json
import os
from datetime import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def format_timestamp(timestamp):
    """Convert Unix timestamp to readable format"""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

def main():
    print("Starting enhanced chat history script...")
    # Database configuration
    db_path = 'storage/database.sqlite'
    print(f"Database file exists: {os.path.exists(db_path)}")
    print(f"Working directory: {os.getcwd()}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        table_exists = cursor.fetchone()
        print(f"Chat history table exists: {table_exists is not None}")

        if not table_exists:
            print("No chat_history table found in database")
            return

        # Get total count
        cursor.execute('SELECT COUNT(*) as count FROM chat_history')
        total_count = cursor.fetchone()['count']
        print(f"Total chat history records: {total_count}")

        # Query recent chat history
        cursor.execute('''
            SELECT id, document_id, user_query, system_response, created_at, meta 
            FROM chat_history 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        rows = cursor.fetchall()

        print(f'\nShowing {len(rows)} most recent conversations:')
        print('\n' + '='*80)
        
        for i, row in enumerate(rows, 1):
            print(f"CONVERSATION #{i}")
            print(f"ID: {row['id']}")
            print(f"Document ID: {row['document_id']}")
            print(f"Created: {format_timestamp(row['created_at'])}")
            
            # Parse meta if it exists
            meta_info = ""
            if row.get('meta'):
                try:
                    meta = json.loads(row['meta'])
                    if 'query_type' in meta:
                        meta_info = f" ({meta['query_type']})"
                except:
                    pass
            
            print(f"\nUser Query{meta_info}:")
            print(f"  {row['user_query']}")
            
            print(f"\nAI Response:")
            response = row['system_response']
            # Show first 300 characters for readability
            if len(response) > 300:
                print(f"  {response[:300]}...")
                print(f"  [Response truncated - full length: {len(response)} characters]")
            else:
                print(f"  {response}")
            
            print('\n' + '-'*80)

        # Show some statistics
        print(f"\nSTATISTICS:")
        cursor.execute('SELECT COUNT(DISTINCT document_id) as unique_docs FROM chat_history')
        unique_docs = cursor.fetchone()['unique_docs']
        print(f"Unique documents queried: {unique_docs}")
        
        cursor.execute('SELECT AVG(LENGTH(user_query)) as avg_query_len FROM chat_history')
        avg_query_len = cursor.fetchone()['avg_query_len']
        print(f"Average query length: {avg_query_len:.1f} characters")
        
        cursor.execute('SELECT AVG(LENGTH(system_response)) as avg_response_len FROM chat_history')
        avg_response_len = cursor.fetchone()['avg_response_len']
        print(f"Average response length: {avg_response_len:.1f} characters")

        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
