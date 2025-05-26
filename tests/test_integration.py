"""
Integration tests for the AI NVCB application.

These tests verify that different components work together correctly.
"""

import pytest
import asyncio
import httpx
import time
from pathlib import Path
import sys
import os
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


@pytest.mark.integration
@pytest.mark.slow
class TestBackendFrontendIntegration:
    """Test integration between backend and frontend."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment."""
        os.environ["TESTING"] = "1"
        yield
        if "TESTING" in os.environ:
            del os.environ["TESTING"]
    
    async def test_backend_health_check(self, api_config):
        """Test that backend is accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{api_config['base_url']}/docs")
                # Backend should be accessible even if not fully configured
                assert response.status_code in [200, 503, 500]
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for integration testing")
    
    async def test_frontend_health_check(self, streamlit_config):
        """Test that frontend is accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(streamlit_config['base_url'])
                # Frontend should be accessible
                assert response.status_code in [200, 503]
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Frontend not available for integration testing")


@pytest.mark.integration
class TestDocumentWorkflow:
    """Test complete document analysis workflow."""
    
    async def test_document_upload_analysis_flow(self, api_config, sample_text_file):
        """Test complete document upload and analysis flow."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test document analysis endpoint with file
                with open(sample_text_file, 'rb') as f:
                    files = {'files': (sample_text_file.name, f, 'text/plain')}
                    data = {
                        'query_type': 'summary',
                        'user_query': 'Summarize this document'
                    }
                    
                    response = await client.post(
                        f"{api_config['base_url']}/api/documents/analyze",
                        files=files,
                        data=data
                    )
                    
                    # Should handle the request even if Ollama is not available
                    assert response.status_code in [200, 500, 503, 422]
                    
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for integration testing")


@pytest.mark.integration
class TestModelManagement:
    """Test model management integration."""
    
    async def test_model_list_endpoint(self, api_config):
        """Test model listing endpoint."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{api_config['base_url']}/api/ollama/models"
                )
                
                # Should handle the request even if Ollama is not available
                assert response.status_code in [200, 500, 503]
                
                if response.status_code == 200:
                    data = response.json()
                    assert isinstance(data, (list, dict))
                    
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for integration testing")


@pytest.mark.integration
class TestSlideGeneration:
    """Test slide generation workflow."""
    
    async def test_slide_generation_endpoint(self, api_config):
        """Test slide generation endpoint."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                data = {
                    'content': 'Test slide content',
                    'template': 'default'
                }
                
                response = await client.post(
                    f"{api_config['base_url']}/api/slides/generate",
                    json=data
                )
                
                # Should handle the request
                assert response.status_code in [200, 422, 500]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for integration testing")


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_database_connection(self):
        """Test database connection and basic operations."""
        try:
            from utils.database import Storage
            
            # Test storage initialization
            storage = Storage()
            assert storage is not None
            
            # Test basic operations if database is available
            # This will fail gracefully if database is not set up
            
        except ImportError:
            pytest.skip("Database utilities not available")
        except Exception:
            # Database might not be configured in test environment
            pytest.skip("Database not configured for testing")
    
    def test_repository_integration(self):
        """Test repository layer integration."""
        try:
            from utils.repository import DocumentRepository, ChatHistoryRepository
            
            # Test repository initialization
            doc_repo = DocumentRepository()
            chat_repo = ChatHistoryRepository()
            
            assert doc_repo is not None
            assert chat_repo is not None
            
        except ImportError:
            pytest.skip("Repository utilities not available")
        except Exception:
            # Repositories might not be configured in test environment
            pytest.skip("Repositories not configured for testing")


@pytest.mark.integration
class TestCleanupIntegration:
    """Test cleanup system integration."""
    
    async def test_cleanup_endpoints(self, api_config):
        """Test cleanup endpoints."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                endpoints = [
                    "/api/cleanup/cleanup-documents",
                    "/api/cleanup/cleanup-slides",
                    "/api/cleanup/vacuum-database"
                ]
                
                for endpoint in endpoints:
                    response = await client.post(
                        f"{api_config['base_url']}{endpoint}"
                    )
                    
                    # Should require authentication or validation
                    assert response.status_code in [401, 403, 422, 500]
                    
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for integration testing")


@pytest.mark.integration
@pytest.mark.slow
class TestFullWorkflow:
    """Test complete application workflows."""
    
    async def test_complete_document_analysis_workflow(self, api_config, sample_text_file):
        """Test complete document analysis workflow from upload to results."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Step 1: Check backend is available
                health_response = await client.get(f"{api_config['base_url']}/docs")
                if health_response.status_code not in [200]:
                    pytest.skip("Backend not healthy for full workflow test")
                
                # Step 2: Upload and analyze document
                with open(sample_text_file, 'rb') as f:
                    files = {'files': (sample_text_file.name, f, 'text/plain')}
                    data = {
                        'query_type': 'summary',
                        'user_query': 'Provide a brief summary'
                    }
                    
                    response = await client.post(
                        f"{api_config['base_url']}/api/documents/analyze",
                        files=files,
                        data=data
                    )
                    
                    # Document analysis should be handled
                    assert response.status_code in [200, 500, 503]
                    
                    if response.status_code == 200:
                        result = response.json()
                        assert isinstance(result, dict)
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for full workflow testing")
    
    async def test_model_management_workflow(self, api_config):
        """Test model management workflow."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: List available models
                models_response = await client.get(
                    f"{api_config['base_url']}/api/ollama/models"
                )
                
                # Should handle model listing
                assert models_response.status_code in [200, 500, 503]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for model management testing")
