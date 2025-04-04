#!/usr/bin/env python3
"""
Script to update, install dependencies, and run the AI NVCB application in separate terminals.
This script will:
1. Pull the latest changes from git
2. Update Poetry dependencies
3. Start both backend and frontend servers in separate terminal windows
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def run_command(command, cwd=None, shell=False):
    """Run a command and print its output"""
    print(f"\n[Running] {command}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd or project_root,
            shell=shell,
            check=True,
            text=True,
            capture_output=True
        )
        print(f"[Success] {command}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Error] {command} failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        return False

def update_repository():
    """Pull the latest changes from the git repository"""
    print("\n==== Updating repository ====")
    return run_command(["git", "pull"])

def update_dependencies():
    """Update Poetry dependencies"""
    print("\n==== Updating dependencies ====")
    
    # Check if pyproject.toml exists
    if not os.path.isfile(os.path.join(project_root, "pyproject.toml")):
        print("[Error] pyproject.toml not found. Cannot update dependencies.")
        return False
        
    # Update the lock file
    lock_success = run_command(["poetry", "lock"])
    if not lock_success:
        return False
        
    # Install dependencies
    return run_command(["poetry", "install"])

def open_new_terminal(command, title=None):
    """Open a new terminal window with the given command"""
    system = platform.system()
    
    if system == "Windows":
        # Windows - use start command with title
        terminal_title = title or "Terminal"
        cmd = f'start "{terminal_title}" cmd /k "{command}"'
        subprocess.Popen(cmd, shell=True)
        return True
        
    elif system == "Darwin":  # macOS
        # Use AppleScript to open a new Terminal window
        script = f'tell application "Terminal" to do script "{command}"'
        subprocess.Popen(["osascript", "-e", script])
        return True
        
    elif system == "Linux":
        # Try different terminal emulators
        terminal_cmds = [
            ["gnome-terminal", "--", "bash", "-c", f"{command}; exec bash"],
            ["xterm", "-e", f"{command}; exec bash"],
            ["konsole", "-e", f"{command}"],
            ["terminator", "-e", f"{command}"],
            ["xfce4-terminal", "-e", f"{command}"],
            ["lxterminal", "-e", f"{command}"]
        ]
        
        for term_cmd in terminal_cmds:
            try:
                subprocess.Popen(term_cmd)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
                
        print("[Warning] Could not find a suitable terminal emulator. Running in background instead.")
        subprocess.Popen(command, shell=True)
        return False
    else:
        print(f"[Warning] Unsupported operating system: {system}. Running in background.")
        subprocess.Popen(command, shell=True)
        return False

def run_backend():
    """Run the backend server in a new terminal window"""
    print("\n==== Starting backend server in new terminal ====")
    backend_cmd = f"cd \"{project_root}\" && python run_backend.py"
    success = open_new_terminal(backend_cmd, "Backend Server")
    if success:
        print("Backend server started in a new terminal window.")
    return success

def run_frontend():
    """Run the Streamlit frontend in a new terminal window"""
    print("\n==== Starting frontend server in new terminal ====")
    frontend_cmd = f"cd \"{project_root}\" && streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0"
    success = open_new_terminal(frontend_cmd, "Frontend Server")
    if success:
        print("Frontend server started in a new terminal window.")
    return success

def main():
    try:
        # Update repository if it's a git repo
        if os.path.isdir(os.path.join(project_root, ".git")):
            if not update_repository():
                print("Warning: Repository update failed, continuing with local version.")
        else:
            print("Warning: Not a git repository, skipping update.")
        
        # Update dependencies
        if not update_dependencies():
            print("Error: Failed to update dependencies.")
            return 1
        
        # Start the backend server in a new terminal
        if not run_backend():
            print("Error: Failed to start backend server.")
            return 1
        
        # Wait for backend to initialize (5 seconds)
        print("Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start the frontend server in a new terminal
        if not run_frontend():
            print("Error: Failed to start frontend server.")
            return 1
        
        print("\n==== Application started successfully ====")
        print("Backend server running at: http://localhost:8000")
        print("Frontend available at: http://localhost:8501")
        print("Services are running in separate terminal windows.")
        print("You can close each terminal window individually to stop the services.")
        
        # Exit the launcher
        input("Press Enter to exit this launcher...")
        return 0
                
    except KeyboardInterrupt:
        print("\nReceived interrupt signal.")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 