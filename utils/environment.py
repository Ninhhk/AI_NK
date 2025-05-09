"""
Environment Validation Utilities

This module contains functions to validate the runtime environment,
ensuring all required dependencies and services are available.
"""

import sys
import platform
import importlib
import subprocess
from typing import List, Dict, Tuple, Any, Optional
import pkg_resources
import requests
from pathlib import Path
import os


def get_python_version() -> Tuple[int, int, int]:
    """Get the current Python version as a tuple of (major, minor, patch)."""
    return (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)


def check_python_version(min_version: Tuple[int, int, int] = (3, 12, 0)) -> bool:
    """Check if the current Python version meets the minimum requirements."""
    current = get_python_version()
    
    if current[0] < min_version[0]:  # Major version is lower
        return False
    elif current[0] == min_version[0] and current[1] < min_version[1]:  # Same major, lower minor
        return False
    elif current[0] == min_version[0] and current[1] == min_version[1] and current[2] < min_version[2]:  # Same major & minor, lower patch
        return False
    
    return True


def is_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed."""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def check_required_packages(required_packages: List[str]) -> Dict[str, bool]:
    """Check if all required packages are installed and return their status."""
    package_status = {}
    
    for package in required_packages:
        package_status[package] = is_package_installed(package)
    
    return package_status


def check_ollama_service(base_url: str = "http://localhost:11434") -> Dict[str, Any]:
    """
    Check if Ollama service is running and configured correctly.
    
    Returns:
        Dict with keys:
        - running: bool, True if service is responding
        - models: List of available models or None if service not running
        - error: Error message if any
    """
    result = {
        "running": False,
        "models": None,
        "error": None
    }
    
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            result["running"] = True
            models_data = response.json()
            # Extract model names
            result["models"] = [model.get("name") for model in models_data.get("models", [])]
        else:
            result["error"] = f"Ollama returned status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
    
    return result


def check_env_file_exists() -> bool:
    """Check if .env file exists in the project root."""
    project_root = Path(__file__).parent.parent.absolute()
    env_path = project_root / ".env"
    return env_path.exists()


def validate_environment(
    min_python_version: Tuple[int, int, int] = (3, 12, 0),
    required_packages: List[str] = None,
    check_ollama: bool = True,
    required_models: List[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Perform a complete environment validation.
    
    Args:
        min_python_version: Minimum required Python version
        required_packages: List of required Python packages
        check_ollama: Whether to check Ollama service
        required_models: List of required Ollama models (if check_ollama is True)
        verbose: Whether to print validation results
    
    Returns:
        Dictionary with validation results
    """
    if required_packages is None:
        required_packages = [
            "fastapi", "uvicorn", "python-multipart", "langchain", 
            "langchain-community", "streamlit", "python-dotenv",
            "langdetect", "sentence-transformers", "faiss-cpu"
        ]
    
    if required_models is None and check_ollama:
        required_models = ["gemma3:1b"]
    
    # Initialize result dictionary
    result = {
        "python_version": {
            "current": get_python_version(),
            "required": min_python_version,
            "valid": check_python_version(min_python_version)
        },
        "packages": check_required_packages(required_packages),
        "env_file": check_env_file_exists(),
        "ollama": None,
        "overall_valid": True
    }
    
    # Check Ollama if requested
    if check_ollama:
        ollama_result = check_ollama_service()
        result["ollama"] = ollama_result
        
        # Check required models
        if ollama_result["running"] and required_models:
            ollama_result["missing_models"] = [
                model for model in required_models 
                if model not in ollama_result["models"]
            ]
    
    # Determine overall validity
    if not result["python_version"]["valid"]:
        result["overall_valid"] = False
    
    missing_packages = [pkg for pkg, installed in result["packages"].items() if not installed]
    if missing_packages:
        result["overall_valid"] = False
    
    if check_ollama and (not result["ollama"]["running"] or 
                        (result["ollama"].get("missing_models") and 
                         len(result["ollama"]["missing_models"]) > 0)):
        result["overall_valid"] = False
    
    # Print results if verbose
    if verbose:
        print("\n" + "="*60)
        print("ENVIRONMENT VALIDATION RESULTS")
        print("="*60)
        
        # Python version
        py_current = ".".join(map(str, result["python_version"]["current"]))
        py_required = ".".join(map(str, result["python_version"]["required"]))
        py_valid = result["python_version"]["valid"]
        py_status = "✅" if py_valid else "❌"
        
        print(f"\nPython Version: {py_status}")
        print(f"  Current: {py_current}")
        print(f"  Required: {py_required}")
        
        # Packages
        print("\nRequired Packages:")
        all_packages_installed = True
        for pkg, installed in result["packages"].items():
            pkg_status = "✅" if installed else "❌"
            if not installed:
                all_packages_installed = False
            print(f"  {pkg_status} {pkg}")
        
        # Environment file
        env_status = "✅" if result["env_file"] else "❌"
        print(f"\nEnvironment File (.env): {env_status}")
        
        # Ollama
        if check_ollama:
            if result["ollama"]["running"]:
                print("\nOllama Service: ✅")
                
                # Check models
                if "missing_models" in result["ollama"] and result["ollama"]["missing_models"]:
                    print("  Required Models:")
                    for model in required_models:
                        model_installed = model not in result["ollama"]["missing_models"]
                        model_status = "✅" if model_installed else "❌"
                        print(f"    {model_status} {model}")
                    
                    # Print instructions for missing models
                    if result["ollama"]["missing_models"]:
                        print("\n  To install missing models, run:")
                        for model in result["ollama"]["missing_models"]:
                            print(f"    ollama pull {model}")
            else:
                print("\nOllama Service: ❌")
                print(f"  Error: {result['ollama']['error']}")
                print("  Make sure Ollama is installed and running:")
                print("    https://ollama.ai/download")
                print("    Run: ollama serve")
        
        # Overall result
        print("\n" + "-"*60)
        overall_status = "✅ PASSED" if result["overall_valid"] else "❌ FAILED"
        print(f"Overall Environment Validation: {overall_status}")
        print("="*60 + "\n")
    
    return result


if __name__ == "__main__":
    """Run environment validation when script is executed directly."""
    validation_result = validate_environment()
    
    sys.exit(0 if validation_result["overall_valid"] else 1) 