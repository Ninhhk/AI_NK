#!/usr/bin/env python
"""
Script to automate project updates, dependency management, and testing.
This script will:
1. Pull the latest changes from git
2. Update poetry dependencies
3. Run basic dependency tests to verify everything works
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_command(command, description=None):
    """Run a shell command and print its output"""
    if description:
        print(f"\n{'=' * 50}")
        print(f"⏳ {description}")
        print(f"{'=' * 50}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        success = True
        output = result.stdout
    except subprocess.CalledProcessError as e:
        success = False
        output = f"ERROR: {e.stderr}\n{e.stdout}"
    
    duration = time.time() - start_time
    
    print(output)
    if success:
        print(f"✅ Completed in {duration:.2f}s\n")
    else:
        print(f"❌ Failed after {duration:.2f}s\n")
        if "--continue-on-error" not in sys.argv:
            sys.exit(1)
    
    return success, output


def check_dependencies():
    """Test basic dependencies to ensure they're working"""
    print(f"\n{'=' * 50}")
    print(f"🧪 Running dependency tests")
    print(f"{'=' * 50}")
    
    # List of dependencies to test (module name, import statement)
    dependencies = [
        ("fastapi", "import fastapi"),
        ("uvicorn", "import uvicorn"),
        ("langchain", "import langchain"),
        ("streamlit", "import streamlit"),
        ("langdetect", "import langdetect; print(f'langdetect is installed')"),
        ("sentence_transformers", "from sentence_transformers import SentenceTransformer"),
        ("faiss", "import faiss")
    ]
    
    all_passed = True
    for name, import_statement in dependencies:
        try:
            print(f"Testing {name}... ", end="")
            exec(import_statement)
            print("✅")
        except ImportError as e:
            print(f"❌ - {e}")
            all_passed = False
        except Exception as e:
            print(f"⚠️ - {e}")
    
    if all_passed:
        print("\n✅ All dependency tests passed!")
    else:
        print("\n⚠️ Some dependency tests failed!")
    
    return all_passed


def main():
    print("🚀 Starting project update and dependency check")
    print(f"Working directory: {os.getcwd()}")
    
    # Update from git
    run_command("git pull", "Pulling latest changes from git")
    
    # Update poetry dependencies
    run_command("poetry lock", "Updating poetry lock file")
    run_command("poetry install", "Installing dependencies")
    
    # Check if dependencies are working
    check_dependencies()
    
    print("\n✨ Update and test process completed!")


if __name__ == "__main__":
    main() 
    