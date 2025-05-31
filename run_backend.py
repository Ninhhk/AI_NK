import os
import sys
from pathlib import Path
import argparse

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

import uvicorn


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the AI-NVCB backend server")
    parser.add_argument(
        "--skip-validation", 
        action="store_true", 
        help="Skip environment validation"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default=os.environ.get("HOST", "0.0.0.0"), 
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("PORT", "8000")), 
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default=os.environ.get("LOG_LEVEL", "info"), 
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        default=os.environ.get("RELOAD", "").lower() in ("true", "1", "yes"),
        help="Enable auto-reload for development"
    )
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables if needed
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run environment validation if not skipped
    if not args.skip_validation and validate_environment is not None:
        print("Running environment validation...")
        validation_result = validate_environment(
            # Require Python 3.8+ (adjust based on your needs)
            min_python_version=(3, 8, 0),
            # Check for required models on Ollama
            required_models=[os.environ.get("MODEL_NAME", "qwen3:8b")],
        )
        
        # Exit if validation fails, unless using the --continue-on-validation-fail flag
        if not validation_result["overall_valid"]:
            print("\n⚠️ Environment validation failed!")
            print("You can fix the issues reported above or run with --skip-validation to bypass this check.")
            print("Note: Running with an invalid environment may cause unexpected errors.")
            
            # Ask user if they want to continue anyway
            response = input("\nContinue anyway? (y/N): ").strip().lower()
            if response not in ("y", "yes"):
                print("Exiting...")
                sys.exit(1)
    
    print("Starting the backend server...")
    print(f"Project root: {project_root}")
    print(f"Python path: {sys.path}")
    
    # Run the server
    uvicorn.run(
        "backend.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main() 