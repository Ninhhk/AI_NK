"""
Unit tests for the FastAPI backend application.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.unit
class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_health_check_exists(self, client):
        """Test that health check endpoint exists."""
        # Since we don't have a health endpoint, test the root
        response = client.get("/")
        # Should return 404 or redirect, not 500
        assert response.status_code in [200, 404, 307]
    
    def test_api_docs_accessible(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


@pytest.mark.unit
class TestDocumentAPI:
    """Test document analysis API endpoints."""
    
    def test_document_analyze_endpoint_exists(self, client):
        """Test that document analyze endpoint exists."""
        response = client.post("/api/documents/analyze")
        # Should return 422 (validation error) not 404
        assert response.status_code in [422, 400]
    
    def test_document_analyze_missing_data(self, client):
        """Test document analyze with missing required data."""
        response = client.post("/api/documents/analyze", json={})
        assert response.status_code == 422
    
    def test_document_analyze_invalid_query_type(self, client):
        """Test document analyze with invalid query type."""
        data = {
            "query_type": "invalid_type",
            "user_query": "test query"
        }
        response = client.post("/api/documents/analyze", data=data)
        assert response.status_code in [422, 400]


@pytest.mark.unit
class TestSlideAPI:
    """Test slide generation API endpoints."""
    
    def test_slide_generate_endpoint_exists(self, client):
        """Test that slide generation endpoint exists."""
        response = client.post("/api/slides/generate")
        # Should return 422 (validation error) not 404
        assert response.status_code in [422, 400]
    
    def test_slide_download_endpoint_exists(self, client):
        """Test that slide download endpoint exists."""
        response = client.get("/api/slides/download/nonexistent")
        # Should return 404 or 422, not 500
        assert response.status_code in [404, 422]


@pytest.mark.unit
class TestModelAPI:
    """Test Ollama model management API endpoints."""
    
    def test_models_list_endpoint_exists(self, client):
        """Test that models list endpoint exists."""
        response = client.get("/api/ollama/models")
        # Should return 200 or connection error, not 404
        assert response.status_code in [200, 500, 503]
    
    def test_model_pull_endpoint_exists(self, client):
        """Test that model pull endpoint exists."""
        response = client.post("/api/ollama/pull")
        # Should return 422 (validation error) not 404
        assert response.status_code in [422, 400]
    
    def test_model_delete_endpoint_exists(self, client):
        """Test that model delete endpoint exists."""
        response = client.delete("/api/ollama/delete")
        # Should return 422 (validation error) not 404
        assert response.status_code in [422, 400]


@pytest.mark.unit
class TestCleanupAPI:
    """Test cleanup API endpoints."""
    
    def test_cleanup_documents_endpoint_exists(self, client):
        """Test that cleanup documents endpoint exists."""
        response = client.post("/api/cleanup/cleanup-documents")
        # Should return 422 or 401 (auth required), not 404
        assert response.status_code in [422, 401, 403]
    
    def test_cleanup_slides_endpoint_exists(self, client):
        """Test that cleanup slides endpoint exists."""
        response = client.post("/api/cleanup/cleanup-slides")
        # Should return 422 or 401 (auth required), not 404
        assert response.status_code in [422, 401, 403]
    
    def test_vacuum_database_endpoint_exists(self, client):
        """Test that vacuum database endpoint exists."""
        response = client.post("/api/cleanup/vacuum-database")
        # Should return 422 or 401 (auth required), not 404
        assert response.status_code in [422, 401, 403]


@pytest.mark.unit
class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/documents/analyze")
        # Check for CORS headers
        assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
    
    def test_preflight_request(self, client):
        """Test preflight request handling."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = client.options("/api/documents/analyze", headers=headers)
        assert response.status_code in [200, 204]


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling."""
    
    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_405_handling(self, client):
        """Test 405 error handling."""
        response = client.put("/api/documents/analyze")
        assert response.status_code == 405
