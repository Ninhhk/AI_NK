"""Model manager service for handling Ollama models."""
import logging
import json
import asyncio
import aiohttp
import hashlib
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from fastapi import HTTPException, UploadFile
from datetime import datetime
import tempfile

from .config import OLLAMA_API_BASE_URL, ModelInfo, ModelDownloadProgress

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """Service for managing Ollama models."""
    
    def __init__(self):
        """Initialize the model manager."""
        self.active_downloads: Dict[str, ModelDownloadProgress] = {}
        self._model_cache: List[ModelInfo] = []
        self._model_cache_time: Optional[datetime] = None
        self._cache_validity = 60  # seconds
    
    async def get_models(self) -> List[ModelInfo]:
        """Get a list of available models from Ollama."""
        # Return cached models if available and not expired
        if self._model_cache and self._model_cache_time:
            time_since_cache = (datetime.now() - self._model_cache_time).total_seconds()
            if time_since_cache < self._cache_validity:
                return self._model_cache
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{OLLAMA_API_BASE_URL}/api/tags") as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch models from Ollama: Status {response.status}")
                        return []  # Return empty list instead of raising exception
                    
                    data = await response.json()
                    models = []
                    
                    for model in data.get("models", []):
                        models.append(
                            ModelInfo(
                                name=model.get("name"),
                                modified_at=model.get("modified_at", ""),
                                size=model.get("size", 0),
                                digest=model.get("digest", ""),
                                details=model
                            )
                        )
                    
                    # Update cache
                    self._model_cache = models
                    self._model_cache_time = datetime.now()
                    
                    return models
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return []  # Return empty list instead of raising exception
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        models = await self.get_models()
        for model in models:
            if model.name == model_name:
                return model
        return None
    
    async def pull_model(self, model_name: str) -> str:
        """Start pulling a model and return a task ID."""
        # Check if model is already being downloaded
        if model_name in self.active_downloads:
            raise HTTPException(status_code=400, detail=f"Model {model_name} is already being downloaded")
        
        # Create a download progress tracker
        progress = ModelDownloadProgress(model=model_name, done=False)
        self.active_downloads[model_name] = progress
        
        # Start download as a background task
        asyncio.create_task(self._pull_model_task(model_name))
        
        return model_name
    
    async def get_download_progress(self, model_name: str) -> ModelDownloadProgress:
        """Get the download progress for a model."""
        if model_name not in self.active_downloads:
            raise HTTPException(status_code=404, detail=f"No active download for model {model_name}")
        
        return self.active_downloads[model_name]
    
    async def get_all_download_progress(self) -> Dict[str, ModelDownloadProgress]:
        """Get all active download progress."""
        return self.active_downloads
    
    async def cancel_model_pull(self, model_name: str) -> bool:
        """Cancel an ongoing model pull."""
        if model_name not in self.active_downloads:
            raise HTTPException(status_code=404, detail=f"No active download for model {model_name}")
        
        # Mark as cancelled and remove from active downloads
        del self.active_downloads[model_name]
        
        # Try to delete the partial model
        try:
            await self.delete_model(model_name)
        except Exception as e:
            logger.warning(f"Failed to delete partial model {model_name}: {str(e)}")
        
        return True
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model from Ollama."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{OLLAMA_API_BASE_URL}/api/delete",
                    json={"name": model_name}
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to delete model {model_name}: {text}"
                        )
                    
                    # Invalidate cache
                    self._model_cache = []
                    self._model_cache_time = None
                    
                    return True
        except Exception as e:
            logger.error(f"Error deleting model {model_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")
    
    async def upload_model(self, file: UploadFile, model_name: Optional[str] = None) -> str:
        """Upload a GGUF model file to Ollama."""
        if not file.filename.endswith(".gguf"):
            raise HTTPException(status_code=400, detail="Only GGUF files are supported")
        
        # Generate model name if not provided
        if not model_name:
            model_name = os.path.splitext(file.filename)[0].lower()
        
        try:
            # Create a temp file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Calculate SHA256 hash for blob
            sha256_hash = hashlib.sha256(content).hexdigest()
            
            # Upload blob to Ollama
            async with aiohttp.ClientSession() as session:
                # First create blob
                async with session.post(
                    f"{OLLAMA_API_BASE_URL}/api/blobs",
                    json={"sha256": sha256_hash}
                ) as response:
                    blob_response = await response.json()
                    
                    # If the blob doesn't exist, upload it
                    if not blob_response.get("exists", False):
                        with open(temp_file_path, "rb") as f:
                            async with session.post(
                                f"{OLLAMA_API_BASE_URL}/api/blobs/{sha256_hash}",
                                data=f
                            ) as upload_response:
                                if upload_response.status != 200:
                                    text = await upload_response.text()
                                    raise HTTPException(
                                        status_code=upload_response.status,
                                        detail=f"Failed to upload blob: {text}"
                                    )
                
                # Create model referencing the blob
                modelfile_content = f"""
                FROM {sha256_hash}
                PARAMETER temperature 0.7
                PARAMETER top_k 50
                PARAMETER top_p 0.95
                PARAMETER stop "<|endoftext|>"
                """
                
                async with session.post(
                    f"{OLLAMA_API_BASE_URL}/api/create",
                    json={
                        "name": model_name,
                        "modelfile": modelfile_content
                    }
                ) as create_response:
                    if create_response.status != 200:
                        text = await create_response.text()
                        raise HTTPException(
                            status_code=create_response.status,
                            detail=f"Failed to create model: {text}"
                        )
                    
                    # Invalidate cache
                    self._model_cache = []
                    self._model_cache_time = None
                    
                    return model_name
        except Exception as e:
            logger.error(f"Error uploading model: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upload model: {str(e)}")
        finally:
            # Clean up temp file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    async def _pull_model_task(self, model_name: str) -> None:
        """Background task for pulling a model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{OLLAMA_API_BASE_URL}/api/pull",
                    json={"name": model_name},
                    headers={"Accept": "application/x-ndjson"}
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        self.active_downloads[model_name].error = f"Failed to pull model: {text}"
                        self.active_downloads[model_name].done = True
                        return
                    
                    # Process the streaming response
                    async for line in response.content:
                        if model_name not in self.active_downloads:
                            # Download was cancelled
                            return
                        
                        try:
                            line_str = line.decode('utf-8').strip()
                            if not line_str:
                                continue
                            
                            data = json.loads(line_str)
                            
                            # Update progress based on stream data
                            if "status" in data:
                                progress = self.active_downloads[model_name]
                                
                                if "digest" in data:
                                    progress.digest = data["digest"]
                                
                                if "completed" in data and "total" in data:
                                    # Calculate progress in per mille for precision
                                    if data["total"] > 0:
                                        progress.pull_progress = int((data["completed"] / data["total"]) * 1000)
                                    else:
                                        progress.pull_progress = 0
                                
                                # Update stored progress
                                self.active_downloads[model_name] = progress
                        except Exception as e:
                            logger.error(f"Error processing stream: {str(e)}")
                    
                    # Mark as completed
                    self.active_downloads[model_name].done = True
                    self.active_downloads[model_name].pull_progress = 1000  # 100.0%
                    
                    # Invalidate cache
                    self._model_cache = []
                    self._model_cache_time = None
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {str(e)}")
            if model_name in self.active_downloads:
                self.active_downloads[model_name].error = str(e)
                self.active_downloads[model_name].done = True

# Create singleton instance
model_manager = ModelManager()
