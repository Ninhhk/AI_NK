import streamlit as st
import requests
import time
from typing import Optional, List
import json
import pkg_resources
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from frontend.components.system_prompt import system_prompt_ui
from frontend.components.conversation_simple import add_chat_message, initialize_chat_history, chat_interface

# Set page config for better appearance
st.set_page_config(
    page_title="Phân Tích Tài Liệu AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL (can be customized via environment variable)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to get the current model
def get_current_model():
    """Lấy model đang hoạt động hiện tại từ API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/slides/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        st.error(f"Lỗi khi lấy thông tin model hiện tại: {e}")
        return None

def analyze_document(
    files: List,
    query_type: str,
    user_query: Optional[str] = None,
    model_name: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> dict:
    """Gửi tài liệu lên backend để phân tích."""
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
    }
    
    if user_query:
        data["user_query"] = user_query
    
    if model_name:
        data["model_name"] = model_name
        
    if system_prompt:
        data["system_prompt"] = system_prompt
    
    # Log request info if in debug mode
    if st.session_state.debug_mode:
        st.write(f"Sending {len(files)} files to the backend")
        for i, f in enumerate(files):
            st.write(f"File {i+1}: {f.name}")
        
    response = requests.post(
        f"{API_BASE_URL}/api/documents/analyze",
        files=files_dict,
        data=data,
    )
    response.raise_for_status()
    return response.json()

def get_chat_history(document_id: str) -> dict:
    """Retrieve chat history for a document."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/documents/chat-history/{document_id}"
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        if st.session_state.debug_mode:
            st.error(f"Error retrieving chat history: {e}")
        return {"history": []}

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

def is_valid_uuid(test_string):
    """Check if a string is a valid UUID format"""
    import re
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', test_string))

def is_old_hash_format(test_string):
    """Check if a string is in old MD5 hash format"""
    import re
    return bool(re.match(r'^[a-f0-9]{32}$', test_string))

def load_chat_history():
    """Load chat history and store in session state with document ID validation"""
    if not st.session_state.document_id:
        if st.session_state.debug_mode:
            st.info("No document ID available for chat history loading")
        return False
        
    document_id = st.session_state.document_id
    
    # CRITICAL: Check if we have an old hash-based document ID
    if is_old_hash_format(document_id):
        st.error(f"🚨 Old hash-based document ID detected: {document_id}")
        st.error("This document was processed with the old system. Please:")        
        st.error("1. Refresh the page and upload a new document")
        st.error("2. If the issue persists, restart the application")
        st.error("3. The new document will get a proper UUID format ID")
        st.session_state.chat_history = []
        st.session_state.chat_history_last_loaded = time.time()
        return False
    
    # Verify we have a valid UUID format
    if not is_valid_uuid(document_id):
        st.error(f"🚨 Invalid document ID format: {document_id}")
        st.error("Expected UUID format like: a562ca5b-649b-4cb2-bc34-3ee3fd06d0c3")
        st.session_state.chat_history = []
        st.session_state.chat_history_last_loaded = time.time()
        return False
    
    try:
        if st.session_state.debug_mode:
            st.write(f"Loading chat history for document ID: {document_id}")
            st.success(f"✅ Valid UUID format detected: {document_id}")
        
        # Get chat history from API
        history_data = get_chat_history(document_id)
        st.session_state.chat_history = history_data.get("history", [])
        st.session_state.chat_history_last_loaded = time.time()
        
        # Show debug info
        if st.session_state.debug_mode:
            st.info(f"Chat history loaded from API: {len(st.session_state.chat_history)} messages")
        
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

def display_analysis_results(result, query_type, start_time):
    """Display analysis results in a consistent format for both QA and summary modes."""
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
    if query_type == "qa" and "answer" in result:
        content = result["answer"]  # In QA mode, the answer is in result["answer"]
    elif "result" in result:
        content = result["result"]  # In summary mode, the result is in result["result"]
    else:
        content = "No result content available."
    
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
                <strong>⏱️ Execution time:</strong> {time.time() - start_time:.2f} seconds
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display debug information if enabled
    if st.session_state.debug_mode and "debug" in result:
        st.expander("Debug Information").write(result["debug"])
      # Chat interface removed - users can access chat history via the Chat History tab

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
           st.rerun()
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
    st.session_state.debug_mode = True  # Change to False after debugging

# Create a custom sidebar with document upload, function selection, and system prompt
with st.sidebar:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📤 Tải Lên Tài Liệu
            </h2>
        </div>
    """, unsafe_allow_html=True)    # Debug section removed for cleaner UI
    
    files = st.file_uploader("Chọn file PDF", type=["pdf"], accept_multiple_files=True)
    if files:
        st.markdown("""
            <div style='background-color: var(--success-color); color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5em;'>
                ✅ Tài liệu đã được tải lên thành công
            </div>
        """, unsafe_allow_html=True)
      # Display current model information
    current_model = get_current_model()
    if current_model:
        st.info(f"🤖 Đang sử dụng model: **{current_model}**. Bạn có thể thay đổi model trong trang Quản Lý Model.", icon="ℹ️")
    
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🔍 Loại Phân Tích
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    query_type = st.radio("Chọn chức năng", ["summary", "qa"])
    
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ⚙️ System Prompt
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # First get the current system prompt from the API
    current_system_prompt = ""
    try:
        current_system_prompt = get_system_prompt()
    except:
        # If API is not available, use an empty default prompt
        pass
        
    # Show the system prompt UI component
    system_prompt = system_prompt_ui(default_prompt=current_system_prompt, key_prefix="doc_analysis")
      # Add a button to save the system prompt globally
    if st.button("💾 Lưu System Prompt Toàn Cục"):
        result = set_system_prompt(system_prompt)
        if result:
            st.success("✅ System prompt đã được lưu toàn cục")
        else:
            st.error("❌ Không thể lưu system prompt")
    
    # Add a divider at the bottom
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Thông Tin Ứng Dụng**")
    st.markdown("Phiên bản: 1.0.0")
    st.markdown("© 2025 Phân Tích Tài Liệu AI")

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                📄 Phân Tích Tài Liệu
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Xử Lý Thông Tin Hiệu Quả Với AI
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Main content area tabs - QA section and Chat History
tab1, tab2 = st.tabs(["📝 Phân Tích Tài Liệu", "💬 Lịch Sử Trò Chuyện"])

with tab1:
    # Show a clean question area when document is uploaded    if files:
        if query_type == "qa":
            st.markdown("""
                <div class="card fade-in">
                    <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                        ❓ Câu Hỏi Của Bạn
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            user_query = st.text_area(
                "",
                value="Dữ liệu nào được sử dụng trong phân tích này?",
                help="Nhập câu hỏi cụ thể để nhận được câu trả lời chính xác",
                height=100
            )
            
            # Make the analyze button more prominent
            if st.button("🚀 Phân Tích Tài Liệu", type="primary", use_container_width=True):
                result = None
                start = time.time()
                with st.status("🔄 Đang phân tích tài liệu...", expanded=True) as status:
                    try:
                        model_name = get_current_model()
                        result = analyze_document(
                            files=files,
                            query_type=query_type,                            user_query=user_query if query_type == "qa" else None,
                            model_name=model_name,
                            system_prompt=system_prompt                        )
                        status.update(label="✅ Hoàn thành!", state="complete", expanded=False)
                        
                        # CRITICAL FIX: Clear any existing document ID first to avoid using cached old hash-based IDs
                        st.session_state.document_id = None
                        
                        # Store document_id for chat history - prioritize multi_document_id for multi-file scenarios
                        if "multi_document_id" in result:
                            st.session_state.document_id = result["multi_document_id"]
                            if st.session_state.debug_mode:
                                st.info(f"✅ Using multi_document_id: {result['multi_document_id']}")
                        elif "document_id" in result:
                            st.session_state.document_id = result["document_id"]
                            if st.session_state.debug_mode:
                                st.info(f"✅ Got document_id: {result['document_id']}")
                        elif "document_ids" in result and result["document_ids"]:
                            # Use the first document ID if we have a list
                            st.session_state.document_id = result["document_ids"][0]
                            if st.session_state.debug_mode:
                                st.info(f"✅ Using first document_id from document_ids: {result['document_ids'][0]}")
                        
                        # Validate the document ID format
                        if st.session_state.document_id:
                            if is_valid_uuid(st.session_state.document_id):
                                if st.session_state.debug_mode:
                                    st.success(f"✅ Valid UUID format document ID assigned: {st.session_state.document_id}")
                            else:
                                st.error(f"🚨 Invalid document ID format received from backend: {st.session_state.document_id}")
                                st.session_state.document_id = None
                                
                        # If this was a QA query, setup chat history
                        if query_type == "qa" and st.session_state.document_id:
                            # Add a slight delay to allow the backend to update
                            time.sleep(0.5)
                            
                            # Add the QA result to our in-memory chat history
                            from frontend.components.conversation_simple import add_chat_message, initialize_chat_history
                            
                            # Initialize chat history for this document
                            initialize_chat_history(st.session_state.document_id)
                            
                            # Add the new message pair
                            if "answer" in result:
                                add_chat_message(
                                    document_id=st.session_state.document_id,
                                    user_query=user_query,
                                    system_response=result["answer"]
                                )
                            
                            # Debug the document ID we're using
                            if st.session_state.debug_mode:
                                st.write(f"Analyzing complete, using document_id: {st.session_state.document_id}")
                                
                            # Load chat history to update the display
                            load_chat_history()
                            
                            # Debug the full result object
                            if st.session_state.debug_mode:
                                st.json(result)
                    except Exception as e:
                        status.update(label="❌ Error", state="error", expanded=False)
                        st.error(f"⚠️ An error occurred: {e}")
                        result = None
                  # Display results if available in QA mode
                if result:
                    # Call the common results display function
                    display_analysis_results(result, query_type, start)
        else:
            # Summary mode
            st.markdown("""
                <div class="card fade-in">
                    <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                        📝 Tạo Tóm Tắt Tài Liệu
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Initialize result to None
            result = None
            
            # Make the analyze button more prominent
            if st.button("🚀 Tạo Tóm Tắt", type="primary", use_container_width=True):
                start = time.time()
                with st.status("🔄 Generating summary...", expanded=True) as status:
                    try:
                        model_name = get_current_model()
                        result = analyze_document(
                            files=files,
                            query_type=query_type,
                            model_name=model_name,
                            system_prompt=system_prompt                        )
                        status.update(label="✅ Completed!", state="complete", expanded=False)
                        
                        # CRITICAL FIX: Clear any existing document ID first to avoid using cached old hash-based IDs
                        st.session_state.document_id = None
                        
                        # Store document_id for chat history - prioritize multi_document_id for multi-file scenarios
                        if "multi_document_id" in result:
                            st.session_state.document_id = result["multi_document_id"]
                            if st.session_state.debug_mode:
                                st.info(f"✅ Using multi_document_id: {result['multi_document_id']}")
                        elif "document_id" in result:
                            st.session_state.document_id = result["document_id"]
                            if st.session_state.debug_mode:
                                st.info(f"✅ Got document_id: {result['document_id']}")
                        elif "document_ids" in result and result["document_ids"]:
                            # Use the first document ID if we have a list
                            st.session_state.document_id = result["document_ids"][0]
                            if st.session_state.debug_mode:
                                st.info(f"✅ Using first document_id from document_ids: {result['document_ids'][0]}")
                        
                        # Validate the document ID format
                        if st.session_state.document_id:
                            if is_valid_uuid(st.session_state.document_id):
                                if st.session_state.debug_mode:
                                    st.success(f"✅ Valid UUID format document ID assigned: {st.session_state.document_id}")
                            else:
                                st.error(f"🚨 Invalid document ID format received from backend: {st.session_state.document_id}")
                                st.session_state.document_id = None
                                
                        # Load chat history
                        if st.session_state.document_id:
                            load_chat_history()
                            
                            # For QA-like interactions in summary mode
                            if "answer" in result:
                                # Add a slight delay to allow the backend to update
                                time.sleep(0.5)
                                
                                # Add the QA result to our in-memory chat history
                                from frontend.components.conversation_simple import add_chat_message, initialize_chat_history
                                
                                # Initialize chat history for this document
                                initialize_chat_history(st.session_state.document_id)
                                
                                # Add the new message pair
                                add_chat_message(
                                    document_id=st.session_state.document_id,
                                    user_query="Generate a summary of this document",
                                    system_response=result["answer"]
                                )
                                
                                # Debug the document ID we're using
                                if st.session_state.debug_mode:
                                    st.write(f"Analyzing complete, using document_id: {st.session_state.document_id}")
                                    
                                # Load chat history to update the display
                                load_chat_history()
                                
                                # Debug the full result object
                                if st.session_state.debug_mode:
                                    st.json(result)
                    except Exception as e:
                        status.update(label="❌ Error", state="error", expanded=False)
                        st.error(f"⚠️ An error occurred: {e}")
                        result = None

            if result:
                # Call the common results display function
                display_analysis_results(result, query_type, start)

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
