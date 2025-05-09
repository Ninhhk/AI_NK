import streamlit as st
import requests
import time
from typing import Optional, List
import json
import pkg_resources

# Set page config for better appearance
st.set_page_config(
    page_title="AI Document Analysis",
    page_icon="📄",
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

def analyze_document(
    files: List,
    query_type: str,
    user_query: Optional[str] = None,
    start_page: int = 0,
    end_page: int = -1,
    model_name: Optional[str] = None,
) -> dict:
    """Send document(s) to backend for analysis."""
    # Prepare files for multi-file upload
    files_dict = {}
    
    if len(files) == 1:
        # Single file case
        files_dict = {"file": files[0]}
    else:
        # Multiple files case - properly send all files
        # Main file (required by the API)
        files_dict["file"] = files[0]
        
        # Add all additional files using both methods to ensure compatibility
        # 1. Using extra_files_N parameters (for older API versions)
        for i, f in enumerate(files[1:5]):  # Support up to 5 additional files
            files_dict[f"extra_files_{i+1}"] = f
            
        # 2. Also use files[] format for newer API versions that support it
        for i, f in enumerate(files):
            files_dict[f"files[{i}]"] = f
    
    data = {
        "query_type": query_type,
        "start_page": str(start_page),
        "end_page": str(end_page),
    }
    
    if user_query:
        data["user_query"] = user_query
    
    if model_name:
        data["model_name"] = model_name
    
    # Log request info if in debug mode
    if st.session_state.debug_mode:
        st.write(f"Sending {len(files)} files to the backend")
        for i, f in enumerate(files):
            st.write(f"File {i+1}: {f.name}")
        
    response = requests.post(
        "http://localhost:8000/api/documents/analyze",
        files=files_dict,
        data=data,
    )
    response.raise_for_status()
    return response.json()

def get_chat_history(document_id: str) -> dict:
    """Retrieve chat history for a document."""
    response = requests.get(
        f"http://localhost:8000/api/documents/chat-history/{document_id}"
    )
    response.raise_for_status()
    return response.json()

def load_chat_history():
    """Load chat history and store in session state"""
    if st.session_state.document_id:
        try:
            history_data = get_chat_history(st.session_state.document_id)
            st.session_state.chat_history = history_data.get("history", [])
            st.session_state.chat_history_last_loaded = time.time()
            return True
        except requests.exceptions.ConnectionError:
            if st.session_state.debug_mode:
                st.error("Cannot connect to server. Please check if the backend server has been started.")
            else:
                st.error("Cannot connect to server. Please try again later.")
            return False
        except requests.exceptions.HTTPError as e:
            if st.session_state.debug_mode:
                st.error(f"HTTP error when loading chat history: {e}")
            if "404" in str(e):
                st.warning("API endpoint for chat history does not exist. Please update the backend code.")
            return False
        except Exception as e:
            if st.session_state.debug_mode:
                st.error(f"Error loading chat history: {e}")
            return False
    return False

def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to a readable format."""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S")

def get_streamlit_version():
    """Get the installed Streamlit version."""
    try:
        return pkg_resources.get_distribution("streamlit").version
    except:
        return "unknown"

def refresh_page():
    """Refresh the page using the appropriate Streamlit method based on version compatibility."""
    streamlit_version = get_streamlit_version()
    
    # Log version for debugging
    if st.session_state.get('debug_mode', False):
        st.info(f"Streamlit version: {streamlit_version}")
    
    try:
        # For Streamlit >= 1.27.0
        if streamlit_version != "unknown" and tuple(map(int, streamlit_version.split('.')[:2])) >= (1, 27):
            st.rerun()
        else:
            # For older versions
            st.experimental_rerun()
    except Exception as e:
        # Fallback message if both methods fail
        st.warning(f"Unable to refresh page automatically. Please refresh the page manually. (Error: {e})")

# Initialize session state variables
if 'document_id' not in st.session_state:
    st.session_state.document_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_history_last_loaded' not in st.session_state:
    st.session_state.chat_history_last_loaded = 0

# Debug mode flag - set to True to enable debug information
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False  # Change to True for debugging

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                📄 Document Analysis
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Efficient Information Processing with AI
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
                📤 Upload Document
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    files = st.file_uploader("Select PDF file", type=["pdf"], accept_multiple_files=True)
    if files:
        st.markdown("""
            <div style='background-color: var(--success-color); color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5em;'>
                ✅ Document uploaded successfully
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📑 Page Range
            </h3>
            <p style='color: var(--text-primary); margin: 0.5em 0;'>
                Select page range. Pages are numbered from 0. For the last page, you can also use negative numbers to count from the end, e.g., -1 is the last page, -2 is the second-to-last page, etc.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Start page:", value=0, min_value=0)
    with col2:
        end_page = st.number_input("End page:", value=-1)
        
    # Display current model information
    current_model = get_current_model()
    if current_model:
        st.info(f"🤖 Using model: **{current_model}**. You can change the model in the Model Management page.", icon="ℹ️")

    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🔍 Analysis Type
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    query_type = st.radio("Select function", ["summary", "qa"])

# Main content area tabs - QA section and Chat History
tab1, tab2 = st.tabs(["📝 Document Analysis", "💬 Chat History"])

with tab1:
    if query_type == "qa":
        st.markdown("""
            <div class="card fade-in">
                <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                    ❓ Your Question
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        user_query = st.text_area(
            "",
            value="What data is used in this analysis?",
            help="Enter a specific question to get an accurate answer"
        )

    if st.button("🚀 Analyze", type="primary"):
        result = None
        start = time.time()
        if not files:
            st.error("⚠️ Please upload a file.")
        else:
            with st.status("🔄 Analyzing...", expanded=True) as status:
                try:
                    model_name = get_current_model()
                    result = analyze_document(
                        files=files,
                        query_type=query_type,
                        user_query=user_query if query_type == "qa" else None,
                        start_page=start_page,
                        end_page=end_page,
                        model_name=model_name,
                    )
                    status.update(label="✅ Completed!", state="complete", expanded=False)

                    # Store document_id for chat history
                    if "document_id" in result:
                        st.session_state.document_id = result["document_id"]
                        # If this was a QA query, reload chat history
                        if query_type == "qa":
                            # Add a slight delay to allow the backend to update
                            time.sleep(0.5)
                            load_chat_history()
                    
                except Exception as e:
                    status.update(label="❌ Error", state="error", expanded=False)
                    st.error(f"⚠️ An error occurred: {e}")
                    result = None

            if result:
                # Check if we have document information to display
                has_multiple_docs = "document_count" in result and result["document_count"] > 1
                
                # Display result header and result content
                st.markdown("""
                    <div class="card fade-in">
                        <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                            📊 Results
                        </h2>
                        <div style='color: var(--text-primary);'>
                """, unsafe_allow_html=True)
                
                # Format result content to highlight citations
                content = result["result"]
                
                # If we have multiple documents, add a document reference section
                if has_multiple_docs and "documents" in result:
                    st.markdown("""
                        <div style="background-color: #f0f7ff; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #3498db;">
                            <h4 style="margin-top: 0; color: #2c3e50;">Documents used:</h4>
                            <ul style="margin-bottom: 0;">
                    """, unsafe_allow_html=True)
                    
                    for doc in result.get("documents", []):
                        st.markdown(f"""
                            <li>
                                <strong>[{doc['id']}]</strong>: {doc['filename']}
                            </li>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Format the content to highlight citations like [doc_1_abc123]
                import re
                if has_multiple_docs:
                    # Find all citation patterns like [doc_X_XXXXX] in the text
                    citation_pattern = r'\[(doc_\d+_[a-z0-9]+)\]'
                    
                    # Split by citations to preserve formatting
                    parts = re.split(f'({citation_pattern})', content)
                    
                    formatted_parts = []
                    for i, part in enumerate(parts):
                        # Check if this part is a citation
                        if i % 2 == 1 and re.match(citation_pattern, part):
                            # Format as a citation badge
                            citation_id = part[1:-1]  # Remove brackets
                            formatted_parts.append(f'<span style="background-color: #e1f5fe; padding: 2px 6px; border-radius: 3px; color: #0277bd; font-weight: bold; font-size: 0.9em;">{part}</span>')
                        else:
                            formatted_parts.append(part)
                    
                    # Join parts back together
                    formatted_content = ''.join(formatted_parts)
                    st.markdown(formatted_content, unsafe_allow_html=True)
                else:
                    # Regular content without special formatting
                    st.markdown(content)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
                
                # Display timing information
                st.markdown(f"""
                    <div class="card fade-in" style='margin-top: 1rem;'>
                        <p style='margin: 0; color: var(--text-primary);'>
                            <strong>⏱️ Execution time:</strong> {time.time() - start:.2f} seconds
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display debug information if enabled
                if st.session_state.debug_mode and "debug" in result:
                    st.expander("Debug Information").write(result["debug"])

with tab2:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                💬 Chat History
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if we have a document ID
    if st.session_state.document_id:
        # Add refresh button for chat history - manually call the load function
        if st.button("🔄 Refresh history", key="refresh_history"):
            # Load chat history into session state
            success = load_chat_history()
            if success and st.session_state.debug_mode:
                st.success("Chat history refreshed!")
            
        # Load chat history if not already loaded
        if not st.session_state.chat_history or time.time() - st.session_state.chat_history_last_loaded > 30:
            load_chat_history()
            
        # Display debug info if needed
        if st.session_state.debug_mode:
            st.info(f"Streamlit version: {get_streamlit_version()}")
            st.info(f"Loaded {len(st.session_state.chat_history)} messages from chat history.")
            st.info(f"Last updated: {format_timestamp(st.session_state.chat_history_last_loaded)}")
        
        # Display chat history from session state
        if not st.session_state.chat_history:
            st.info("No conversations with this document yet.")
        else:
            # Display chat history in reverse order (newest first)
            for chat in reversed(st.session_state.chat_history):
                # Chat container with user question and system response
                st.markdown("""
                    <div class="card fade-in" style="margin-bottom: 1rem; padding: 1rem;">
                """, unsafe_allow_html=True)
                
                # User question
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <p style="color: var(--accent-color); font-weight: bold; margin-bottom: 0.5rem;">
                            🙋 Question ({format_timestamp(chat["timestamp"])})
                        </p>
                        <div style="background-color: rgba(52, 152, 219, 0.1); padding: 0.8rem; border-radius: 8px; border-left: 3px solid var(--accent-color);">
                            <p style="margin: 0; color: var(--text-primary);">{chat["user_query"]}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # System response
                st.markdown(f"""
                    <div>
                        <p style="color: var(--primary-color); font-weight: bold; margin-bottom: 0.5rem;">
                            🤖 Response
                        </p>
                        <div style="background-color: rgba(31, 119, 180, 0.1); padding: 0.8rem; border-radius: 8px; border-left: 3px solid var(--primary-color);">
                            <p style="margin: 0; color: var(--text-primary);">{chat["system_response"]}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Please analyze a document using the Q&A function first to have chat history.")

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)