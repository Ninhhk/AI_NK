from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="AI NVCB API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from api.document_routes import router as document_router
from api.slide_routes import router as slide_router

app.include_router(document_router, prefix="/api/documents", tags=["Documents"])
app.include_router(slide_router, prefix="/api/slides", tags=["Slides"])

if __name__ == "__main__":
    print("Starting the backend server...")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    ) 