import streamlit as st
import requests
import json
import time
import os
from datetime import datetime

# Set page config for better appearance
st.set_page_config(
    page_title="AI Slide Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add custom styles for status and download button
st.markdown("""
    <style>
    .stStatus {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stStatus > div {
        color: var(--text-primary);
    }
    .stStatus[data-state="complete"] {
        background: linear-gradient(135deg, var(--success-color) 0%, #27ae60 100%);
    }
    .stStatus[data-state="error"] {
        background: linear-gradient(135deg, var(--error-color) 0%, #c0392b 100%);
    }
    .stDownloadButton {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stDownloadButton:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    .stDownloadButton > button {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

def generate_slides(topic: str, num_slides: int, document_file=None) -> dict:
    """Send content to backend for slide generation."""
    files = {}
    if document_file:
        files["document"] = document_file
        
    data = {
        "topic": topic,
        "num_slides": num_slides
    }
    
    response = requests.post(
        "http://localhost:8000/api/slides/generate",
        files=files,
        data=data
    )
    response.raise_for_status()
    return response.json()

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                🎯 Tạo Slide
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Tạo Bài Thuyết Trình Chuyên Nghiệp Với AI
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Input section with better layout
col1, col2 = st.columns([2,1])

with col1:
    topic = st.text_input(
        "📝 Chủ đề của bạn",
        placeholder="Nhập chủ đề bạn muốn tạo slide cho...",
        help="Nhập một chủ đề rõ ràng để AI có thể tạo slide phù hợp"
    )

with col2:
    num_slides = st.number_input(
        "📊 Số lượng slide",
        min_value=1,
        max_value=20,
        value=5,
        help="Chọn số lượng slide bạn muốn tạo (tối đa 20 slide)"
    )

# Document upload section
st.markdown("""
    <div class="card fade-in">
        <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
            📄 Tài liệu tham khảo (không bắt buộc)
        </h3>
    </div>
""", unsafe_allow_html=True)

document_file = st.file_uploader("Tải lên tài liệu để AI tham khảo nội dung", 
                                type=["pdf", "docx", "txt"], 
                                help="Tải lên tài liệu để AI tham khảo khi tạo slide. Hỗ trợ PDF, DOCX, và TXT")

if document_file:
    st.success(f"Đã tải lên tài liệu: {document_file.name}")

# Generate button with custom styling
if st.button("🚀 Tạo Slide", type="primary"):
    if not topic:
        st.error("⚠️ Vui lòng nhập chủ đề trước.")
    else:
        with st.status("🔄 Đang tạo slide...", expanded=True) as status:
            try:
                start_time = time.time()
                result = generate_slides(topic, num_slides, document_file)
                
                # Generate filename based on topic and timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_topic = safe_topic.replace(' ', '_')
                filename = f"{safe_topic}_{timestamp}.pptx"
                
                # Get the output directory path
                output_dir = os.path.join("output", "slides")
                pptx_path = os.path.join(output_dir, filename)
                
                # Wait a short time for the file to be created
                max_attempts = 10
                file_found = False
                
                for attempt in range(max_attempts):
                    if os.path.exists(pptx_path):
                        file_found = True
                        break
                    time.sleep(0.5)  # Wait 0.5 seconds between checks
                
                if file_found:
                    status.update(label="✅ Hoàn thành!", state="complete", expanded=False)
                    
                    # Show download button with better styling
                    st.markdown("""
                        <div class="stDownloadButton">
                    """, unsafe_allow_html=True)
                    
                    with open(pptx_path, "rb") as f:
                        file_data = f.read()
                        
                    st.download_button(
                        label="📥 Tải PowerPoint",
                        data=file_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Performance metrics with better styling
                    st.markdown(f"""
                        <div class="card fade-in" style='margin-top: 1rem;'>
                            <p style='margin: 0; color: var(--text-primary);'>
                                <strong>⏱️ Thời gian thực hiện:</strong> {time.time() - start_time:.2f} giây
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    status.update(label="⚠️ Đã tạo slide nhưng tên file có thể quá dài để hiển thị, tìm file trong /output/sildes", state="error", expanded=False)
                    st.error(f"⚠️ Không thể tìm thấy file {filename} do tên quá dài. Vui lòng tìm file trong /output/sildes.")
                
            except Exception as e:
                status.update(label="❌ Lỗi", state="error", expanded=False)
                st.error(f"⚠️ Đã xảy ra lỗi: {e}")

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)