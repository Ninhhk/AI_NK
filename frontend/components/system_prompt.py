import streamlit as st

def system_prompt_ui(default_prompt="", key_prefix=""):
    """
    Reusable system prompt UI component.
    
    Args:
        default_prompt: Default system prompt to display
        key_prefix: Prefix for session state keys to avoid conflicts
    
    Returns:
        The current system prompt value
    """
    # Initialize session state for this component instance
    session_key = f"{key_prefix}_system_prompt"
    if session_key not in st.session_state:
        st.session_state[session_key] = default_prompt
        
    st.markdown("""
        <div>
            <h3 style='color: var(--text-secondary); margin-top: 0;'>
                Customize AI Behavior
            </h3>
            <p>
                The system prompt provides instructions to the AI about how to process your request.
                You can customize it to control the style, tone, and content of responses.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state[session_key],
        height=100,
        help="Instructions for the AI",
        placeholder="Enter instructions for the AI...",
        key=f"{key_prefix}_prompt_textarea"
    )
    
    # Store in session state
    st.session_state[session_key] = system_prompt
    
    # Examples section with different examples based on the prefix
    st.markdown("### Example System Prompts")
    
    col1, col2 = st.columns(2)
    
    if "doc" in key_prefix:
        # Document analysis examples
        with col1:
            if st.button("Technical Analysis", key=f"{key_prefix}_tech"):
                example_prompt = """Focus on technical aspects and terminology. Provide detailed analysis 
with accurate technical terms. Use a formal tone and structure information hierarchically."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
        
        with col2:
            if st.button("Educational Analysis", key=f"{key_prefix}_edu"):
                example_prompt = """Analyze in an educational context. Simplify complex concepts 
and explain them in an accessible way. Focus on learning outcomes."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
    
    elif "quiz" in key_prefix:
        # Quiz examples
        with col1:
            if st.button("Factual Questions", key=f"{key_prefix}_fact"):
                example_prompt = """Create questions that test factual recall and basic understanding.
Focus on clear, unambiguous questions with specific correct answers."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
        
        with col2:
            if st.button("Analytical Questions", key=f"{key_prefix}_analyt"):
                example_prompt = """Create questions that require critical thinking and analysis.
Include questions that test application of concepts and understanding of relationships."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
    
    else:
        # General examples for other contexts
        with col1:
            if st.button("Concise Responses", key=f"{key_prefix}_concise"):
                example_prompt = """Provide concise, direct responses without unnecessary details.
Focus on key points only and use simple language."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
        
        with col2:
            if st.button("Detailed Responses", key=f"{key_prefix}_detailed"):
                example_prompt = """Provide detailed, comprehensive responses with examples.
Explain concepts thoroughly and consider multiple perspectives."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()

    return system_prompt
