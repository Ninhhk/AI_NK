"""Simple model management routes."""
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from typing import Dict, List, Optional, Any
import requests
import json
import os
from pydantic import BaseModel
from backend.model_management.system_prompt_manager import system_prompt_manager

router = APIRouter()

# Ollama API settings
OLLAMA_API_URL = "http://localhost:11434"

class Model(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str

class ModelList(BaseModel):
    models: List[Model]

class ModelResponse(BaseModel):
    message: str
    success: bool

# Current model tracking
current_model = "gemma3:1b"  # Default model

@router.get("/models", response_model=ModelList)
def get_models():
    """List available models from Ollama."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        response.raise_for_status()
        models_data = response.json().get("models", [])
        
        models = []
        for model_data in models_data:
            models.append(
                Model(
                    name=model_data.get("name"),
                    modified_at=model_data.get("modified_at", ""),
                    size=model_data.get("size", 0),
                    digest=model_data.get("digest", "")
                )
            )
        
        return {"models": models}
    except Exception as e:
        # Return empty list on error
        return {"models": []}

@router.post("/models/pull", response_model=ModelResponse)
def pull_model(model_name: str = Form(...)):
    """Pull a model from Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        # Just initiate the pull and return success
        return {"message": f"Started pulling model {model_name}", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/models/{model_name}", response_model=ModelResponse)
def delete_model(model_name: str):
    """Delete a model from Ollama."""
    try:
        response = requests.delete(
            f"{OLLAMA_API_URL}/api/delete",
            json={"name": model_name}
        )
        response.raise_for_status()
        return {"message": f"Model {model_name} deleted", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model selection for slide generation
@router.get("/current-model", response_model=Dict[str, str])
def get_current_model():
    """Get current model for slide generation."""
    global current_model
    return {"model_name": current_model}

@router.post("/set-model", response_model=Dict[str, str])
def set_model(model_name: str = Form(...)):
    """Set model for slide generation."""
    global current_model
    current_model = model_name
    return {"model_name": model_name, "message": f"Model changed to {model_name}"}

@router.get("/system-prompt", response_model=Dict[str, str])
def get_system_prompt():
    """
    Get the current system prompt used by models.
    
    Returns:
    - A dictionary containing the current system prompt
    """
    return {"system_prompt": system_prompt_manager.get_system_prompt()}

@router.post("/system-prompt", response_model=Dict[str, str])
def set_system_prompt(system_prompt: str = Form(...)):
    """
    Set the system prompt to use for all model interactions.
    
    Parameters:
    - system_prompt: The system prompt to set
    
    Returns:
    - A dictionary containing the updated system prompt
    """
    try:
        system_prompt_manager.set_system_prompt(system_prompt)
        return {"system_prompt": system_prompt, "message": "System prompt updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
