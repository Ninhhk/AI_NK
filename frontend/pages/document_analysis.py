import streamlit as st
import requests
import time
from typing import Optional

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

# Main content area
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

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)