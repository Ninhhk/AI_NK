import streamlit as st
import requests
import time
import os

# Configure the page
st.set_page_config(
    page_title="AI NVCB - Chào mừng",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to get the current model
def get_current_model():
    """Lấy model đang hoạt động hiện tại từ API"""
    try:
        API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
        response = requests.get(f"{API_BASE_URL}/api/slides/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        return "Không thể kết nối đến API"

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                🏠 AI NVCB
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Công cụ Phân tích Tài liệu, Tạo Bài thuyết trình & Bài Trắc Nghiệm
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Brief Description with animated card
st.markdown("""
    <div class="card fade-in">
        <p style='margin: 0; color: var(--text-primary); font-size: 1.1em;'>
            Công cụ này giúp bạn phân tích tài liệu, tạo các bài thuyết trình chuyên nghiệp và bài trắc nghiệm bằng công nghệ AI.
            Chọn từ các tính năng của chúng tôi trong thanh điều hướng bên:
        </p>
    </div>
""", unsafe_allow_html=True)

# Feature Cards with hover effects
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                📄 Phân tích Tài liệu
            </h2>
            <div style='margin: 1em 0;'>
                <h4 style='color: var(--text-secondary);'>Tính năng:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tải lên tài liệu PDF
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Nhận tóm tắt ngay lập tức
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Đặt câu hỏi về tài liệu
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Trích xuất thông tin quan trọng
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Hỗ trợ nhiều tài liệu
                    </li>
                </ul>
            </div>
            <div style='margin-top: 1.5em;'>
                <h4 style='color: var(--text-secondary);'>Cách sử dụng:</h4>
                <ol style='color: var(--text-primary); padding-left: 1.5em;'>
                    <li style='margin: 0.5em 0;'>Điều hướng đến 'Phân tích Tài liệu'</li>
                    <li style='margin: 0.5em 0;'>Tải lên tài liệu PDF của bạn</li>
                    <li style='margin: 0.5em 0;'>Chọn loại phân tích</li>
                    <li style='margin: 0.5em 0;'>Nhận thông tin chi tiết</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Thử Phân tích Tài liệu →", type="primary"):
        st.switch_page("pages/document_analysis.py")

with col2:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🎯 Tạo Slide
            </h2>
            <div style='margin: 1em 0;'>
                <h4 style='color: var(--text-secondary);'>Tính năng:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tạo slide từ chủ đề
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tùy chỉnh số lượng slide
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Nội dung có cấu trúc
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Xuất sang PowerPoint
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Hỗ trợ tài liệu tham khảo
                    </li>
                </ul>
            </div>
            <div style='margin-top: 1.5em;'>
                <h4 style='color: var(--text-secondary);'>Cách sử dụng:</h4>
                <ol style='color: var(--text-primary); padding-left: 1.5em;'>
                    <li style='margin: 0.5em 0;'>Điều hướng đến 'Tạo Slide'</li>
                    <li style='margin: 0.5em 0;'>Nhập chủ đề thuyết trình</li>
                    <li style='margin: 0.5em 0;'>Chọn số lượng slide</li>
                    <li style='margin: 0.5em 0;'>Nhận bài thuyết trình</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Thử Tạo Slide →", type="primary"):
        st.switch_page("pages/slide_generation.py")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ❓ Tạo Bài Trắc Nghiệm
            </h2>
            <div style='margin: 1em 0;'>
                <h4 style='color: var(--text-secondary);'>Tính năng:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tạo câu hỏi trắc nghiệm
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tùy chỉnh số lượng câu hỏi
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Chọn độ khó
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tự động đáp án
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Hỗ trợ nhiều tài liệu (RAG)
                    </li>
                </ul>
            </div>
            <div style='margin-top: 1.5em;'>
                <h4 style='color: var(--text-secondary);'>Cách sử dụng:</h4>
                <ol style='color: var(--text-primary); padding-left: 1.5em;'>
                    <li style='margin: 0.5em 0;'>Điều hướng đến 'Tạo Bài Trắc Nghiệm'</li>
                    <li style='margin: 0.5em 0;'>Tải lên tài liệu PDF</li>
                    <li style='margin: 0.5em 0;'>Tùy chỉnh cài đặt</li>
                    <li style='margin: 0.5em 0;'>Nhận bài trắc nghiệm</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Thử Tạo Bài Trắc Nghiệm →", type="primary"):
        st.switch_page("pages/quiz_generation.py")

with col2:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🤖 Quản Lý Model
            </h2>
            <div style='margin: 1em 0;'>
                <h4 style='color: var(--text-secondary);'>Tính năng:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Xem danh sách model
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Thay đổi model đang sử dụng
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Tùy chỉnh system prompt
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>✓</span> Quản lý cài đặt hệ thống
                    </li>
                </ul>
            </div>
            <div style='margin-top: 1.5em;'>
                <h4 style='color: var(--text-secondary);'>Cách sử dụng:</h4>
                <ol style='color: var(--text-primary); padding-left: 1.5em;'>
                    <li style='margin: 0.5em 0;'>Điều hướng đến 'Quản Lý Model'</li>
                    <li style='margin: 0.5em 0;'>Xem các model có sẵn</li>
                    <li style='margin: 0.5em 0;'>Chọn model để sử dụng</li>
                    <li style='margin: 0.5em 0;'>Tùy chỉnh system prompt</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Quản Lý Model →", type="primary"):
        st.switch_page("pages/model_management.py")

# Tips section with animated cards
st.markdown("""
    <div class="card fade-in" style='margin-top: 2em;'>
        <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
            💡 Mẹo cho Kết quả Tốt nhất
        </h2>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 2em; margin-top: 1em;'>
            <div>
                <h4 style='color: var(--text-secondary);'>Cho Phân tích Tài liệu:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> PDF rõ ràng, dễ đọc
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Chỉ định phạm vi trang
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Câu hỏi cụ thể
                    </li>
                </ul>
            </div>
            <div>
                <h4 style='color: var(--text-secondary);'>Cho Tạo Trắc Nghiệm:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Tài liệu rõ ràng
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Chọn độ khó phù hợp
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Có thể sử dụng nhiều tài liệu
                    </li>
                </ul>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Model info
try:
    current_model = get_current_model()
    st.markdown(f"""
        <div class="card fade-in" style='margin-top: 1em;'>
            <p style='color: var(--accent-color); font-weight: bold; margin: 0;'>
                🤖 Model đang sử dụng: {current_model}
            </p>
        </div>
    """, unsafe_allow_html=True)
except:
    pass

# Version and Updates in sidebar
with st.sidebar:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ℹ️ Thông tin
            </h2>
            <div style='margin-top: 1em;'>
                <p style='color: var(--text-primary); margin: 0.5em 0;'>
                    <strong>Phiên bản:</strong> 2.0.0
                </p>
                <p style='color: var(--text-primary); margin: 0.5em 0;'>
                    <strong>Cập nhật:</strong> Tháng 5 năm 2025
                </p>
                <p style='color: var(--text-primary); margin: 0.5em 0;'>
                    <strong>Tính năng mới:</strong> RAG cho Trắc Nghiệm
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### Điều Hướng")
    st.markdown("- [Trang Chủ](./)")
    st.markdown("- [Phân Tích Tài Liệu](./document_analysis)")
    st.markdown("- [Tạo Slide](./slide_generation)")
    st.markdown("- [Tạo Bài Trắc Nghiệm](./quiz_generation)")
    st.markdown("- [Quản Lý Model](./model_management)")
    
# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Được Hỗ Trợ Bởi Công Nghệ AI | Được Tạo Với ❤️</p>
    </div>
""", unsafe_allow_html=True)
