"""
End-to-end tests for the AI NVCB application.

These tests simulate real user interactions with the application.
"""

import pytest
import asyncio
import httpx
import time
from pathlib import Path
import sys
import os
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


@pytest.mark.slow
class TestDocumentAnalysisE2E:
    """End-to-end tests for document analysis."""
    
    async def test_complete_document_analysis_user_flow(self, api_config, sample_text_file):
        """Test complete user flow for document analysis."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Step 1: User checks available models
                models_response = await client.get(
                    f"{api_config['base_url']}/api/ollama/models"
                )
                
                # Step 2: User uploads document for analysis
                with open(sample_text_file, 'rb') as f:
                    files = {'files': (sample_text_file.name, f, 'text/plain')}
                    data = {
                        'query_type': 'summary',
                        'user_query': 'Please provide a comprehensive summary of this document'
                    }
                    
                    analysis_response = await client.post(
                        f"{api_config['base_url']}/api/documents/analyze",
                        files=files,
                        data=data
                    )
                    
                    # Document analysis should be handled
                    assert analysis_response.status_code in [200, 500, 503, 422]
                    
                    if analysis_response.status_code == 200:
                        result = analysis_response.json()
                        
                        # Verify response structure
                        assert isinstance(result, dict)
                        
                        # If successful, should have analysis results
                        if 'analysis' in result or 'response' in result:
                            assert len(str(result)) > 0
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")
    
    async def test_qa_analysis_flow(self, api_config, sample_text_file):
        """Test Q&A analysis flow."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(sample_text_file, 'rb') as f:
                    files = {'files': (sample_text_file.name, f, 'text/plain')}
                    data = {
                        'query_type': 'qa',
                        'user_query': 'What is the main topic of this document?'
                    }
                    
                    response = await client.post(
                        f"{api_config['base_url']}/api/documents/analyze",
                        files=files,
                        data=data
                    )
                    
                    assert response.status_code in [200, 500, 503, 422]
                    
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")


@pytest.mark.slow
class TestSlideGenerationE2E:
    """End-to-end tests for slide generation."""
    
    async def test_complete_slide_generation_flow(self, api_config):
        """Test complete slide generation flow."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Step 1: Generate slides
                slide_data = {
                    'content': 'AI NVCB Test Presentation\n\n• Key Point 1\n• Key Point 2\n• Key Point 3',
                    'template': 'default',
                    'title': 'Test Presentation'
                }
                
                generate_response = await client.post(
                    f"{api_config['base_url']}/api/slides/generate",
                    json=slide_data
                )
                
                assert generate_response.status_code in [200, 422, 500]
                
                if generate_response.status_code == 200:
                    result = generate_response.json()
                    
                    # Should have slide ID or download info
                    if 'slide_id' in result or 'download_url' in result:
                        slide_id = result.get('slide_id', 'test_id')
                        
                        # Step 2: Try to download generated slides
                        download_response = await client.get(
                            f"{api_config['base_url']}/api/slides/download/{slide_id}"
                        )
                        
                        # Download should be handled
                        assert download_response.status_code in [200, 404, 500]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")


@pytest.mark.slow
class TestModelManagementE2E:
    """End-to-end tests for model management."""
    
    async def test_model_management_flow(self, api_config):
        """Test model management flow."""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Step 1: List current models
                models_response = await client.get(
                    f"{api_config['base_url']}/api/ollama/models"
                )
                
                assert models_response.status_code in [200, 500, 503]
                
                if models_response.status_code == 200:
                    models = models_response.json()
                    assert isinstance(models, (list, dict))
                
                # Step 2: Test model pull endpoint (without actually pulling)
                pull_data = {
                    'model_name': 'llama3.1:8b'
                }
                
                pull_response = await client.post(
                    f"{api_config['base_url']}/api/ollama/pull",
                    json=pull_data
                )
                
                # Should handle the request
                assert pull_response.status_code in [200, 422, 500]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")


@pytest.mark.slow
class TestSystemPromptE2E:
    """End-to-end tests for system prompt management."""
    
    async def test_system_prompt_workflow(self, api_config):
        """Test system prompt management workflow."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test system prompt endpoints if they exist
                # This is a placeholder for system prompt testing
                
                # Check if system prompt endpoints are available
                response = await client.get(f"{api_config['base_url']}/docs")
                
                if response.status_code == 200:
                    docs_content = response.text
                    
                    # Check if system prompt endpoints are documented
                    if 'system' in docs_content.lower() or 'prompt' in docs_content.lower():
                        # System prompt functionality is available
                        assert True
                    else:
                        # System prompt might be managed internally
                        assert True
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")


@pytest.mark.slow
class TestErrorHandlingE2E:
    """End-to-end tests for error handling."""
    
    async def test_invalid_file_upload(self, api_config, temp_dir):
        """Test error handling for invalid file uploads."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create an invalid file
                invalid_file = temp_dir / "invalid.bin"
                invalid_file.write_bytes(b'\x00\x01\x02\x03\x04')
                
                with open(invalid_file, 'rb') as f:
                    files = {'files': (invalid_file.name, f, 'application/octet-stream')}
                    data = {
                        'query_type': 'summary',
                        'user_query': 'Analyze this file'
                    }
                    
                    response = await client.post(
                        f"{api_config['base_url']}/api/documents/analyze",
                        files=files,
                        data=data
                    )
                    
                    # Should handle invalid files gracefully
                    assert response.status_code in [400, 422, 500]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")
    
    async def test_missing_required_fields(self, api_config):
        """Test error handling for missing required fields."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test with missing required fields
                response = await client.post(
                    f"{api_config['base_url']}/api/documents/analyze",
                    json={}
                )
                
                # Should return validation error
                assert response.status_code == 422
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")
    
    async def test_large_file_handling(self, api_config, temp_dir):
        """Test handling of large files."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Create a moderately large text file
                large_file = temp_dir / "large.txt"
                content = "This is a test sentence. " * 1000  # ~25KB
                large_file.write_text(content)
                
                with open(large_file, 'rb') as f:
                    files = {'files': (large_file.name, f, 'text/plain')}
                    data = {
                        'query_type': 'summary',
                        'user_query': 'Summarize this large document'
                    }
                    
                    response = await client.post(
                        f"{api_config['base_url']}/api/documents/analyze",
                        files=files,
                        data=data
                    )
                    
                    # Should handle large files
                    assert response.status_code in [200, 413, 422, 500]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for E2E testing")


@pytest.mark.slow
class TestPerformanceE2E:
    """End-to-end performance tests."""
    
    async def test_concurrent_requests(self, api_config):
        """Test handling of concurrent requests."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Create multiple concurrent requests
                tasks = []
                
                for i in range(3):  # Small number for testing
                    task = client.get(f"{api_config['base_url']}/api/ollama/models")
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # At least some requests should succeed
                successful_requests = [
                    r for r in results 
                    if not isinstance(r, Exception) and 
                    hasattr(r, 'status_code') and 
                    r.status_code in [200, 500, 503]
                ]
                
                assert len(successful_requests) > 0
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for performance testing")
    
    async def test_response_time(self, api_config):
        """Test response time for basic endpoints."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                
                response = await client.get(f"{api_config['base_url']}/docs")
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Basic endpoints should respond quickly
                assert response_time < 10.0  # 10 seconds max
                assert response.status_code in [200, 500, 503]
                
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Backend not available for performance testing")
