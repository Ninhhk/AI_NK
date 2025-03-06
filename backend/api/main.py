from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.api.document_routes import router as document_router
from backend.api.slide_routes import router as slide_router

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