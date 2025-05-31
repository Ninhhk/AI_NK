#!/usr/bin/env python3
"""
Copy .env.example to .env

This script copies the content from .env.example to .env file.
Useful for setting up the environment configuration.
"""

import os
import shutil
from pathlib import Path


def copy_env_example():
    """Copy .env.example to .env file."""
    
    # Get the current directory (where the script is located)
    script_dir = Path(__file__).parent
    
    # Define file paths
    env_example_path = script_dir / ".env.example"
    env_path = script_dir / ".env"
    
    try:
        # Check if .env.example exists
        if not env_example_path.exists():
            print("❌ Error: .env.example file not found!")
            print(f"   Expected location: {env_example_path}")
            return False
        
        # Check if .env already exists
        if env_path.exists():
            print("⚠️  Warning: .env file already exists!")
            response = input("   Do you want to overwrite it? (y/N): ").strip().lower()
            if response not in ('y', 'yes'):
                print("   Operation cancelled.")
                return False
        
        # Copy the file
        shutil.copy2(env_example_path, env_path)
        
        # Verify the copy
        if env_path.exists():
            print("✅ Successfully copied .env.example to .env")
            
            # Show the content
            print("\n📄 Content of .env file:")
            print("-" * 40)
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
            print("-" * 40)
            
            return True
        else:
            print("❌ Error: Failed to create .env file")
            return False
            
    except PermissionError:
        print("❌ Error: Permission denied!")
        print("   Try running the script as administrator.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Main function."""
    print("🔧 AI NVCB Environment Setup")
    print("=" * 40)
    print("Copying .env.example to .env...")
    print()
    
    success = copy_env_example()
    
    if success:
        print("\n🎉 Environment setup completed!")
        print("💡 You can now run the application with:")
        print("   python run_backend.py")
        print("   python run_frontend.py")
    else:
        print("\n💥 Environment setup failed!")
        print("📋 Manual steps:")
        print("   1. Make sure .env.example exists")
        print("   2. Copy its content to .env manually")
        print("   3. Or run this script as administrator")


if __name__ == "__main__":
    main()
