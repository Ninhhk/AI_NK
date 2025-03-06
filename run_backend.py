import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

import uvicorn

def main():
    # Load environment variables if needed
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Starting the backend server...")
    print(f"Project root: {project_root}")
    print(f"Python path: {sys.path}")
    
    # Run the server
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    main() 