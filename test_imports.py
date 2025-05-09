import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Try to import the model manager
try:
    from backend.model_management.model_manager import model_manager
    print("✅ Successfully imported model_manager")
except ImportError as e:
    print(f"❌ Failed to import model_manager: {e}")

# Try to import the ModelInfo class
try:
    from backend.model_management.config import ModelInfo
    print("✅ Successfully imported ModelInfo")
except ImportError as e:
    print(f"❌ Failed to import ModelInfo: {e}")

print("\nPython path:")
for path in sys.path:
    print(f"- {path}")
