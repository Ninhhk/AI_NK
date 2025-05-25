# filepath: frontend/components/conversation_simple.py
import streamlit as st
import time
import requests
import os
from datetime import datetime
import uuid
from typing import Dict, List, Any, Optional, Callable

# API Base URL (can be customized via environment variable)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Initialize session state for conversations if not exists
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to a readable format."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S, %b %d")

def get_conversations(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get conversations from session state."""
    if 'conversations' not in st.session_state:
        st.session_state.conversations = []
    
    # Sort conversations by updated_at (newest first)
    sorted_convs = sorted(
        st.session_state.conversations, 
        key=lambda x: x.get('updated_at', 0), 
        reverse=True
    )
    
    # Apply limit and offset
    return sorted_convs[offset:offset+limit]

def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """Get a specific conversation by ID."""
    if 'conversations' not in st.session_state:
        return {}
    
    for conv in st.session_state.conversations:
        if conv.get('id') == conversation_id:
            return conv
    
    return {}

def get_conversation_messages(conversation_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Get messages for a specific conversation."""
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = {}
    
    if conversation_id not in st.session_state.conversation_messages:
        return []
    
    # Sort messages by timestamp
    sorted_msgs = sorted(
        st.session_state.conversation_messages[conversation_id],
        key=lambda x: x.get('created_at', 0)
    )
    
    # Apply limit and offset
    return sorted_msgs[offset:offset+limit]

def add_message_to_conversation(conversation_id: str, content: str, role: str = "user", parent_id: Optional[str] = None) -> Dict[str, Any]:
    """Add a new message to a conversation."""
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = {}
    
    if conversation_id not in st.session_state.conversation_messages:
        st.session_state.conversation_messages[conversation_id] = []
    
    message = {
        'id': str(uuid.uuid4()),
        'conversation_id': conversation_id,
        'content': content,
        'role': role,
        'parent_id': parent_id,
        'created_at': time.time(),
        'model': 'mock-model'
    }
    
    st.session_state.conversation_messages[conversation_id].append(message)
    
    # Update conversation's updated_at timestamp
    for conv in st.session_state.conversations:
        if conv.get('id') == conversation_id:
            conv['updated_at'] = time.time()
            break
    
    # If it's a user message, automatically generate an AI response
    if role == "user":
        ai_message = {
            'id': str(uuid.uuid4()),
            'conversation_id': conversation_id,
            'content': f"This is a simulated AI response to: {content}",
            'role': "assistant",
            'parent_id': message['id'],
            'created_at': time.time() + 1,  # 1 second later
            'model': 'mock-model'
        }
        st.session_state.conversation_messages[conversation_id].append(ai_message)
        
        return {
            'user_message': message,
            'assistant_message': ai_message
        }
    
    return {'message': message}

def update_conversation_title(conversation_id: str, title: str) -> Dict[str, Any]:
    """Update the title of a conversation."""
    for conv in st.session_state.conversations:
        if conv.get('id') == conversation_id:
            conv['title'] = title
            conv['updated_at'] = time.time()
            return conv
    
    return {}

def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation."""
    if 'conversations' not in st.session_state:
        return False
    
    # Find and remove the conversation
    for i, conv in enumerate(st.session_state.conversations):
        if conv.get('id') == conversation_id:
            st.session_state.conversations.pop(i)
            
            # Remove associated messages
            if 'conversation_messages' in st.session_state:
                if conversation_id in st.session_state.conversation_messages:
                    del st.session_state.conversation_messages[conversation_id]
            
            return True
    
    return False

def create_conversation(document_id: str, title: str = "New Conversation", user_id: str = "default_user") -> Dict[str, Any]:
    """Create a new conversation."""
    if 'conversations' not in st.session_state:
        st.session_state.conversations = []
    
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = {}
    
    conversation_id = str(uuid.uuid4())
    now = time.time()
    
    conversation = {
        'id': conversation_id,
        'document_id': document_id,
        'user_id': user_id,
        'title': title,
        'created_at': now,
        'updated_at': now,
        'meta': {
            'document_title': f"Document {document_id[:8]}"
        }
    }
    
    st.session_state.conversations.append(conversation)
    st.session_state.conversation_messages[conversation_id] = []
    
    return conversation

def render_conversation_thread(messages, truncate_length=500):
    """Render a conversation thread."""
    if not messages:
        st.info("No messages in this conversation yet.")
        return
    
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        
        if role == 'user':
            st.markdown(f"**🧑 You:** {content if len(content) < truncate_length else content[:truncate_length] + '...'}")
        else:
            st.markdown(f"**🤖 AI:** {content if len(content) < truncate_length else content[:truncate_length] + '...'}")

def conversation_sidebar(selected_document_id: Optional[str] = None):
    """Display a sidebar with conversation navigation."""
    st.sidebar.markdown("## 💬 Conversations")
    
    # Show existing conversations for this document
    conversations = []
    if selected_document_id:
        for conv in st.session_state.conversations:
            if conv.get('document_id') == selected_document_id:
                conversations.append(conv)
    
    if conversations:
        st.sidebar.markdown("### Previous conversations:")
        for conv in conversations:
            if st.sidebar.button(f"📝 {conv.get('title', 'Untitled')}"):
                st.session_state.selected_conversation_id = conv.get('id')
                st.session_state.conversation_mode = "existing"
                st.rerun()
    
    # Button to start a new conversation
    if selected_document_id and st.sidebar.button("➕ New Conversation"):
        # Create a new conversation
        new_conv = create_conversation(
            document_id=selected_document_id,
            title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        st.session_state.selected_conversation_id = new_conv.get('id')
        st.session_state.conversation_mode = "new"
        st.rerun()

# Create some mock data on first load
def create_mock_data():
    """Create some mock conversations and messages for testing."""
    if 'mock_data_created' not in st.session_state:
        # Create a few mock conversations
        mock_docs = [str(uuid.uuid4()) for _ in range(3)]
        
        for i, doc_id in enumerate(mock_docs):
            # Create 2 conversations per document
            for j in range(2):
                conv = create_conversation(
                    document_id=doc_id,
                    title=f"Sample Conversation {i+1}-{j+1}",
                    user_id="default_user"
                )
                
                # Add some messages
                add_message_to_conversation(
                    conversation_id=conv['id'],
                    content=f"This is a sample question for document {i+1}?",
                    role="user"
                )
                
                add_message_to_conversation(
                    conversation_id=conv['id'],
                    content=f"Let me tell you about document {i+1}. This is a test document used for showcasing the conversation interface.",
                    role="assistant"
                )
                
                # Add a follow-up question
                response = add_message_to_conversation(
                    conversation_id=conv['id'],
                    content=f"Can you provide more details about document {i+1}?",
                    role="user"                )
        
        st.session_state.mock_data_created = True

# Functions for document_analysis page
def initialize_chat_history(document_id: str):
    """Initialize chat history for a document."""
    try:
        # Initialize chat history on the backend
        response = requests.post(
            f"{API_BASE_URL}/api/documents/chat-history/{document_id}/initialize"
        )
        response.raise_for_status()
        
        # Also initialize in memory for the current session
        if 'in_memory_chat_history' not in st.session_state:
            st.session_state.in_memory_chat_history = {}
        
        if document_id not in st.session_state.in_memory_chat_history:
            st.session_state.in_memory_chat_history[document_id] = []
            
        return True
    except Exception as e:
        if 'debug_mode' in st.session_state and st.session_state.debug_mode:
            st.error(f"Failed to initialize chat history: {e}")
        
        # Still initialize the local memory
        if 'in_memory_chat_history' not in st.session_state:
            st.session_state.in_memory_chat_history = {}
        
        if document_id not in st.session_state.in_memory_chat_history:
            st.session_state.in_memory_chat_history[document_id] = []
            
        return False

def add_chat_message(document_id: str, user_query: str, system_response: str):
    """Add a Q&A pair to the chat history."""
    try:
        # Create a message entry
        message = {
            'user_query': user_query,
            'system_response': system_response,
            'timestamp': time.time()
        }
        
        # Send message to backend API
        response = requests.post(
            f"{API_BASE_URL}/api/documents/chat-history/{document_id}/add",
            json=message
        )
        response.raise_for_status()
        
        # Also keep track in memory for the current session
        if 'in_memory_chat_history' not in st.session_state:
            st.session_state.in_memory_chat_history = {}
        
        if document_id not in st.session_state.in_memory_chat_history:
            st.session_state.in_memory_chat_history[document_id] = []
        
        # Add to history
        st.session_state.in_memory_chat_history[document_id].append(message)
        
        return True
    except Exception as e:
        if st.session_state.debug_mode:
            st.error(f"Failed to add chat message: {e}")
        return False

def chat_interface(document_id: str, on_submit_callback=None):
    """Display a chat interface for follow-up questions."""
    # Chat input
    user_question = st.text_area(
        "Ask a follow-up question:",
        placeholder="What else would you like to know?",
        height=100,
        key=f"chat_input_{document_id}"
    )
    
    # Submit button
    col1, col2 = st.columns([1, 3])
    with col1:
        submit = st.button(
            "🚀 Ask",
            key=f"chat_submit_{document_id}",
            use_container_width=True
        )
    
    # Process the question when submitted
    if submit and user_question:
        with st.status("Processing follow-up question...", expanded=True) as status:
            # Call the callback function to process the question
            if on_submit_callback:
                answer = on_submit_callback(user_question)
                
                if answer:
                    # Add to chat history
                    add_chat_message(
                        document_id=document_id,
                        user_query=user_question,
                        system_response=answer
                    )
                    
                    # Show the answer
                    status.update(label="✅ Answer ready!", state="complete", expanded=False)
                    st.success("Answer successfully generated!")
                    
                    # Force a rerun to refresh the chat history display
                    st.rerun()
                else:
                    status.update(label="❌ Failed to get an answer", state="error")
                    st.error("No answer was returned. Please try a different question.")
            else:
                status.update(label="❌ No callback defined", state="error")
                st.error("Cannot process question without a callback function.")

# Initialize mock data
create_mock_data()
