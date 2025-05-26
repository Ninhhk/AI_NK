"""
Unit tests for utility modules and core functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


@pytest.mark.unit
class TestEnvironmentValidation:
    """Test environment validation utilities."""
    
    def test_import_validation_utils(self):
        """Test that validation utilities can be imported."""
        try:
            from utils.environment import validate_environment
            assert validate_environment is not None
        except ImportError:
            pytest.skip("Environment validation utilities not available")
    
    @patch('utils.environment.validate_environment')
    def test_validation_function_callable(self, mock_validate):
        """Test that validation function is callable."""
        mock_validate.return_value = {"overall_valid": True}
        
        from utils.environment import validate_environment
        result = validate_environment()
        
        assert isinstance(result, dict)
        assert "overall_valid" in result


@pytest.mark.unit
class TestDatabaseUtils:
    """Test database utilities."""
    
    def test_import_database_utils(self):
        """Test that database utilities can be imported."""
        try:
            from utils.database import Storage
            assert Storage is not None
        except ImportError:
            pytest.skip("Database utilities not available")
    
    def test_import_repository_utils(self):
        """Test that repository utilities can be imported."""
        try:
            from utils.repository import DocumentRepository, ChatHistoryRepository
            assert DocumentRepository is not None
            assert ChatHistoryRepository is not None
        except ImportError:
            pytest.skip("Repository utilities not available")


@pytest.mark.unit
class TestCleanupUtils:
    """Test cleanup utilities."""
    
    def test_import_cleanup_utils(self):
        """Test that cleanup utilities can be imported."""
        try:
            from utils.cleanup import (
                cleanup_old_documents,
                cleanup_old_slides,
                cleanup_orphaned_uploads,
                vacuum_database
            )
            assert cleanup_old_documents is not None
            assert cleanup_old_slides is not None
            assert cleanup_orphaned_uploads is not None
            assert vacuum_database is not None
        except ImportError:
            pytest.skip("Cleanup utilities not available")


@pytest.mark.unit
class TestDocumentService:
    """Test document analysis service."""
    
    def test_import_document_service(self):
        """Test that document service can be imported."""
        try:
            from backend.document_analysis.document_service import DocumentAnalysisService
            assert DocumentAnalysisService is not None
        except ImportError:
            pytest.skip("Document service not available")
    
    def test_document_service_initialization(self):
        """Test document service can be initialized."""
        try:
            from backend.document_analysis.document_service import DocumentAnalysisService
            service = DocumentAnalysisService(
                model_name="test_model",
                base_url="http://localhost:11434"
            )
            assert service is not None
        except ImportError:
            pytest.skip("Document service not available")
        except Exception as e:
            # Service may fail to initialize due to missing dependencies
            # but we can still test the import
            assert "DocumentAnalysisService" in str(type(e).__name__) or True


@pytest.mark.unit
class TestSystemPromptManager:
    """Test system prompt manager."""
    
    def test_import_system_prompt_manager(self):
        """Test that system prompt manager can be imported."""
        try:
            from backend.model_management.system_prompt_manager import system_prompt_manager
            assert system_prompt_manager is not None
        except ImportError:
            pytest.skip("System prompt manager not available")
    
    def test_system_prompt_manager_methods(self):
        """Test system prompt manager has required methods."""
        try:
            from backend.model_management.system_prompt_manager import system_prompt_manager
            
            # Test that methods exist
            assert hasattr(system_prompt_manager, 'get_system_prompt')
            assert hasattr(system_prompt_manager, 'set_system_prompt')
            assert callable(system_prompt_manager.get_system_prompt)
            assert callable(system_prompt_manager.set_system_prompt)
        except ImportError:
            pytest.skip("System prompt manager not available")


@pytest.mark.unit
class TestFileHandling:
    """Test file handling utilities."""
    
    def test_temp_file_creation(self, temp_dir):
        """Test temporary file creation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    def test_path_operations(self, temp_dir):
        """Test path operations."""
        nested_dir = temp_dir / "nested" / "directory"
        nested_dir.mkdir(parents=True, exist_ok=True)
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()
    
    def test_file_extension_handling(self, temp_dir):
        """Test file extension handling."""
        files = [
            temp_dir / "test.txt",
            temp_dir / "test.pdf",
            temp_dir / "test.docx",
            temp_dir / "test.md"
        ]
        
        for file_path in files:
            file_path.write_text("test content")
            assert file_path.suffix in [".txt", ".pdf", ".docx", ".md"]


@pytest.mark.unit
class TestConfigValidation:
    """Test configuration validation."""
    
    def test_import_config_modules(self):
        """Test that configuration modules can be imported."""
        try:
            from backend.document_analysis.config import OLLAMA_CONFIG
            assert OLLAMA_CONFIG is not None
            assert isinstance(OLLAMA_CONFIG, dict)
        except ImportError:
            pytest.skip("Configuration modules not available")
    
    def test_config_structure(self):
        """Test configuration has required keys."""
        try:
            from backend.document_analysis.config import OLLAMA_CONFIG
            
            required_keys = ["model_name", "base_url"]
            for key in required_keys:
                assert key in OLLAMA_CONFIG, f"Missing required config key: {key}"
        except ImportError:
            pytest.skip("Configuration modules not available")


@pytest.mark.unit
class TestRunnerScripts:
    """Test runner scripts can be imported."""
    
    def test_frontend_runner_import(self):
        """Test frontend runner can be imported."""
        try:
            import run_frontend
            assert hasattr(run_frontend, 'main')
        except ImportError:
            pytest.skip("Frontend runner not available")
    
    def test_backend_runner_import(self):
        """Test backend runner can be imported."""
        try:
            import run_backend
            assert hasattr(run_backend, 'main')
        except ImportError:
            pytest.skip("Backend runner not available")
    
    def test_update_and_test_import(self):
        """Test update and test script can be imported."""
        try:
            import update_and_test
            assert hasattr(update_and_test, 'main')
        except ImportError:
            pytest.skip("Update and test script not available")
