import streamlit as st
import requests
import time
import re  # Added for regex pattern matching
from typing import Optional

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
        response = requests.get("http://localhost:8000/api/slides/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        st.error(f"Error fetching current model: {e}")
        return None

def generate_quiz(
    files: list,
    num_questions: int = 5,
    difficulty: str = "medium",
    start_page: int = 0,
    end_page: int = -1,
    model_name: str = None,
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
        "start_page": str(start_page),
        "end_page": str(end_page),
    }
    
    # Add model_name if specified
    if model_name:
        data["model_name"] = model_name
        
    response = requests.post(
        "http://localhost:8000/api/documents/generate-quiz",
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
                ✅ {len(files)} file(s) uploaded successfully
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📑 Page Range
            </h3>
            <p style='color: var(--text-primary); margin: 0.5em 0;'>
                Select page range for quiz generation. Use -1 for last page.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Start page:", value=0, min_value=0)
    with col2:
        end_page = st.number_input("End page:", value=-1)

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
                    start_page=start_page,
                    end_page=end_page,
                    model_name=model_name,
                )
                elapsed_time = time.time() - start_time
                status.update(label=f"✅ Completed in {elapsed_time:.1f} seconds!", state="complete", expanded=False)

                # Store results for use outside the status block
                quiz_result = result
                st.write("Debug quiz_result:", quiz_result)
                
                # Extract quiz text and guard against missing content
                quiz_text = quiz_result.get("result", "")
                if not quiz_text.strip():
                    st.error("⚠️ Backend returned no quiz content. Full response:")
                    st.json(quiz_result)
                    st.stop()
                actual_questions = len(quiz_text.split("Câu "))
                
            except Exception as e:
                status.update(label="❌ Error", state="error", expanded=True)
                st.error(f"⚠️ An error occurred: {str(e)}")
                st.error("Please try again or adjust the parameters.")
        
        # Display results only if we have a valid quiz_text
        if quiz_text:
            # Display quiz in a card with better formatting
            st.markdown(f"""
                <div class="card fade-in">
                    <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                        📝 Quiz ({actual_questions} questions)
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Split questions by pattern and display them in separate containers
            quiz_content = quiz_text
            questions = []
            current = ""
            
            # Split the content by lines
            lines = quiz_content.split('\n')
            for line in lines:
                if line.strip().startswith("Câu "):
                    if current:
                        questions.append(current.strip())
                    current = line
                elif current:
                    current += "\n" + line
                    
            # Add the last question
            if current:
                questions.append(current.strip())
            
            # Display each question in styled containers (not expanders)
            for i, question in enumerate(questions, 1):
                st.markdown(f"""
                    <div style='background-color: #1e2130; padding: 15px; 
                         border-radius: 10px; border-left: 4px solid var(--primary-color); 
                         margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                        <h4 style='color: var(--primary-color); margin-top: 0;'>Question {i}</h4>
                        <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{question}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Show performance metrics
            st.markdown(f"""
                <div class="card fade-in" style='margin-top: 1rem;'>
                    <p style='margin: 0; color: var(--text-primary);'>
                        <strong>⏱️ Execution time:</strong> {elapsed_time:.2f} seconds
                    </p>
                    <p style='margin: 0; color: var(--text-primary);'>
                        <strong>📊 Questions generated:</strong> {actual_questions}/{num_questions}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Prepare download data
            quiz_text = quiz_text
            st.download_button(
                label="📥 Download Quiz",
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