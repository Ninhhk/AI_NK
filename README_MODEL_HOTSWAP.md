# AI NVCB with Ollama Model Hotswap

This update adds a powerful model management system to AI NVCB, allowing you to download, upload, and switch between different Ollama models for slide generation.

## New Features

- **Model Management UI**: A dedicated page to manage your Ollama models
- **Model Downloading**: Download models directly from Ollama with progress tracking
- **Model Upload**: Upload your own GGUF model files
- **Model Switching**: Seamlessly switch between models for slide generation
- **Progress Tracking**: Real-time progress tracking for model downloads

## Setup Instructions

1. Start Ollama server:
   ```bash
   ollama serve
   ```

2. Start the backend and frontend (in separate terminals):
   ```bash
   # Terminal 1: Backend
   python run_backend.py

   # Terminal 2: Frontend
   python run_frontend.py
   ```

3. Access the application in your browser at http://localhost:8501

## Using the Model Management

1. Go to the "Model Management" page in the sidebar
2. Download models by entering their name (e.g., `llama3:8b`, `gemma3:1b`)
3. Track download progress in the "Active Downloads" tab
4. Upload your own GGUF models in the "Add New Model" tab
5. Select a model to use in the slide generation page

## API Endpoints

The following new API endpoints have been added:

### Model Management API
- `GET /api/ollama/models` - List all available models
- `GET /api/ollama/models/{model_name}` - Get model details
- `POST /api/ollama/models/pull` - Start downloading a model
- `GET /api/ollama/models/pull/{model_name}/progress` - Get download progress
- `GET /api/ollama/models/pull/progress` - Get all download progress
- `DELETE /api/ollama/models/pull/{model_name}/cancel` - Cancel a download
- `DELETE /api/ollama/models/{model_name}` - Delete a model
- `POST /api/ollama/models/upload` - Upload a model file

### Slide Generation API
- `GET /api/slides/current-model` - Get current model
- `POST /api/slides/set-model` - Set model for slide generation

## Technical Details

The model hotswap system works by:

1. Maintaining a singleton model manager service
2. Tracking download progress in real-time
3. Using streaming responses for progress updates
4. Providing a Svelte-inspired reactive store pattern
5. Supporting immediate model swapping in the slide service

## Troubleshooting

- If model downloads fail, ensure Ollama is running and accessible
- For large model uploads, increase the timeout in `run_backend.py`
- If a model is stuck at 0%, try canceling and restarting the download
