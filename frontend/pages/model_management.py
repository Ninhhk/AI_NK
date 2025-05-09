import streamlit as st
import requests
import json
import time
import os
from io import BytesIO

# Set page config for better appearance
st.set_page_config(
    page_title="AI Model Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add custom styles for model management
st.markdown("""
    <style>
    .model-card {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    .model-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
    }
    .model-progress {
        background-color: var(--primary-color-light);
        border-radius: 5px;
        height: 12px;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    .model-progress-inner {
        background: linear-gradient(to right, var(--primary-color), var(--accent-color));
        height: 100%;
        transition: width 0.3s ease;
    }
    .model-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .model-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .model-header {
        display: flex;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoints
OLLAMA_API_URL = "http://localhost:8000/api/ollama"
SLIDES_API_URL = "http://localhost:8000/api/slides"

def get_models():
    """Fetch all available models from API"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/models")
        response.raise_for_status()
        return response.json()["models"]
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []

def get_current_model():
    """Get the currently active model for slide generation"""
    try:
        response = requests.get(f"{SLIDES_API_URL}/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        st.error(f"Error fetching current model: {e}")
        return None

def set_model(model_name):
    """Set the model for slide generation"""
    try:
        response = requests.post(
            f"{SLIDES_API_URL}/set-model",
            data={"model_name": model_name}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error setting model: {e}")
        return None

def pull_model(model_name):
    """Start pulling a model from Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/models/pull",
            data={"model_name": model_name}
        )
        response.raise_for_status()
        return model_name  # Return the model name as the task ID
    except Exception as e:
        st.error(f"Error pulling model: {e}")
        return None

def get_download_progress(task_id):
    """Get download progress for a specific task"""
    try:
        # In the simplified version, we don't track progress
        # So we'll just return a dummy object
        return {"done": True, "pull_progress": 1000, "error": None}
    except Exception as e:
        return {"done": False, "pull_progress": 0, "error": str(e)}

def get_all_progress():
    """Get all download progress"""
    try:
        # In the simplified version, we don't track progress
        return {}
    except Exception as e:
        return {}

def cancel_model_pull(task_id):
    """Cancel model pull"""
    # In the simplified version, we don't support cancellation
    return True

def delete_model(model_name):
    """Delete a model"""
    try:
        response = requests.delete(f"{OLLAMA_API_URL}/models/{model_name}")
        response.raise_for_status()
        return response.json()["success"]
    except Exception as e:
        st.error(f"Error deleting model: {e}")
        return False

def upload_model(file, model_name=None):
    """Upload a model file"""
    # In our simplified version, we don't support file uploads
    st.warning("Model file uploads are not supported in this version")
    return False

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                🤖 Model Management
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Manage Your AI Models for Slide Generation
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["Available Models", "Add New Model", "Active Downloads"])

with tab1:
    # Fetch current model
    current_model = get_current_model()
    
    # Refresh button 
    if st.button("🔄 Refresh Models", type="primary"):
        st.experimental_rerun()
    
    # Get models
    models = get_models()
    
    if not models:
        st.info("No models available. Add models in the 'Add New Model' tab.")
    else:
        st.markdown(f"### Available Models ({len(models)})")
        st.markdown("Click on a model name to set it as the current model for slide generation.")
        
        for model in models:
            with st.container():
                st.markdown(f"""
                <div class="model-card">
                    <div class="model-header">
                        <div class="model-icon">🧠</div>
                        <div>
                            <h3 style="margin: 0;">{model['name']}</h3>
                            <p style="margin: 0; color: var(--text-secondary);">
                                Size: {model['size'] / (1024*1024):.1f} MB | Modified: {model['modified_at']}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons in columns
                col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
                
                with col1:
                    if st.button(f"Select", key=f"select_{model['name']}"):
                        result = set_model(model['name'])
                        if result:
                            st.success(f"Model changed to {model['name']}")
                            time.sleep(1)
                            st.experimental_rerun()
                
                with col2:
                    if st.button(f"Info", key=f"info_{model['name']}"):
                        st.json(model['details'] if 'details' in model else model)
                
                with col3:
                    if st.button(f"Delete", key=f"delete_{model['name']}"):
                        if model['name'] == current_model:
                            st.error("Cannot delete the currently active model")
                        else:
                            if delete_model(model['name']):
                                st.success(f"Model {model['name']} deleted")
                                time.sleep(1)
                                st.experimental_rerun()
                
                with col4:
                    if model['name'] == current_model:
                        st.success("✅ Current model for slide generation")

with tab2:
    st.markdown("### Add a New Model")
    
    # Model pull section
    with st.expander("Pull Model from Ollama", expanded=True):
        st.markdown("""
        Enter the name of an Ollama model to download. Examples:
        - `llama3:8b`
        - `gemma3:1b`
        - `mistral:latest`
        """)
        
        with st.form("pull_model_form"):
            model_name = st.text_input("Model Name", placeholder="e.g., llama3:8b")
            submitted = st.form_submit_button("Start Download")
            
            if submitted and model_name:
                task_id = pull_model(model_name)
                if task_id:
                    st.success(f"Started downloading {model_name}")
                    time.sleep(1)
                    st.experimental_rerun()
    
    # Model upload section
    with st.expander("Upload GGUF Model File", expanded=False):
        st.markdown("""
        Upload a GGUF model file directly. This will be added to Ollama.
        """)
        
        with st.form("upload_model_form"):
            uploaded_file = st.file_uploader("Select GGUF file", type=["gguf"])
            custom_name = st.text_input("Custom Model Name (optional)")
            upload_submitted = st.form_submit_button("Upload Model")
            
            if upload_submitted and uploaded_file:
                success = upload_model(uploaded_file, custom_name if custom_name else None)
                if success:
                    st.success(f"Model uploaded successfully")
                    time.sleep(1)
                    st.experimental_rerun()

with tab3:
    st.markdown("### Active Downloads")
    
    # Auto-refresh for download progress
    auto_refresh = st.checkbox("Auto-refresh (every 2 seconds)", value=True)
    
    # Get all download progress
    download_progress = get_all_progress()
    
    if not download_progress:
        st.info("No active downloads. Start a download in the 'Add New Model' tab.")
    else:
        for model_name, progress in download_progress.items():
            with st.container():
                # Calculate percentage for display
                percentage = progress.get("pull_progress", 0) / 10 if progress.get("pull_progress") is not None else 0
                
                st.markdown(f"""
                <div class="model-card">
                    <h3>{model_name}</h3>
                    <p>Status: {"Completed" if progress.get("done", False) else "Downloading..."}</p>
                    <div class="model-progress">
                        <div class="model-progress-inner" style="width: {percentage}%;"></div>
                    </div>
                    <p>{percentage:.1f}% complete</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Cancel button
                if not progress.get("done", False):
                    if st.button(f"Cancel", key=f"cancel_{model_name}"):
                        if cancel_model_pull(model_name):
                            st.success(f"Cancelled download of {model_name}")
                            time.sleep(1)
                            st.experimental_rerun()
    
    # Auto-refresh logic
    if auto_refresh and download_progress:
        time.sleep(2)
        st.experimental_rerun()

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by Ollama | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)
