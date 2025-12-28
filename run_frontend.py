#!/usr/bin/env python
"""
Frontend Application Starter with Environment Validation

This script starts the Streamlit frontend application after validating
the environment to ensure all dependencies are properly set up.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Import environment validation utilities
try:
    from utils.environment import validate_environment
except ImportError:
    print("WARNING: Could not import environment validation utilities.")
    print("Running without environment validation.")
    validate_environment = None


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the AI-NVCB frontend application")
    parser.add_argument(
        "--skip-validation", 
        action="store_true", 
        help="Skip environment validation"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("STREAMLIT_SERVER_PORT", "8501")), 
        help="Port to run Streamlit on"
    )
    parser.add_argument(
        "--check-backend",
        action="store_true",
        default=True,
        help="Check if backend is running before starting"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default=os.environ.get("BACKEND_URL", "http://localhost:8000"),
        help="Backend URL to check"
    )
    return parser.parse_args()


def check_backend_availability(url: str) -> bool:
    """Check if the backend is available."""
    try:
        import requests
        response = requests.get(f"{url}/api/documents/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def main():
    """Run the Streamlit frontend application."""
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validate environment before starting
    if not args.skip_validation and validate_environment is not None:
        print("Running environment validation...")
        validation_result = validate_environment(
            # Require Python 3.8+ (adjust based on your needs)
            min_python_version=(3, 8, 0),
            # Check Ollama but don't require it
            check_ollama=True,
            required_models=[],  # Don't require specific models for frontend
            # Frontend-specific dependencies
            required_packages=["streamlit", "requests", "python-dotenv"],
        )
        
        # Warn but don't exit if validation fails
        if not validation_result["overall_valid"]:
            print("\n⚠️ Environment validation found issues!")
            print("The application may not function correctly.")
            response = input("\nContinue anyway? (Y/n): ").strip().lower()
            if response in ("n", "no"):
                print("Exiting...")
                sys.exit(1)
    
    # Check if backend is available if requested
    if args.check_backend:
        print(f"Checking backend availability at {args.backend_url}...")
        if not check_backend_availability(args.backend_url):
            print("\n⚠️ Backend server is not responding!")
            print(f"Make sure the backend is running at {args.backend_url}")
            print("You can start the backend with: python run_backend.py")
            response = input("\nContinue anyway? (y/N): ").strip().lower()
            if response not in ("y", "yes"):
                print("Exiting...")
                sys.exit(1)
    
    # Start the Streamlit application
    print(f"Starting Streamlit frontend on port {args.port}...")
    # Use the current interpreter to run Streamlit so it works without
    # requiring the user to activate a venv in their shell.
    streamlit_args = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port",
        str(args.port),
    ]
    
    # Add headless mode if in CI/CD or if specified in environment
    if os.environ.get("STREAMLIT_SERVER_HEADLESS", "").lower() in ("true", "1", "yes"):
        streamlit_args.extend(["--server.headless", "true"])
    
    # Run Streamlit
    try:
        subprocess.run(streamlit_args, check=True)
    except KeyboardInterrupt:
        print("\nStreamlit server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running Streamlit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 