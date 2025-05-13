# PowerShell script to repair database
# Script: c:\Users\ADMIN\Test_Gen_slide\AI_NVCB\AI_NVCB\repair_database.ps1

Write-Host "Starting database repair..."

# Use sqlite3 command line to repair the database
$databasePath = "C:\Users\ADMIN\Test_Gen_slide\AI_NVCB\AI_NVCB\storage\database.sqlite"
$documentId = "5192dfa061eb9db2a0889a83e7cdcc8f"
$timestamp = [int](Get-Date -UFormat %s)
$chatId = [guid]::NewGuid().ToString()

# Create commands file
$sqlCommands = @"
-- Check if document exists
SELECT COUNT(*) FROM documents WHERE id = '$documentId';

-- Create document if it doesn't exist
INSERT OR IGNORE INTO documents (
    id, user_id, filename, path, content_type, size, content, meta, created_at, updated_at
) VALUES (
    '$documentId', 'default_user', 'test_document.txt', 'storage/uploads/test_document.txt',
    'text/plain', 0, 'This is a test document.', 
    '{"repaired":true,"description":"Test document created during repair"}',
    $timestamp, $timestamp
);

-- Add a test chat entry
INSERT INTO chat_history (
    id, document_id, user_query, system_response, meta, created_at, updated_at
) VALUES (
    '$chatId', '$documentId', 
    'What is in this document?', 
    'This is a test document created for debugging purposes.', 
    '{"repair":true}', $timestamp, $timestamp
);

-- Verify it worked
SELECT COUNT(*) FROM documents WHERE id = '$documentId';
SELECT COUNT(*) FROM chat_history WHERE document_id = '$documentId';

-- Show the document
SELECT * FROM documents WHERE id = '$documentId';

-- Show chat history
SELECT * FROM chat_history WHERE document_id = '$documentId';
"@

# Save SQL commands to a temporary file
$tempFile = [System.IO.Path]::GetTempFileName()
$sqlCommands | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "Running SQL commands from $tempFile"
Write-Host "Database path: $databasePath"

# Execute the SQL commands
& sqlite3 $databasePath ".read $tempFile"

# Clean up
Remove-Item $tempFile

Write-Host "Database repair completed."
