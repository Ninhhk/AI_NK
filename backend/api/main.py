from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

from backend.api.document_routes import router as document_router
from backend.api.slide_routes import router as slide_router
from backend.api.simple_model_routes import router as model_router
from backend.api.cleanup_routes import router as cleanup_router
from backend.model_management.system_prompt_manager import system_prompt_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="AI NVCB API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document_router, prefix="/api/documents", tags=["Documents"])
app.include_router(slide_router, prefix="/api/slides", tags=["Slides"])
app.include_router(model_router, prefix="/api/ollama", tags=["Ollama Models"])
app.include_router(cleanup_router, prefix="/api/cleanup", tags=["Storage Cleanup"])

# Setup background cleaning tasks (runs on server startup)
@app.on_event("startup")
async def startup_event():
    try:
        from utils.cleanup import setup_cleaning_tasks
        
        logger.info("Setting up background cleaning tasks...")
        # Add environment variable configuration here if needed
        setup_cleaning_tasks(
            document_retention_days=30,  # Default is 30 days
            slide_retention_days=30,     # Default is 30 days
            upload_retention_hours=24    # Default is 24 hours
        )
        logger.info("Background cleaning tasks setup complete")
        
        # Ensure the system prompt is set correctly on startup
        vietnamese_prompt = "must answer in vietnamese, phải trả lời bằng tiếng việt"
        current_prompt = system_prompt_manager.get_system_prompt()
        
        if current_prompt != vietnamese_prompt:
            logger.info(f"Setting system prompt to: '{vietnamese_prompt}'")
            system_prompt_manager.set_system_prompt(vietnamese_prompt)
            logger.info("System prompt set successfully")
        else:
            logger.info(f"System prompt already set to: '{current_prompt}'")
    except Exception as e:
        logger.error(f"Error in startup event: {e}")
        # Don't fail startup, just log the error