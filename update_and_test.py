#!/usr/bin/env python
"""
Script to automate project updates, dependency management, and testing.
This script will:
1. Stash any local changes (optional)
2. Pull the latest changes from git
3. Update poetry dependencies
4. Run basic dependency tests to verify everything works
5. Restore stashed changes (if any)

Usage:
    python update_and_test.py [--continue-on-error] [--skip-stash] [--stash-only]

Options:
    --continue-on-error  Continue even if some steps fail
    --skip-stash         Don't stash local changes before updating
    --stash-only         Only stash changes, don't update or pull
    --no-restore         Don't restore stashed changes after updating
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Update project and check dependencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue even if some steps fail"
    )
    parser.add_argument(
        "--skip-stash",
        action="store_true",
        help="Skip stashing local changes"
    )
    parser.add_argument(
        "--stash-only",
        action="store_true",
        help="Only stash changes, don't update or pull"
    )
    parser.add_argument(
        "--no-restore",
        action="store_true",
        help="Don't restore stashed changes after updating"
    )
    return parser.parse_args()


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
        if not args.continue_on_error:
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
        ("faiss", "import faiss"),
        ("openai", "import openai"),
        ("requests", "import requests"),
        ("pandas", "import pandas"),
        ("numpy", "import numpy")
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
    
    # Additional checks for key functionality
    try:
        print("Testing FastAPI app import... ", end="")
        from backend.api.main import app
        print("✅")
    except Exception as e:
        print(f"❌ - {e}")
        all_passed = False
    
    try:
        print("Testing Streamlit app import... ", end="")
        # Basic import test for frontend
        import sys
        import os
        sys.path.append(os.path.join(os.getcwd(), 'frontend'))
        print("✅")
    except Exception as e:
        print(f"❌ - {e}")
        all_passed = False
    
    if all_passed:
        print("\n✅ All dependency tests passed!")
    else:
        print("\n⚠️ Some dependency tests failed!")
    
    return all_passed


def check_git_conflicts(stash_index=0):
    """Check if applying stash will cause conflicts with current changes"""
    try:
        # Try a dry run of git stash apply to check for conflicts
        result = subprocess.run(
            f"git stash apply --index {stash_index} --check",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return False  # No conflicts
    except subprocess.CalledProcessError:
        return True  # Conflicts detected


def main():
    global args
    args = parse_args()
    
    print("🚀 Starting project update and dependency check")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if there are local changes that need stashing
    status_success, git_status = run_command("git status --porcelain", "Checking Git status")
    has_local_changes = git_status.strip() != ""
    
    # Stash local changes if present and not skipped
    stashed = False
    stash_name = f"auto-stash-{time.strftime('%Y%m%d-%H%M%S')}"
    
    if has_local_changes and not args.skip_stash:
        print("📦 Local changes detected, stashing them temporarily...")
        stash_success, stash_output = run_command(f"git stash push -m \"{stash_name}\"", "Stashing local changes")
        stashed = stash_success and "No local changes to save" not in stash_output
    elif has_local_changes and args.skip_stash:
        print("⚠️ Local changes detected but stashing is skipped. This might cause conflicts.")
    
    # If stash-only mode, exit after stashing
    if args.stash_only:
        if stashed:
            print("\n✨ Changes stashed successfully!")
        else:
            print("\n⚠️ No changes were stashed.")
        return
    
    try:
        # Update from git
        run_command("git pull", "Pulling latest changes from git")
        
        # Update poetry dependencies
        run_command("poetry lock", "Updating poetry lock file")
        run_command("poetry install", "Installing dependencies")
        
        # Check if dependencies are working
        check_dependencies()
    finally:
        # Restore stashed changes if needed and not disabled
        if stashed and not args.no_restore:
            # Get stash index (should be 0 if we just stashed)
            stash_index = 0
            _, stash_list = run_command("git stash list", "Checking stash list")
            for i, line in enumerate(stash_list.strip().split('\n')):
                if stash_name in line:
                    stash_index = i
                    break
            
            # Check for potential conflicts
            will_conflict = check_git_conflicts(stash_index)
            
            if will_conflict:
                print("\n⚠️ Warning: Restoring your stashed changes might cause conflicts.")
                print("You have a few options:")
                print("1. Apply stash anyway (might cause conflicts)")
                print("2. Keep changes stashed (stash name: " + stash_name + ")")
                print("3. Create a branch with your stashed changes")
                
                choice = input("\nChoose an option (1-3) [1]: ").strip() or "1"
                
                if choice == "1":
                    print("📦 Attempting to restore your local changes...")
                    run_command(f"git stash pop stash@{{{stash_index}}}", "Restoring stashed changes")
                elif choice == "2":
                    print(f"📦 Your changes remain in the stash as '{stash_name}'")
                    print(f"   To restore later: git stash apply stash@{{{stash_index}}}")
                elif choice == "3":
                    branch_name = f"stashed-changes-{time.strftime('%Y%m%d-%H%M%S')}"
                    print(f"📦 Creating new branch '{branch_name}' with your stashed changes...")
                    run_command(f"git checkout -b {branch_name}", "Creating new branch")
                    run_command(f"git stash apply stash@{{{stash_index}}}", "Applying stashed changes to new branch")
                    run_command(f"git stash drop stash@{{{stash_index}}}", "Dropping stash after creating branch")
            else:
                print("📦 Restoring your local changes...")
                run_command(f"git stash pop stash@{{{stash_index}}}", "Restoring stashed changes")
        elif stashed and args.no_restore:
            print(f"\n📦 Your changes remain in the stash as '{stash_name}'")
            print(f"   To restore later: git stash apply")
    
    print("\n✨ Update and test process completed!")


if __name__ == "__main__":
    main() 
    