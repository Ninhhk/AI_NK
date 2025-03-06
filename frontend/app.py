import streamlit as st

# Configure the page
st.set_page_config(
    page_title="AI NVCB - Welcome",
    page_icon="🏠",
    layout="wide"
)

# Title and Introduction
st.title("Welcome to AI NVCB")
st.markdown("### Your AI-Powered Document Analysis & Presentation Generation Tool")

# Brief Description
st.markdown("""
This tool helps you analyze documents and generate professional presentations using AI technology.
Choose from our two main features in the sidebar navigation:
""")

# Feature Cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Document Analysis")
    st.markdown("""
    **Features:**
    - Upload PDF documents
    - Get instant summaries
    - Ask questions about your documents
    - Extract key information
    
    **How to use:**
    1. Navigate to 'Document Analysis' in the sidebar
    2. Upload your PDF document
    3. Choose analysis type (Summary or Q&A)
    4. Get AI-powered insights
    """)
    if st.button("Try Document Analysis →"):
        st.switch_page("pages/document_analysis.py")

with col2:
    st.markdown("### 🎯 Slide Generation")
    st.markdown("""
    **Features:**
    - Generate presentation slides from topics
    - Customize number of slides
    - Get structured content
    - Export to PowerPoint
    
    **How to use:**
    1. Navigate to 'Slide Generation' in the sidebar
    2. Enter your presentation topic
    3. Choose number of slides
    4. Get AI-generated presentation
    """)
    if st.button("Try Slide Generation →"):
        st.switch_page("pages/slide_generation.py")

# Additional Information
st.markdown("---")
st.markdown("### 💡 Tips for Best Results")
st.markdown("""
- **For Document Analysis:**
  - Use clear, readable PDFs
  - Specify page ranges for large documents
  - Ask specific questions for better answers

- **For Slide Generation:**
  - Provide clear, focused topics
  - Use 5-10 slides for optimal results
  - Review and customize generated content
""")

# Version and Updates
with st.sidebar:
    st.markdown("### About")
    st.markdown("Version: 1.0.0")
    st.markdown("Last Updated: March 2025")
    
# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using FastAPI and Streamlit</p>
    <p>For support, contact: support@ainvcb.com</p>
</div>
""", unsafe_allow_html=True) 