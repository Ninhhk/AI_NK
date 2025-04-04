import streamlit as st
import requests
import time
from typing import Optional
import json

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

def get_chat_history(document_id: str) -> dict:
    """Retrieve chat history for a document."""
    response = requests.get(
        f"http://localhost:8000/api/documents/chat-history/{document_id}"
    )
    response.raise_for_status()
    return response.json()

def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to a readable format."""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S")

# Initialize session state for document ID
if 'document_id' not in st.session_state:
    st.session_state.document_id = None

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

# Sidebar with settings
with st.sidebar:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ⚙️ Cài Đặt
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📤 Tải Lên Tài Liệu
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("Chọn tệp PDF", type=["pdf"])
    if file:
        st.markdown("""
            <div style='background-color: var(--success-color); color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5em;'>
                ✅ Tài liệu đã được tải lên thành công
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📑 Phạm Vi Trang
            </h3>
            <p style='color: var(--text-primary); margin: 0.5em 0;'>
                Chọn phạm vi trang. Các trang được đánh số từ 0. Đối với trang cuối cùng, bạn cũng có thể sử dụng số âm để đếm từ cuối, ví dụ: -1 là trang cuối cùng, -2 là trang gần cuối, v.v.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Trang bắt đầu:", value=0, min_value=0)
    with col2:
        end_page = st.number_input("Trang kết thúc:", value=-1)

    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🔍 Loại Phân Tích
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    query_type = st.radio("Chọn chức năng", ["summary", "qa"])

# Main content area tabs - QA section and Chat History
tab1, tab2 = st.tabs(["📝 Phân Tích Tài Liệu", "💬 Lịch Sử Trò Chuyện"])

with tab1:
    if query_type == "qa":
        st.markdown("""
            <div class="card fade-in">
                <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                    ❓ Câu hỏi của bạn
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        user_query = st.text_area(
            "",
            value="Dữ liệu nào được sử dụng trong phân tích này?",
            help="Nhập câu hỏi cụ thể để nhận câu trả lời chính xác"
        )

    if st.button("🚀 Phân Tích", type="primary"):
        result = None
        start = time.time()
        if file is None:
            st.error("⚠️ Vui lòng tải lên tệp.")
        else:
            with st.status("🔄 Đang phân tích...", expanded=True) as status:
                try:
                    result = analyze_document(
                        file=file,
                        query_type=query_type,
                        user_query=user_query if query_type == "qa" else None,
                        start_page=start_page,
                        end_page=end_page,
                    )
                    status.update(label="✅ Hoàn thành!", state="complete", expanded=False)

                    # Store document_id for chat history
                    if "document_id" in result:
                        st.session_state.document_id = result["document_id"]
                    
                except Exception as e:
                    status.update(label="❌ Lỗi", state="error", expanded=False)
                    st.error(f"⚠️ Đã xảy ra lỗi: {e}")
                    result = None

            if result:
                st.markdown("""
                    <div class="card fade-in">
                        <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                            📊 Kết Quả
                        </h2>
                        <div style='color: var(--text-primary);'>
                """, unsafe_allow_html=True)
                st.markdown(result["result"])
                st.markdown("</div></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="card fade-in" style='margin-top: 1rem;'>
                        <p style='margin: 0; color: var(--text-primary);'>
                            <strong>⏱️ Thời gian thực hiện:</strong> {time.time() - start:.2f} giây
                        </p>
                    </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                💬 Lịch Sử Trò Chuyện
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if we have a document ID
    if st.session_state.document_id:
        # Add refresh button for chat history
        if st.button("🔄 Làm mới lịch sử", key="refresh_history"):
            st.experimental_rerun()
            
        try:
            history_data = get_chat_history(st.session_state.document_id)
            chat_history = history_data.get("history", [])
            
            if not chat_history:
                st.info("Chưa có cuộc trò chuyện nào với tài liệu này.")
            else:
                # Display chat history in reverse order (newest first)
                for chat in reversed(chat_history):
                    # Chat container with user question and system response
                    st.markdown("""
                        <div class="card fade-in" style="margin-bottom: 1rem; padding: 1rem;">
                    """, unsafe_allow_html=True)
                    
                    # User question
                    st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <p style="color: var(--accent-color); font-weight: bold; margin-bottom: 0.5rem;">
                                🙋 Câu hỏi ({format_timestamp(chat["timestamp"])})
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
                                🤖 Trả lời
                            </p>
                            <div style="background-color: rgba(31, 119, 180, 0.1); padding: 0.8rem; border-radius: 8px; border-left: 3px solid var(--primary-color);">
                                <p style="margin: 0; color: var(--text-primary);">{chat["system_response"]}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Không thể tải lịch sử trò chuyện: {e}")
    else:
        st.info("Vui lòng phân tích tài liệu bằng chức năng Q&A trước để có lịch sử trò chuyện.")

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)