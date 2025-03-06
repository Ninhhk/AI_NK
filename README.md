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
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the backend server:
   ```bash
   poetry run python backend/app.py
   ```

2. Start the frontend application:
   ```bash
   poetry run streamlit run frontend/app.py
   ```

## Development

- Use Poetry for dependency management
- Follow PEP 8 style guidelines
- Write tests for new features

## License

MIT License - See LICENSE file for details 