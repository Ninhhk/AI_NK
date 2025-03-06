import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    logger.info("Checking environment setup...")
    
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    
    # Check current directory and PYTHONPATH
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Check if main application file exists
    api_main = Path("api/main.py")
    if api_main.exists():
        logger.info(f"Found api/main.py: {api_main.absolute()}")
    else:
        logger.error(f"Could not find api/main.py in {api_main.absolute()}")
    
    # Try importing key dependencies
    try:
        import fastapi
        logger.info(f"FastAPI version: {fastapi.__version__}")
    except ImportError as e:
        logger.error(f"Failed to import FastAPI: {e}")
    
    try:
        import uvicorn
        logger.info(f"Uvicorn version: {uvicorn.__version__}")
    except ImportError as e:
        logger.error(f"Failed to import Uvicorn: {e}")

def test_imports():
    logger.info("Testing imports...")
    try:
        from api.main import app
        logger.info("Successfully imported FastAPI app")
        logger.info(f"App title: {app.title}")
        logger.info(f"Available routes: {[route.path for route in app.routes]}")
    except Exception as e:
        logger.error(f"Failed to import app: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        check_environment()
        test_imports()
    except Exception as e:
        logger.error(f"Debug script failed: {e}", exc_info=True)
        sys.exit(1) 