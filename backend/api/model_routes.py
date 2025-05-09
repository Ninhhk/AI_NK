"""API routes for model management."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from typing import Dict, List, Optional
from pydantic import BaseModel

from backend.model_management.model_manager import model_manager, ModelInfo, ModelDownloadProgress

router = APIRouter()

class ModelResponse(BaseModel):
    """Response model for model list."""
    models: List[ModelInfo]

class ModelPullRequest(BaseModel):
    """Request model for pulling a model."""
    name: str

class ModelPullResponse(BaseModel):
    """Response model for model pull request."""
    task_id: str

class ModelProgressResponse(BaseModel):
    """Response model for model progress."""
    model: str
    digest: Optional[str] = None
    pull_progress: Optional[int] = None  # 0-1000 (per mille for precision)
    done: bool = False
    error: Optional[str] = None

class AllProgressResponse(BaseModel):
    """Response model for all progress."""
    downloads: Dict[str, ModelProgressResponse]

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool

@router.get("/models", response_model=ModelResponse)
async def get_models():
    """Get a list of available models."""
    return {"models": await model_manager.get_models()}

@router.get("/models/{model_name}", response_model=Optional[ModelInfo])
async def get_model_info(model_name: str):
    """Get information about a specific model."""
    model = await model_manager.get_model_info(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    return model

@router.post("/models/pull", response_model=ModelPullResponse)
async def pull_model(request: ModelPullRequest):
    """Start pulling a model."""
    task_id = await model_manager.pull_model(request.name)
    return {"task_id": task_id}

@router.get("/models/pull/{model_name}/progress", response_model=ModelProgressResponse)
async def get_model_progress(model_name: str):
    """Get progress for a specific model pull."""
    progress = await model_manager.get_download_progress(model_name)
    return progress

@router.get("/models/pull/progress", response_model=AllProgressResponse)
async def get_all_progress():
    """Get progress for all active model pulls."""
    progress = await model_manager.get_all_download_progress()
    return {"downloads": progress}

@router.delete("/models/pull/{model_name}/cancel", response_model=MessageResponse)
async def cancel_model_pull(model_name: str):
    """Cancel a model pull."""
    success = await model_manager.cancel_model_pull(model_name)
    return {"message": f"Model pull for {model_name} cancelled", "success": success}

@router.delete("/models/{model_name}", response_model=MessageResponse)
async def delete_model(model_name: str):
    """Delete a model."""
    success = await model_manager.delete_model(model_name)
    return {"message": f"Model {model_name} deleted", "success": success}

@router.post("/models/upload", response_model=MessageResponse)
async def upload_model(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form(None)
):
    """Upload a GGUF model file."""
    model_name = await model_manager.upload_model(file, model_name)
    return {"message": f"Model {model_name} uploaded and created", "success": True}
