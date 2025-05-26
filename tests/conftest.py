"""
Test configuration and fixtures for AI NVCB test suite.
"""

import os
import pytest
import asyncio
from pathlib import Path
from typing import Generator, Dict, Any
import tempfile
import shutil

# Set test environment variables
os.environ["TESTING"] = "1"
os.environ["LOG_LEVEL"] = "debug"

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_text_file(temp_dir: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample text file for testing document analysis.")
    return file_path


@pytest.fixture
def api_config() -> Dict[str, Any]:
    """Configuration for API tests."""
    return {
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "headers": {
            "Content-Type": "application/json"
        }
    }


@pytest.fixture
def streamlit_config() -> Dict[str, Any]:
    """Configuration for Streamlit tests."""
    return {
        "base_url": "http://localhost:8501",
        "timeout": 30
    }


@pytest.fixture
def mock_ollama_response() -> Dict[str, Any]:
    """Mock response from Ollama API."""
    return {
        "model": "llama3.1:8b",
        "response": "This is a mock response from Ollama",
        "done": True,
        "created_at": "2024-01-01T00:00:00Z",
        "context": [1, 2, 3, 4, 5]
    }


# Test markers
pytest_plugins = []

# Mark slow tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "frontend: marks tests as frontend tests"
    )
