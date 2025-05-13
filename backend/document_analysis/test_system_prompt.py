import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.document_analysis.document_service import DocumentAnalysisService
from backend.model_management.system_prompt_manager import system_prompt_manager
import tempfile

def test_vietnamese_system_prompt():
    """Test the Vietnamese system prompt."""
    # Set the system prompt to Vietnamese
    vietnamese_prompt = "must answer in vietnamese, phải trả lời bằng tiếng việt"
    system_prompt_manager.set_system_prompt(vietnamese_prompt)
    
    # Verify it was set correctly
    current_prompt = system_prompt_manager.get_system_prompt()
    print(f"Current system prompt: '{current_prompt}'")
    print(f"Matches Vietnamese prompt: {current_prompt == vietnamese_prompt}")

def test_document_service_with_prompt():
    """Test the document service with a custom system prompt."""
    # Create a sample document service
    document_service = DocumentAnalysisService()
    
    # Test data
    test_prompt = "Generate very difficult questions focusing on deep technical concepts."
    
    # Create a temporary PDF file for testing
    try:
        with open("test_document.pdf", "rb") as f:
            test_content = f.read()
            
        # Test the quiz generation with system prompt
        result = document_service.generate_quiz(
            file_content=test_content,
            num_questions=3,
            difficulty="hard",
            system_prompt=test_prompt
        )
        
        print("\nTest result:")
        print(result["result"])
        print("\nSystem prompt was used:", test_prompt in document_service.llm._invocation_params.get("system", ""))
    except Exception as e:
        print(f"Error in test: {str(e)}")

if __name__ == "__main__":
    # Test the Vietnamese system prompt
    test_vietnamese_system_prompt()
    
    # Optionally test the document service with a custom prompt
    # Uncomment to run this test
    # test_document_service_with_prompt()
