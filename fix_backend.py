import os
import shutil

# Path to the original file and the fixed file
original_file = 'backend/document_analysis/document_service.py'
fixed_file = 'backend/document_analysis/document_service_fixed.py'

# Backup the original file
backup_file = 'backend/document_analysis/document_service.py.bak'
if os.path.exists(original_file):
    print(f"Backing up {original_file} to {backup_file}")
    shutil.copy2(original_file, backup_file)

# Replace the original file with the fixed file
if os.path.exists(fixed_file):
    print(f"Replacing {original_file} with {fixed_file}")
    shutil.copy2(fixed_file, original_file)
    print("Replacement complete")
else:
    print(f"Error: Fixed file {fixed_file} not found")
