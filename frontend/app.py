import streamlit as st

# Configure the page
st.set_page_config(
    page_title="AI NVCB - Chào mừng",
    page_icon="🏠",
    layout="wide"
)

# Title and Introduction
st.title("Chào mừng đến với AI NVCB")
st.markdown("### Công cụ Phân tích Tài liệu & Tạo Bài thuyết trình được hỗ trợ bởi AI")

# Brief Description
st.markdown("""
Công cụ này giúp bạn phân tích tài liệu và tạo các bài thuyết trình chuyên nghiệp bằng công nghệ AI.
Chọn từ hai tính năng chính của chúng tôi trong thanh điều hướng bên:
""")

# Feature Cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Phân tích Tài liệu")
    st.markdown("""
    **Tính năng:**
    - Tải lên tài liệu PDF
    - Nhận tóm tắt ngay lập tức
    - Đặt câu hỏi về tài liệu của bạn
    - Trích xuất thông tin quan trọng
    
    **Cách sử dụng:**
    1. Điều hướng đến 'Phân tích Tài liệu' ở thanh bên
    2. Tải lên tài liệu PDF của bạn
    3. Chọn loại phân tích (Tóm tắt hoặc Hỏi đáp)
    4. Nhận thông tin chi tiết được hỗ trợ bởi AI
    """)
    if st.button("Thử Phân tích Tài liệu →"):
        st.switch_page("pages/document_analysis.py")

with col2:
    st.markdown("### 🎯 Tạo Slide")
    st.markdown("""
    **Tính năng:**
    - Tạo slide thuyết trình từ các chủ đề
    - Tùy chỉnh số lượng slide
    - Nhận nội dung có cấu trúc
    - Xuất sang PowerPoint
    
    **Cách sử dụng:**
    1. Điều hướng đến 'Tạo Slide' ở thanh bên
    2. Nhập chủ đề thuyết trình của bạn
    3. Chọn số lượng slide
    4. Nhận bài thuyết trình được tạo bởi AI
    """)
    if st.button("Thử Tạo Slide →"):
        st.switch_page("pages/slide_generation.py")

# Additional Information
st.markdown("---")
st.markdown("### 💡 Mẹo cho Kết quả Tốt nhất")
st.markdown("""
- **Cho Phân tích Tài liệu:**
  - Sử dụng PDF rõ ràng, dễ đọc
  - Chỉ định phạm vi trang cho tài liệu lớn
  - Đặt câu hỏi cụ thể để có câu trả lời tốt hơn

- **Cho Tạo Slide:**
  - Cung cấp chủ đề rõ ràng, tập trung
  - Sử dụng 5-10 slide để có kết quả tối ưu
  - Xem lại và tùy chỉnh nội dung đã tạo
""")

# Version and Updates
with st.sidebar:
    st.markdown("### Thông tin")
    st.markdown("Phiên bản: 1.0.0")
    st.markdown("Cập nhật lần cuối: Tháng 3 năm 2025")
    
# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Được xây dựng với ❤️ sử dụng FastAPI và Streamlit</p>
    <p>Để được hỗ trợ, liên hệ: support@ainvcb.com</p>
</div>
""", unsafe_allow_html=True)