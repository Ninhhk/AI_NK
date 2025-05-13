import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from frontend.components.system_prompt import system_prompt_ui

# Set page config for better appearance
st.set_page_config(
    page_title="AI Slide Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add custom styles for status and download button
st.markdown("""
    <style>
    .stStatus {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stStatus > div {
        color: var(--text-primary);
    }
    .stStatus[data-state="complete"] {
        background: linear-gradient(135deg, var(--success-color) 0%, #27ae60 100%);
    }
    .stStatus[data-state="error"] {
        background: linear-gradient(135deg, var(--error-color) 0%, #c0392b 100%);
    }
    .stDownloadButton {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stDownloadButton:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    .stDownloadButton > button {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

def generate_slides(topic: str, num_slides: int, model_name: str = None, document_files=None, system_prompt: str = None) -> dict:
    """Send content to backend for slide generation with multiple documents."""
    # Prepare files list for multi-file upload under 'documents'
    files = []
    if document_files:
        for f in document_files:
            files.append((
                "documents",
                (f.name, f.getvalue(), f.type)
            ))
    data = {
        "topic": topic, 
        "num_slides": num_slides
    }
    
    # Add model_name if specified
    if model_name:
        data["model_name"] = model_name
        
    # Add system_prompt if specified
    if system_prompt:
        data["system_prompt"] = system_prompt
        
    response = requests.post(
        "http://localhost:8000/api/slides/generate",
        files=files or None,
        data=data
    )
    response.raise_for_status()
    return response.json()

def get_available_models() -> list:
    """Get list of available models from backend."""
    try:
        response = requests.get("http://localhost:8000/api/ollama/models")
        response.raise_for_status()
        return response.json().get("models", [])
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []
    
def get_current_model() -> str:
    """Get current model being used for slide generation."""
    try:
        response = requests.get("http://localhost:8000/api/slides/current-model")
        response.raise_for_status()
        return response.json().get("model_name", "")
    except Exception as e:
        print(f"Error fetching current model: {e}")
        return ""

def get_system_prompt() -> str:
    """Get current system prompt for slide generation."""
    try:
        response = requests.get("http://localhost:8000/api/slides/system-prompt")
        response.raise_for_status()
        return response.json().get("system_prompt", "")
    except Exception as e:
        print(f"Error fetching system prompt: {e}")
        return ""

def set_system_prompt(prompt: str) -> bool:
    """Set system prompt for slide generation."""
    try:
        response = requests.post(
            "http://localhost:8000/api/slides/system-prompt",
            data={"system_prompt": prompt}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error setting system prompt: {e}")
        return False

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                🎯 Create Slides
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Create Professional Presentations With AI
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Get available models for dropdown
available_models = get_available_models()
current_model = get_current_model()

# Model selection
with st.expander("🤖 AI Model Selection", expanded=False):
    st.markdown("""
        Select which AI model to use for all application features including slide generation, document analysis, and quiz generation.
        Any changes made here will apply to the entire application.
        You can manage models in the Model Management page.
    """)
    
    # Create a list of model names for the dropdown
    model_names = [model.get('name') for model in available_models]
    
    # Only show dropdown if there are models available
    if model_names:
        selected_model = st.selectbox(
            "Select Global AI Model",
            options=model_names,
            index=model_names.index(current_model) if current_model in model_names else 0,
            help="Choose which AI model to use for all features (will be applied globally)"
        )
        st.info(f"Using model: {selected_model} for all features including document analysis and quiz generation")
    else:
        st.warning("No models available. Please visit the Model Management page to add models.")
        selected_model = None

# Input section with better layout
col1, col2 = st.columns([2,1])

with col1:
    topic = st.text_input(
        "📝 Your Topic",
        placeholder="Enter the topic you want to create slides for...",
        help="Enter a clear topic for the AI to generate appropriate slides"
    )

with col2:
    num_slides = st.number_input(
        "📊 Number of Slides",
        min_value=1,
        max_value=20,
        value=5,
        help="Choose the number of slides you want to create (maximum 20 slides)"
    )

# System prompt section
with st.expander("💬 System Prompt Settings", expanded=False):
    # Get current system prompt
    current_system_prompt = get_system_prompt()
    
    # Add tabs for different sections
    prompt_tab, examples_tab, help_tab = st.tabs(["Edit Prompt", "Example Prompts", "Help"])
    with prompt_tab:
        # Use the reusable system prompt UI component
        custom_system_prompt = system_prompt_ui(default_prompt=current_system_prompt, key_prefix="slide_gen")
        
        # Save button for system prompt
        if st.button("💾 Save System Prompt"):
            if set_system_prompt(custom_system_prompt):
                st.success("✅ System prompt saved successfully!")
            else:
                st.error("❌ Failed to save system prompt. Please try again.")
                  # Use in current session only
        if 'use_custom_prompt' not in st.session_state:
            st.session_state['use_custom_prompt'] = False
            
        st.session_state['use_custom_prompt'] = st.checkbox(
            "Use custom prompt for this session only (without saving)",
            value=st.session_state['use_custom_prompt'],
            key="slide_gen_use_custom_prompt",
            help="Apply a custom prompt for just this session without saving it as the default"
        )
    
    with examples_tab:
        st.markdown("### Example System Prompts")
        st.markdown("Click on any example to use it:")
        
        # Technical presentation example
        if st.button("Technical Presentation"):
            example_prompt = """You are a technical presentation expert. Create slides with precise, technically accurate content. 
Use formal language, include relevant technical terminology, and organize complex information 
hierarchically. Each slide should focus on a single technical concept with supporting details.
Limit each slide to 5 bullet points maximum, each with 7-10 words."""
            st.session_state['custom_system_prompt'] = example_prompt
            st.experimental_rerun()
        
        # Educational presentation example
        if st.button("Educational Presentation"):
            example_prompt = """You are an education specialist creating slides for students. Present information in a 
clear, engaging way with simple explanations of complex concepts. Include thought-provoking 
questions on some slides, and organize content in a logical learning progression from 
basic to advanced concepts. Use friendly, accessible language."""
            st.session_state['custom_system_prompt'] = example_prompt
            st.experimental_rerun()
        
        # Business presentation example
        if st.button("Business Presentation"):
            example_prompt = """You are a business presentation expert focusing on persuasive, action-oriented slides.
Create content that highlights key business metrics, strategic insights, and clear 
recommendations. Use professional language, emphasize benefits and impacts, and 
ensure each slide contributes to a compelling business narrative. Include a clear 
call to action in the conclusion."""
            st.session_state['custom_system_prompt'] = example_prompt
            st.experimental_rerun()
    
    with help_tab:
        st.markdown("### Tips for Writing Effective System Prompts")
        st.markdown("""
        1. **Be specific about format**: Mention how many bullet points per slide or words per bullet point
        2. **Define the audience**: Specify who the presentation is for
        3. **Set the tone**: Indicate if you want formal, casual, technical, or simplified language
        4. **Provide structure guidance**: Suggest how information should be organized
        5. **Include domain expertise**: Add specific rules relevant to your topic
        
        For more detailed guidance, see the [System Prompt Guide](https://github.com/your-username/AI_NVCB/blob/main/docs/system_prompt_guide.md).
        """)

# Reference document upload section supporting multiple files
st.markdown("""
    <div class="card fade-in">
        <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
            📄 Reference Documents (optional)
        </h3>
    </div>
""", unsafe_allow_html=True)
document_files = st.file_uploader(
    "Upload one or more documents for AI reference",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Upload documents for AI to reference when creating slides. Supports PDF, DOCX, and TXT"
)
if document_files:
    for doc in document_files:
        st.success(f"Uploaded: {doc.name}")

# Generate button with custom styling
if st.button("🚀 Create Slides", type="primary"):
    if not topic:
        st.error("⚠️ Please enter a topic first.")
    else:
        with st.status("🔄 Creating slides...", expanded=True) as status:
            try:
                start_time = time.time()
                # Include selected model in the generation request
                result = generate_slides(
                    topic=topic, 
                    num_slides=num_slides, 
                    model_name=selected_model if 'selected_model' in locals() else None,
                    document_files=document_files,
                    system_prompt=st.session_state.get('slide_gen_system_prompt') if st.session_state.get('use_custom_prompt', False) else None
                )
                
                # Generate filename based on topic and timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_topic = safe_topic.replace(' ', '_')
                filename = f"{safe_topic}_{timestamp}.pptx"
                
                # Get the output directory path
                output_dir = os.path.join("output", "slides")
                pptx_path = os.path.join(output_dir, filename)
                
                # Wait a short time for the file to be created
                max_attempts = 10
                file_found = False
                
                for attempt in range(max_attempts):
                    if os.path.exists(pptx_path):
                        file_found = True
                        break
                    time.sleep(0.5)  # Wait 0.5 seconds between checks
                
                if file_found:
                    status.update(label="✅ Completed!", state="complete", expanded=False)
                    
                    # Show download button with better styling
                    st.markdown("""
                        <div class="stDownloadButton">
                    """, unsafe_allow_html=True)
                    
                    with open(pptx_path, "rb") as f:
                        file_data = f.read()
                        
                    st.download_button(
                        label="📥 Download PowerPoint",
                        data=file_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Performance metrics with better styling
                    st.markdown(f"""
                        <div class="card fade-in" style='margin-top: 1rem;'>
                            <p style='margin: 0; color: var(--text-primary);'>
                                <strong>⏱️ Execution Time:</strong> {time.time() - start_time:.2f} seconds
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    status.update(label="⚠️ Slides created but the filename might be too long to display, find the file in /output/slides", state="error", expanded=False)
                    st.error(f"⚠️ Unable to find file {filename} due to a long filename. Please find the file in /output/slides.")
                
            except Exception as e:
                status.update(label="❌ Error", state="error", expanded=False)
                st.error(f"⚠️ An error occurred: {e}")

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)
