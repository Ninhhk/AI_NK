"""
Sidebar component for the AI application.
This provides consistent navigation and debug options across pages.
"""
import streamlit as st
import os

def create_sidebar():
    """Create a standardized sidebar for the application"""
    with st.sidebar:
        st.title("AI Document Analysis")
        
        # Navigation section
        st.subheader("Navigation")
        st.markdown("- [Home](./)")
        st.markdown("- [Document Analysis](./document_analysis)")
        st.markdown("- [Slide Generation](./slide_generation)")
        st.markdown("- [Conversation Management](./conversation_management)")
        st.markdown("- [Model Management](./model_management)")
        
        # Debug mode toggle
        if "debug_mode" not in st.session_state:
            st.session_state.debug_mode = False
        
        debug_enabled = st.checkbox("Enable Debug Mode", 
                                   value=st.session_state.debug_mode,
                                   key="sidebar_debug_toggle")
        
        if debug_enabled != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_enabled
            st.experimental_rerun()
        
        # API URL display (only in debug mode)
        if st.session_state.debug_mode:
            api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
            st.info(f"API URL: {api_url}")
        
        # Footer
        st.markdown("---")
        st.markdown("**Version**: 1.0.0")
        st.markdown("© 2025 AI Document Analysis")
