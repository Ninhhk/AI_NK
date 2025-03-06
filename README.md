# AI-NVCB

An AI-powered application that combines document analysis and presentation generation capabilities.

## Features

- Document Analysis
  - PDF document processing and analysis
  - LLM-powered document summarization
  - Question answering on documents
  
- Presentation Generation
  - Automatic slide generation from content
  - Support for various input formats
  - Customizable presentation templates

## Project Structure

```
AI_NVCB/
├── frontend/        # Streamlit and Flask frontend applications
├── backend/         # Core backend services and API
├── utils/          # Shared utilities and helper functions
├── data/           # Data storage and resources
└── tests/          # Test suite
```

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **CPU**: Minimum 4 cores (8+ cores recommended for better performance)
- **RAM**: Minimum 8GB (16GB+ recommended)
- **GPU**: Optional but recommended for faster model inference (NVIDIA GPU with CUDA support)
- **Disk Space**: At least 10GB free space
- **Network**: Stable internet connection for model downloads

## Prerequisites

- **Python**: Version 3.8 or higher
- **Ollama**: Latest version for running local LLMs
- **Git**: For cloning the repository
- **Node.js**: Version 14+ (if using any JavaScript components)
- **PDF processing libraries**: System libraries for PyMuPDF/pdf2image (e.g., poppler on Linux/macOS)

## Installation

1. Install prerequisite software:
   - Install [Python 3.8+](https://www.python.org/downloads/)
   - Install [Ollama](https://ollama.ai/download)
   - Install [Git](https://git-scm.com/downloads)
   - Install system dependencies:
     - **Windows**: No additional steps needed
     - **macOS**: `brew install poppler`
     - **Linux**: `sudo apt-get install poppler-utils`

2. Clone the repository
   ```bash
   git clone https://github.com/Ninhhk/AI_NK.git
   cd AI_NK
   ```

3. Install Poetry (if not already installed):
   ```bash
   pip install poetry
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Set up environment variables(if there is no .env file):
   Create a `.env` file with:
   ```
   MODEL_NAME=qwen2.5:7b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

## Usage

1. Start Ollama server and ensure your model is available:
   ```bash
   ollama run qwen2.5:7b
   ```

2. Start the backend server:
   ```bash
   python run_backend.py
   ```
3. Start the frontend application:
   ```bash
   streamlit run frontend/app.py
   ```
4. Access the application in your browser at http://localhost:8501
5. You may have to wait 1-2m for the backend server complete its startup.

## Development

- Use Poetry for dependency management
- Follow PEP 8 style guidelines
- Write tests for new features

## License

MIT License - See LICENSE file for details 