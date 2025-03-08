import streamlit as st
import time

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

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                🏠 AI NVCB
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Công cụ Phân tích Tài liệu & Tạo Bài thuyết trình được hỗ trợ bởi AI
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
            Công cụ này giúp bạn phân tích tài liệu và tạo các bài thuyết trình chuyên nghiệp bằng công nghệ AI.
            Chọn từ hai tính năng chính của chúng tôi trong thanh điều hướng bên:
        </p>
    </div>
""", unsafe_allow_html=True)

# Feature Cards with hover effects
col1, col2, col3 = st.columns(3)

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

with col3:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ❓ Tạo Bài Kiểm Tra
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
                </ul>
            </div>
            <div style='margin-top: 1.5em;'>
                <h4 style='color: var(--text-secondary);'>Cách sử dụng:</h4>
                <ol style='color: var(--text-primary); padding-left: 1.5em;'>
                    <li style='margin: 0.5em 0;'>Điều hướng đến 'Tạo Bài Kiểm Tra'</li>
                    <li style='margin: 0.5em 0;'>Tải lên tài liệu PDF</li>
                    <li style='margin: 0.5em 0;'>Tùy chỉnh cài đặt</li>
                    <li style='margin: 0.5em 0;'>Nhận bài kiểm tra</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Thử Tạo Bài Kiểm Tra →", type="primary"):
        st.switch_page("pages/quiz_generation.py")

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
                <h4 style='color: var(--text-secondary);'>Cho Tạo Slide:</h4>
                <ul style='color: var(--text-primary); list-style-type: none; padding-left: 0;'>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Chủ đề rõ ràng
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> 5-10 slide tối ưu
                    </li>
                    <li style='margin: 0.5em 0; display: flex; align-items: center; gap: 0.5em;'>
                        <span style='color: var(--accent-color);'>•</span> Tùy chỉnh nội dung
                    </li>
                </ul>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Version and Updates in sidebar
with st.sidebar:
    st.markdown("""
        <div class="card fade-in">
            <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                ℹ️ Thông tin
            </h2>
            <div style='margin-top: 1em;'>
                <p style='color: var(--text-primary); margin: 0.5em 0;'>
                    <strong>Phiên bản:</strong> 1.0.0
                </p>
                <p style='color: var(--text-primary); margin: 0.5em 0;'>
                    <strong>Cập nhật:</strong> Tháng 3 năm 2025
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
        <p style='margin: 0.5em 0;'>Để được hỗ trợ, liên hệ: support@ainvcb.com</p>
    </div>
""", unsafe_allow_html=True)