#!/usr/bin/env python3
"""
Simple Ollama Model Cleanup Script

This script cleans up Ollama models, keeping only qwen3:8b.
Equivalent to the PowerShell script but in Python.

Usage:
    python simple_cleanup.py           # Interactive mode
    python simple_cleanup.py --force   # Skip confirmations
"""

import requests
import json
import sys


def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_models():
    """Get all installed models."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])
    except Exception as e:
        print(f"Error getting models: {e}")
        return []


def get_running_models():
    """Get running models."""
    try:
        response = requests.get("http://localhost:11434/api/ps")
        response.raise_for_status()
        return response.json().get("models", [])
    except Exception as e:
        print(f"Error getting running models: {e}")
        return []


def delete_model(model_name):
    """Delete a model."""
    try:
        response = requests.delete(
            "http://localhost:11434/api/delete",
            json={"name": model_name}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error deleting {model_name}: {e}")
        return False


def pull_model(model_name):
    """Download a model."""
    try:
        print(f"Downloading {model_name}...")
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name},
            stream=True
        )
        response.raise_for_status()
        
        # Simple progress indication
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if "status" in data:
                        print(f"\r{data['status']}", end="", flush=True)
                    if data.get("status") == "success":
                        print("\nDownload completed!")
                        break
                except:
                    continue
        
        return True
    except Exception as e:
        print(f"Error downloading {model_name}: {e}")
        return False


def format_size(bytes_size):
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def main():
    """Main function."""
    force = "--force" in sys.argv
    target_model = "qwen3:8b"
    
    print("=" * 50)
    print("🧹 Ollama Model Cleanup")
    print("=" * 50)
    
    # Check Ollama service
    if not check_ollama():
        print("❌ Ollama is not running!")
        print("Please start Ollama with: ollama serve")
        sys.exit(1)
    
    print("✅ Ollama is running")
    
    # Get running models
    running = get_running_models()
    if running:
        print(f"\n🔄 Running models: {len(running)}")
        for model in running:
            print(f"   • {model.get('name', 'Unknown')}")
    
    # Get all models
    models = get_models()
    if not models:
        print("\n📭 No models installed")
        if not force:
            install = input(f"Install {target_model}? [y/N]: ").lower()
            if install == 'y':
                pull_model(target_model)
        return
    
    print(f"\n📦 Installed models: {len(models)}")
    target_exists = False
    to_delete = []
    
    for model in models:
        name = model.get("name")
        size = format_size(model.get("size", 0))
        print(f"   • {name} ({size})")
        
        if name == target_model:
            target_exists = True
        else:
            to_delete.append(name)
    
    # Plan actions
    print(f"\n📋 Plan:")
    if target_exists:
        print(f"✅ Keep: {target_model}")
    else:
        print(f"📥 Will install: {target_model}")
    
    if to_delete:
        print(f"🗑️  Will delete: {len(to_delete)} models")
        for name in to_delete:
            print(f"   • {name}")
    else:
        print("✅ No models to delete")
    
    # Confirm
    if not force and (to_delete or not target_exists):
        confirm = input("\n🚀 Proceed? [y/N]: ").lower()
        if confirm != 'y':
            print("❌ Cancelled")
            return
    
    # Execute cleanup
    print(f"\n🗑️  Deleting models...")
    deleted = 0
    for name in to_delete:
        print(f"   Deleting {name}...", end=" ")
        if delete_model(name):
            print("✅")
            deleted += 1
        else:
            print("❌")
    
    if to_delete:
        print(f"📊 Deleted {deleted}/{len(to_delete)} models")
    
    # Install target if needed
    if not target_exists:
        print(f"\n📥 Installing {target_model}...")
        if pull_model(target_model):
            print(f"✅ {target_model} installed")
        else:
            print(f"❌ Failed to install {target_model}")
    
    print(f"\n🎉 Cleanup complete!")
    
    # Final status
    final_models = get_models()
    print(f"📦 Final count: {len(final_models)} models")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
