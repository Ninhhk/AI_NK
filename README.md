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

## Installation

1. Clone the repository
2. Install Poetry (if not already installed):
   ```bash
   pip install poetry
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Set up environment variables:
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

## Development

- Use Poetry for dependency management
- Follow PEP 8 style guidelines
- Write tests for new features

## License

MIT License - See LICENSE file for details 