import sqlite3
import os

# Check both database files
db1 = 'storage/database.sqlite'
db2 = 'documents.db'

print(f'storage/database.sqlite exists: {os.path.exists(db1)}')
print(f'documents.db exists: {os.path.exists(db2)}')

if os.path.exists(db1):
    print(f'storage/database.sqlite size: {os.path.getsize(db1)} bytes')
if os.path.exists(db2):
    print(f'documents.db size: {os.path.getsize(db2)} bytes')

# Check tables in storage/database.sqlite
if os.path.exists(db1):
    conn1 = sqlite3.connect(db1)
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables1 = cursor1.fetchall()
    print(f'Tables in storage/database.sqlite: {[t[0] for t in tables1]}')
    
    # Check chat_history table
    if 'chat_history' in [t[0] for t in tables1]:
        cursor1.execute('SELECT COUNT(*) FROM chat_history')
        count = cursor1.fetchone()[0]
        print(f'Chat history entries in storage/database.sqlite: {count}')
        
        # Check a sample record
        cursor1.execute('SELECT * FROM chat_history LIMIT 1')
        sample = cursor1.fetchone()
        print(f'Sample chat_history record: {sample}')
    conn1.close()
