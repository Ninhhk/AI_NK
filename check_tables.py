import sqlite3
import os

# Check if file exists and size
db_path = 'storage/database.sqlite'
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"Database file exists: {db_path}")
    print(f"File size: {size} bytes")
else:
    print(f"Database file not found: {db_path}")
    exit()

try:
    # Check tables in storage database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables in {db_path}:")
    if not tables:
        print("  No tables found")
    else:
        for table in tables:
            print(f"  - {table[0]}")

    # Check sample data from each table
    for table in tables:
        table_name = table[0]
        print(f"\n--- Sample data from {table_name} ---")
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {columns}")
            
            print(f"Row count: {len(rows)}")
            for i, row in enumerate(rows):
                print(f"  Row {i+1}: {row}")
        except Exception as e:
            print(f"  Error: {e}")

    conn.close()
    
except Exception as e:
    print(f"Database error: {e}")
