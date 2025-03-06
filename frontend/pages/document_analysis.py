import streamlit as st
import requests
import time
from typing import Optional

def analyze_document(
    file,
    query_type: str,
    user_query: Optional[str] = None,
    start_page: int = 0,
    end_page: int = -1,
) -> dict:
    """Send document to backend for analysis."""
    files = {"file": file}
    data = {
        "query_type": query_type,
        "start_page": str(start_page),
        "end_page": str(end_page),
    }
    
    if user_query:
        data["user_query"] = user_query
        
    response = requests.post(
        "http://localhost:8000/api/documents/analyze",
        files=files,
        data=data,
    )
    response.raise_for_status()
    return response.json()

st.title("Tri thức bảo an AI - Document Analysis")
st.write(
    "AI-powered document analysis for efficient information processing"
)

with st.sidebar:
    st.header("Document Settings")
    
    st.subheader("Upload Document")
    file = st.file_uploader("Upload document", type=["pdf"])
    if file:
        st.write("Document uploaded successfully")

    st.subheader("Page Range")
    st.write(
        "Select page range. Pages are numbered from 0. For the last page, you can also use negative numbers to count from the end, e.g., -1 is the last page, -2 is second to last, etc."
    )
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Start page:", value=0, min_value=0)
    with col2:
        end_page = st.number_input("End page:", value=-1)

    st.subheader("Analysis Type")
    query_type = st.radio("Select function", ["summary", "qa"])

if query_type == "qa":
    user_query = st.text_area(
        "Your question", value="What data is used in this analysis?"
    )

if st.button("Analyze"):
    result = None
    start = time.time()
    if file is None:
        st.error("Please upload a file.")
    else:
        with st.status("Analyzing...", expanded=True) as status:
            try:
                result = analyze_document(
                    file=file,
                    query_type=query_type,
                    user_query=user_query if query_type == "qa" else None,
                    start_page=start_page,
                    end_page=end_page,
                )
                status.update(label="Done!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Error", state="error", expanded=False)
                st.error(f"An error occurred: {e}")
                result = None

        if result:
            with st.container(border=True):
                st.header("Result")
                st.markdown(result["result"])
                st.info(f"Time taken: {time.time() - start:.2f} seconds", icon="⏱️") 