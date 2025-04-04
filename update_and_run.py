#!/usr/bin/env python3
"""
Script to update, install dependencies, and run the AI NVCB application.
This script will:
1. Pull the latest changes from git
2. Update Poetry dependencies
3. Start both backend and frontend servers
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Store subprocess objects
processes = []

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

def run_backend():
    """Run the backend server"""
    print("\n==== Starting backend server ====")
    backend_process = subprocess.Popen(
        [sys.executable, os.path.join(project_root, "run_backend.py")],
        cwd=project_root,
        text=True
    )
    processes.append(backend_process)
    print(f"Backend server started (PID: {backend_process.pid})")
    return True

def run_frontend():
    """Run the Streamlit frontend"""
    print("\n==== Starting frontend server ====")
    frontend_process = subprocess.Popen(
        ["streamlit", "run", os.path.join(project_root, "frontend", "app.py"), "--server.port=8501", "--server.address=0.0.0.0"],
        cwd=project_root,
        text=True
    )
    processes.append(frontend_process)
    print(f"Frontend server started (PID: {frontend_process.pid})")
    return True

def cleanup(signum=None, frame=None):
    """Clean up processes when the script is terminated"""
    print("\n==== Shutting down servers ====")
    for process in processes:
        if process.poll() is None:  # If process is still running
            print(f"Terminating process {process.pid}")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Process {process.pid} did not terminate gracefully, killing...")
                process.kill()
    print("All processes terminated.")
    sys.exit(0)

def main():
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
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
        
        # Start the backend server
        if not run_backend():
            print("Error: Failed to start backend server.")
            return 1
        
        # Wait for backend to initialize (5 seconds)
        print("Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start the frontend server
        if not run_frontend():
            print("Error: Failed to start frontend server.")
            cleanup()
            return 1
        
        print("\n==== Application started successfully ====")
        print("Backend server running at: http://localhost:8000")
        print("Frontend available at: http://localhost:8501")
        print("Press Ctrl+C to stop all servers.")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for process in processes[:]:
                if process.poll() is not None:
                    # Process has terminated
                    print(f"Process {process.pid} terminated unexpectedly with code {process.returncode}")
                    processes.remove(process)
            
            # If all processes have terminated, exit
            if not processes:
                print("All processes have terminated. Exiting.")
                return 1
                
    except KeyboardInterrupt:
        print("\nReceived interrupt signal.")
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 