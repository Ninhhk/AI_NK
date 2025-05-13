import streamlit as st
import requests
import time
import re  # Added for regex pattern matching
from typing import Optional
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from frontend.components.system_prompt import system_prompt_ui

# API Base URL (can be customized via environment variable)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Set page config for better appearance
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to get the current model
def get_current_model():
    """Get the currently active model from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/slides/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        st.error(f"Error fetching current model: {e}")
        return None

def get_system_prompt():
    """Get the current system prompt."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/system-prompt")
        response.raise_for_status()
        return response.json()["system_prompt"]
    except Exception as e:
        st.error(f"Error fetching system prompt: {e}")
        return ""

def set_system_prompt(prompt: str):
    """Set the system prompt."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/documents/system-prompt",
            data={"system_prompt": prompt}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error setting system prompt: {e}")
        return None

def generate_quiz(
    files: list,
    num_questions: int = 5,
    difficulty: str = "medium",
    model_name: str = None,
    system_prompt: str = None,
) -> dict:
    """Send document to backend for quiz generation."""
    # Prepare multipart payload for multiple files
    files_dict = {}
    # Primary file
    if files:
        f0 = files[0]
        files_dict['file'] = (f0.name, f0.read(), f0.type)
    # Extra files parameters (up to 5)
    for i, f in enumerate(files[1:6], start=1):
        files_dict[f'extra_files_{i}'] = (f.name, f.read(), f.type)
    # Also include array format for newer APIs
    for i, f in enumerate(files):
        files_dict[f'files[{i}]'] = (f.name, f.read(), f.type)
    
    data = {
        "num_questions": str(num_questions),
        "difficulty": difficulty,
    }
    
    # Add model_name if specified
    if model_name:
        data["model_name"] = model_name
      # Add system_prompt if specified
    if system_prompt:
        # Ensure Vietnamese requirement is included in the system prompt
        if "vietnam" not in system_prompt.lower() and "tiếng việt" not in system_prompt.lower():
            system_prompt = f"Phải trả lời bằng tiếng Việt. {system_prompt}"
        data["system_prompt"] = system_prompt
    else:
        # Add a default Vietnamese system prompt if none is provided
        data["system_prompt"] = "Phải trả lời bằng tiếng Việt. Tạo bài trắc nghiệm theo định dạng rõ ràng."
        
    response = requests.post(
        f"{API_BASE_URL}/api/documents/generate-quiz",
        files=files_dict,
        data=data,
    )
    response.raise_for_status()
    return response.json()

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                ❓ AI Quiz Generator
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Automatically generate quizzes from your documents
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Sidebar with settings
with st.sidebar:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ⚙️ Settings
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📤 Upload Documents
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True)
    if files:
        st.markdown(f"""
            <div style='background-color: var(--success-color); color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5em;'>
                ✅ {len(files)} file(s) uploaded successfully            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🎯 Quiz Options
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    num_questions = st.slider(
        "Number of questions:",
        min_value=1,
        max_value=20,
        value=5,
        help="Select the number of questions for the quiz"
    )
    
    difficulty = st.select_slider(
        "Difficulty:",
        options=["easy", "medium", "hard"],
        value="medium",
        format_func=lambda x: x.capitalize(),
        help="Select the difficulty level for the questions"
    )
      # Display current model information
    current_model = get_current_model()
    if current_model:
        st.info(f"🤖 Using model: **{current_model}**. You can change the model in the Model Management page.", icon="ℹ️")
        
    # Add system prompt UI - first try to get current system prompt
    current_system_prompt = ""
    try:
        current_system_prompt = get_system_prompt()
    except:
        # If API is not available, use an empty default prompt
        pass
        
    # Show the system prompt UI component
    system_prompt = system_prompt_ui(default_prompt=current_system_prompt, key_prefix="quiz_gen")
    
    # Add a button to save the system prompt globally
    if st.button("💾 Save System Prompt Globally"):
        result = set_system_prompt(system_prompt)
        if result:
            st.success("✅ System prompt saved globally")
        else:
            st.error("❌ Failed to save system prompt")

# Main content area
if st.button("🚀 Generate Quiz", type="primary"):
    if not files:
        st.error("⚠️ Please upload at least one PDF before generating a quiz.")
    else:
        # Variables to store results outside the status block
        quiz_result = None
        elapsed_time = 0
        actual_questions = 0

        # Process the file and generate quiz
        with st.status("🔄 Creating quiz...", expanded=True) as status:
            status.update(label="🔄 Processing document...", state="running")
            try:
                start_time = time.time()

                # Add progress updates
                time.sleep(0.5)  # Brief pause for visual feedback
                status.update(label="🔄 Analyzing content...", state="running")
                time.sleep(0.5)  # Brief pause for visual feedback
                status.update(label="🔄 Generating questions... This may take a few minutes.", state="running")
                model_name = get_current_model()
                result = generate_quiz(
                    files=files,
                    num_questions=num_questions,
                    difficulty=difficulty,
                    model_name=model_name,
                    system_prompt=st.session_state.get('quiz_gen_system_prompt', "")
                )
                elapsed_time = time.time() - start_time
                status.update(label=f"✅ Completed in {elapsed_time:.1f} seconds!", state="complete", expanded=False)
                # Store results for use outside the status block
                quiz_result = result

                # Extract quiz text and guard against missing content
                quiz_text = quiz_result.get("result", "")
                if not quiz_text.strip():
                    st.error("⚠️ Backend returned no quiz content. Full response:")
                    st.json(quiz_result)
                    st.stop()

                # Count questions - check for both English and Vietnamese formats
                english_questions = quiz_text.count("Question ")
                vietnamese_questions = quiz_text.count("Câu ")
                option_count = quiz_text.count("A. ")
                actual_questions = max(english_questions, vietnamese_questions)
                if actual_questions == 0 and option_count > 0:
                    actual_questions = option_count

            except Exception as e:
                status.update(label="❌ Error", state="error", expanded=True)
                st.error(f"⚠️ An error occurred: {str(e)}")
                st.error("Please try again or adjust the parameters.")

        # Display results only if we have a valid quiz_text
        if quiz_result and quiz_text:
            st.markdown(f"""
                <div class="card fade-in">
                    <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                        📝 Bài trắc nghiệm ({actual_questions} câu hỏi)
                    </h2>
                </div>
            """, unsafe_allow_html=True)

            quiz_content = quiz_text
            questions = []
            current = ""

            lines = quiz_content.split('\n')
            for line in lines:
                if re.match(r'^Question\s+\d+', line.strip()) or line.strip().startswith("Câu "):
                    if current:
                        questions.append(current.strip())
                    current = line
                elif re.match(r'^[A-D]\.', line.strip()) and not current:
                    current = f"Question {len(questions) + 1}:\n{line}"
                elif current:
                    current += "\n" + line

            if current:
                questions.append(current.strip())

            cleaned_questions = []
            for q in questions:
                if "Questions generated" in q or "generated:" in q or "📊" in q:
                    continue
                cleaned_questions.append(q)

            if cleaned_questions:
                for i, question in enumerate(cleaned_questions, 1):
                    st.markdown(f"""
                        <div style='background-color: #1e2130; padding: 15px; 
                             border-radius: 10px; border-left: 4px solid var(--primary-color); 
                             margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                            <h4 style='color: var(--primary-color); margin-top: 0;'>{'Câu hỏi' if 'Câu' in question else 'Question'} {i}</h4>
                            <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{question}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Không thể phân tích câu hỏi thành các phần riêng biệt. Hiển thị nội dung đầy đủ dưới đây:", icon="ℹ️")
                option_pattern = r'([A-D]\.\s.*?)(?=[A-D]\.\s|$)'
                option_parts = re.findall(option_pattern, quiz_text, re.DOTALL)
                if option_parts:
                    for i, part in enumerate(option_parts):
                        st.markdown(f"""
                            <div style='background-color: #1e2130; padding: 15px; 
                                border-radius: 10px; border-left: 4px solid var(--accent-color); 
                                margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                                <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{part.strip()}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='background-color: #1e2130; padding: 15px; 
                             border-radius: 10px; border-left: 4px solid var(--primary-color); 
                             margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                            <h4 style='color: var(--primary-color); margin-top: 0;'>Quiz Content</h4>
                            <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{quiz_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="card fade-in" style='margin-top: 1rem;'>
                    <p style='margin: 0; color: var(--text-primary);'>
                        <strong>⏱️ Thời gian thực thi:</strong> {elapsed_time:.2f} giây
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📥 Tải xuống bài trắc nghiệm",
                data=quiz_text,
                file_name=f"quiz_{num_questions}q_{difficulty}.txt",
                mime="text/plain",
            )

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)
