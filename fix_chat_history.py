"""
Simple fix for chat history using Streamlit session state.
This script creates a simplified conversation component and updates
the document analysis page to use in-memory storage instead of the database.
"""
import os
import sys
import uuid
import time
from pathlib import Path
import shutil
from datetime import datetime

def main():
    """Apply the fix for chat history using in-memory storage"""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Paths to the files we need to create or modify
    component_path = project_root / "frontend" / "components" / "conversation_simple.py"
    document_analysis_path = project_root / "frontend" / "pages" / "document_analysis.py"
    
    # Create the components directory if it doesn't exist
    os.makedirs(component_path.parent, exist_ok=True)
    
    # Create backup of document_analysis.py if it exists
    if document_analysis_path.exists():
        backup_path = document_analysis_path.with_suffix(".py.bak")
        shutil.copy2(document_analysis_path, backup_path)
        print(f"Created backup of document_analysis.py at {backup_path}")
    
    # Content for conversation_simple.py
    conversation_simple_content = '''"""
Simple conversation component that uses Streamlit session state for storage.
This doesn't require database connectivity and works with in-memory storage.
"""
import streamlit as st
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Initialize session state for conversations
if "all_conversations" not in st.session_state:
    st.session_state.all_conversations = {}

if "conversation_messages" not in st.session_state:
    st.session_state.conversation_messages = {}

def create_mock_data():
    """Create some mock conversations for testing"""
    if not st.session_state.all_conversations:
        # Add a few mock conversations
        doc_ids = ["doc1", "doc2", "test-document-id"]
        doc_titles = ["Sample PDF", "Test Document", "Mock Document"]
        
        for i in range(3):
            conv_id = str(uuid.uuid4())
            doc_id = doc_ids[i]
            
            # Create a conversation
            st.session_state.all_conversations[conv_id] = {
                "id": conv_id,
                "document_id": doc_id,
                "title": f"Conversation about {doc_titles[i]}",
                "created_at": time.time(),
                "updated_at": time.time(),
                "meta": {
                    "document_title": doc_titles[i]
                }
            }
            
            # Add some messages
            st.session_state.conversation_messages[conv_id] = [
                {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conv_id,
                    "role": "user",
                    "content": f"What is this document about?",
                    "created_at": time.time()
                },
                {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conv_id,
                    "role": "assistant",
                    "content": f"This document is about {doc_titles[i]}. It contains information related to the topic.",
                    "created_at": time.time() + 1
                }
            ]

def get_conversations(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all conversations from session state"""
    return list(st.session_state.all_conversations.values())[:limit]

def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific conversation by ID"""
    return st.session_state.all_conversations.get(conversation_id)

def get_conversation_messages(conversation_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a conversation"""
    return st.session_state.conversation_messages.get(conversation_id, [])

def create_conversation(document_id: str, title: str = "New Conversation") -> Dict[str, Any]:
    """Create a new conversation"""
    conv_id = str(uuid.uuid4())
    conversation = {
        "id": conv_id,
        "document_id": document_id,
        "title": title,
        "created_at": time.time(),
        "updated_at": time.time(),
        "meta": {
            "document_title": f"Document {document_id}"
        }
    }
    
    st.session_state.all_conversations[conv_id] = conversation
    st.session_state.conversation_messages[conv_id] = []
    
    return conversation

def update_conversation_title(conversation_id: str, new_title: str) -> bool:
    """Update the title of a conversation"""
    if conversation_id in st.session_state.all_conversations:
        st.session_state.all_conversations[conversation_id]["title"] = new_title
        st.session_state.all_conversations[conversation_id]["updated_at"] = time.time()
        return True
    return False

def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation and its messages"""
    if conversation_id in st.session_state.all_conversations:
        del st.session_state.all_conversations[conversation_id]
        if conversation_id in st.session_state.conversation_messages:
            del st.session_state.conversation_messages[conversation_id]
        return True
    return False

def add_message_to_conversation(
    conversation_id: str, 
    content: str, 
    role: str = "user"
) -> Dict[str, Any]:
    """Add a message to a conversation"""
    if conversation_id not in st.session_state.all_conversations:
        return None
    
    message = {
        "id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": time.time()
    }
    
    if conversation_id not in st.session_state.conversation_messages:
        st.session_state.conversation_messages[conversation_id] = []
    
    st.session_state.conversation_messages[conversation_id].append(message)
    
    # Update conversation timestamp
    st.session_state.all_conversations[conversation_id]["updated_at"] = time.time()
    
    # If this is a user message, automatically generate an AI response for testing
    if role == "user":
        ai_message = {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": f"This is a simulated response to: '{content}'",
            "created_at": time.time() + 1
        }
        st.session_state.conversation_messages[conversation_id].append(ai_message)
    
    return message

def render_conversation_thread(messages: List[Dict[str, Any]]) -> None:
    """Render a conversation thread in the UI"""
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        created_at = msg.get("created_at", 0)
        
        # Format timestamp
        if created_at:
            timestamp = datetime.fromtimestamp(created_at).strftime("%H:%M:%S")
        else:
            timestamp = "Unknown time"
        
        # Style based on role
        if role == "user":
            with st.container():
                st.markdown(f"""
                <div style='background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>You <span style='font-weight: normal; color: #666; font-size: 0.8em;'>{timestamp}</span></div>
                    <div>{content}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.container():
                st.markdown(f"""
                <div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>AI Assistant <span style='font-weight: normal; color: #666; font-size: 0.8em;'>{timestamp}</span></div>
                    <div>{content}</div>
                </div>
                """, unsafe_allow_html=True)

# Chat history functions for document QA integration
def initialize_chat_history(document_id: str) -> None:
    """Initialize chat history for a document if it doesn't exist"""
    chat_key = f"chat_history_{document_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
def get_chat_history(document_id: str) -> List[Dict[str, Any]]:
    """Get chat history for a document from session state"""
    chat_key = f"chat_history_{document_id}"
    initialize_chat_history(document_id)
    return st.session_state[chat_key]

def add_chat_message(document_id: str, user_query: str, system_response: str) -> None:
    """Add a new chat message to the history"""
    chat_key = f"chat_history_{document_id}"
    initialize_chat_history(document_id)
    
    # Create message object
    message = {
        "id": str(uuid.uuid4()),
        "document_id": document_id,
        "user_query": user_query,
        "system_response": system_response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to history
    st.session_state[chat_key].append(message)

def clear_chat_history(document_id: str) -> None:
    """Clear chat history for a document"""
    chat_key = f"chat_history_{document_id}"
    st.session_state[chat_key] = []

def display_chat_history(document_id: str) -> None:
    """Display chat history in a Streamlit UI"""
    history = get_chat_history(document_id)
    
    if not history:
        st.info("No conversations with this document yet.")
        return
    
    for msg in history:
        with st.expander(f"Q: {msg['user_query'][:50]}...", expanded=False):
            st.write("**User Question:**")
            st.write(msg['user_query'])
            st.write("**AI Response:**")
            st.write(msg['system_response'])
            st.caption(f"Timestamp: {msg['timestamp']}")

def chat_interface(document_id: str, on_submit_callback) -> None:
    """Create a chat interface for document Q&A with in-memory history"""
    # Initialize history in session state
    initialize_chat_history(document_id)
    
    # Display current history
    history = get_chat_history(document_id)
    
    # Show history in a clean UI
    st.subheader("Previous Questions & Answers")
    
    if not history:
        st.info("No previous questions for this document. Ask something below!")
    else:
        for i, msg in enumerate(history):
            with st.container():
                st.markdown(f"**Question {i+1}:**")
                st.markdown(f"_{msg['user_query']}_")
                st.markdown("**Answer:**")
                st.markdown(msg['system_response'])
                st.markdown("---")
    
    # Input for new question
    with st.form(key=f"qa_form_{document_id}"):
        user_query = st.text_area("Ask a question about this document:", 
                                   height=100, 
                                   placeholder="What would you like to know about this content?")
        submitted = st.form_submit_button("Ask Question")
        
        if submitted and user_query:
            with st.spinner("Processing your question..."):
                # Get response from callback
                response = on_submit_callback(user_query)
                
                # Add to history
                add_chat_message(document_id, user_query, response)
                
                # Force refresh to show new message
                st.experimental_rerun()
'''
    
    # Content for document_analysis.py
    document_analysis_content = '''"""
Document analysis page with simplified in-memory chat history.
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import application modules
from frontend.components.sidebar import create_sidebar
from frontend.components.conversation_simple import (
    initialize_chat_history, display_chat_history, chat_interface, add_chat_message
)
from backend.document_processor import DocumentProcessor
from backend.qa_engine import QAEngine
from utils.config import get_settings

# Import utilities
from typing import Dict, Any, List, Optional

def document_analysis_page():
    """Document Analysis Page"""
    st.title("Document Analysis")
    create_sidebar()
    
    settings = get_settings()
    
    # Document selection or upload
    document_processor = DocumentProcessor()
    documents = document_processor.list_documents()
    
    # If no documents, show upload option
    if not documents:
        st.info("No documents found. Please upload a document first.")
        return
    
    # Create document selection dropdown
    doc_options = {f"{doc['filename']} ({doc['id']})": doc for doc in documents}
    selected_doc_name = st.selectbox("Select a document to analyze:", 
                                      options=list(doc_options.keys()))
    
    if not selected_doc_name:
        st.info("Please select a document to analyze.")
        return
    
    # Get the selected document
    document = doc_options[selected_doc_name]
    document_id = document['id']
    
    # Document details and content preview
    st.subheader("Document Details")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Filename:** {document['filename']}")
        st.write(f"**Content Type:** {document.get('content_type', 'Unknown')}")
    with col2:
        st.write(f"**Size:** {document.get('size', 0) // 1024} KB")
        st.write(f"**Upload Date:** {document.get('created_at', 'Unknown')}")
    
    # Content preview
    with st.expander("Content Preview", expanded=False):
        content = document.get('content', '')
        if content:
            preview_length = min(len(content), 1000)
            st.text_area("Document Content (preview)", 
                         value=content[:preview_length] + ("..." if len(content) > preview_length else ""),
                         height=200, disabled=True)
        else:
            st.info("Content preview not available for this file type.")
    
    # Q&A Interface
    st.header("Ask Questions About This Document")
    
    # Initialize QA Engine
    qa_engine = QAEngine()
    
    def process_question(question: str) -> str:
        """Process the question and get a response"""
        try:
            response = qa_engine.answer_question(document_id, question)
            
            # If API returns a dict with 'answer' key, extract it
            if isinstance(response, dict) and 'answer' in response:
                return response['answer']
            
            # If it's a plain string, use that
            if isinstance(response, str):
                return response
            
            # Fallback
            return str(response)
        except Exception as e:
            st.error(f"Error processing question: {str(e)}")
            return f"I'm sorry, I couldn't process your question due to a technical error. Here's what happened: {str(e)}"
    
    # Initialize chat history in session state
    initialize_chat_history(document_id)
    
    # Display chat interface with in-memory history
    chat_interface(document_id, process_question)
    
    # Add a button to clear the history
    if st.button("Clear Chat History"):
        st.session_state[f"chat_history_{document_id}"] = []
        st.success("Chat history cleared!")
        st.experimental_rerun()

# Launch the page
if __name__ == "__main__":
    document_analysis_page()
'''
    
    # Write the new files
    with open(component_path, 'w') as f:
        f.write(conversation_simple_content)
    
    with open(document_analysis_path, 'w') as f:
        f.write(document_analysis_content)
    
    print("Successfully applied the in-memory chat history fix!")
    print(f"Created: {component_path}")
    print(f"Updated: {document_analysis_path}")
    print("\nTo use the fix:")
    print("1. Restart the Streamlit app")
    print("2. Navigate to Document Analysis")
    print("3. Your chat history will now be stored in memory during your session")

if __name__ == "__main__":
    main()