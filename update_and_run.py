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
import json
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init()

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def run_command(command, cwd=None, shell=False):
    """Run a command and print its output"""
    print(f"\n{Fore.BLUE}[Running]{Style.RESET_ALL} {command}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd or project_root,
            shell=shell,
            check=True,
            text=True,
            capture_output=True
        )
        print(f"{Fore.GREEN}[Success]{Style.RESET_ALL} {command}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[Error]{Style.RESET_ALL} {command} failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        return False

def update_repository():
    """Pull the latest changes from the git repository"""
    print(f"\n{Fore.BLUE}==== Updating repository ===={Style.RESET_ALL}")
    return run_command(["git", "pull"])

def update_dependencies():
    """Update Poetry dependencies"""
    print(f"\n{Fore.BLUE}==== Updating dependencies ===={Style.RESET_ALL}")
    
    # Check if pyproject.toml exists
    if not os.path.isfile(os.path.join(project_root, "pyproject.toml")):
        print(f"{Fore.RED}[Error] pyproject.toml not found. Cannot update dependencies.{Style.RESET_ALL}")
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
                
        print(f"{Fore.YELLOW}[Warning] Could not find a suitable terminal emulator. Running in background instead.{Style.RESET_ALL}")
        subprocess.Popen(command, shell=True)
        return False
    else:
        print(f"{Fore.YELLOW}[Warning] Unsupported operating system: {system}. Running in background.{Style.RESET_ALL}")
        subprocess.Popen(command, shell=True)
        return False

def run_backend():
    """Run the backend server in a new terminal window"""
    print(f"\n{Fore.BLUE}==== Starting backend server in new terminal ===={Style.RESET_ALL}")
    backend_cmd = f"cd \"{project_root}\" && python run_backend.py"
    success = open_new_terminal(backend_cmd, "Backend Server")
    if success:
        print("Backend server started in a new terminal window.")
    return success

def run_frontend():
    """Run the Streamlit frontend in a new terminal window"""
    print(f"\n{Fore.BLUE}==== Starting frontend server in new terminal ===={Style.RESET_ALL}")
    frontend_cmd = f"cd \"{project_root}\" && streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0"
    success = open_new_terminal(frontend_cmd, "Frontend Server")
    if success:
        print("Frontend server started in a new terminal window.")
    return success

def print_api_info():
    """Print information about available API endpoints"""
    print(f"\n{Fore.GREEN}==== Application started successfully ===={Style.RESET_ALL}")
    print(f"{Fore.BLUE}Backend API server running at:{Style.RESET_ALL} http://localhost:8000")
    print(f"{Fore.CYAN}Available API endpoints:{Style.RESET_ALL}")
    print(f"  - http://localhost:8000/api/documents/analyze {Fore.YELLOW}(POST){Style.RESET_ALL}")
    print(f"  - http://localhost:8000/api/documents/chat-history/{{document_id}} {Fore.YELLOW}(GET){Style.RESET_ALL}")
    print(f"  - http://localhost:8000/api/documents/generate-quiz {Fore.YELLOW}(POST){Style.RESET_ALL}")
    print(f"  - http://localhost:8000/api/documents/health {Fore.YELLOW}(GET){Style.RESET_ALL}")
    print()
    print(f"{Fore.BLUE}Frontend UI available at:{Style.RESET_ALL} http://localhost:8501")
    print()
    print(f"{Fore.YELLOW}NOTE:{Style.RESET_ALL} The backend doesn't serve a web page at the root URL (http://localhost:8000/).")
    print("      You should see \"404 Not Found\" if you access that URL directly - this is normal.")
    print("      The backend health check at http://localhost:8000/api/documents/health should return {\"status\": \"healthy\"}.")
    
    curl_cmd = "curl" if platform.system() != "Windows" else "curl.exe"
    print(f"      You can test it with: {Fore.CYAN}{curl_cmd} http://localhost:8000/api/documents/health{Style.RESET_ALL}")
    print()
    print(f"{Fore.GREEN}The application is now running in separate terminal windows.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}You can close each terminal window individually to stop the services.{Style.RESET_ALL}")

def main():
    try:
        # Check if colorama is installed, if not, try to install it
        try:
            import colorama
        except ImportError:
            print("Installing colorama for colored output...")
            subprocess.run([sys.executable, "-m", "pip", "install", "colorama"], check=True)
            print("Colorama installed successfully.")
            from colorama import Fore, Style, init
            init()
            
        # Update repository if it's a git repo
        if os.path.isdir(os.path.join(project_root, ".git")):
            if not update_repository():
                print(f"{Fore.YELLOW}Warning: Repository update failed, continuing with local version.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Warning: Not a git repository, skipping update.{Style.RESET_ALL}")
        
        # Update dependencies
        if not update_dependencies():
            print(f"{Fore.RED}Error: Failed to update dependencies.{Style.RESET_ALL}")
            return 1
        
        # Start the backend server in a new terminal
        if not run_backend():
            print(f"{Fore.RED}Error: Failed to start backend server.{Style.RESET_ALL}")
            return 1
        
        # Wait for backend to initialize (5 seconds)
        print("Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start the frontend server in a new terminal
        if not run_frontend():
            print(f"{Fore.RED}Error: Failed to start frontend server.{Style.RESET_ALL}")
            return 1
        
        # Print API information
        print_api_info()
        
        # Exit the launcher
        input(f"{Fore.YELLOW}Press Enter to exit this launcher...{Style.RESET_ALL}")
        return 0
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Received interrupt signal.{Style.RESET_ALL}")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 