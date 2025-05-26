"""
Component sidebar cho ứng dụng AI.
Cung cấp điều hướng nhất quán và tùy chọn debug trên các trang.
"""
import streamlit as st
import os

def create_sidebar():
    """Tạo sidebar tiêu chuẩn cho ứng dụng"""
    with st.sidebar:
        st.title("Phân Tích Tài Liệu AI")
          # Phần điều hướng
        st.subheader("Điều Hướng")
        st.markdown("- [Trang Chủ](./)")
        st.markdown("- [Phân Tích Tài Liệu](./document_analysis)")
        st.markdown("- [Tạo Slide](./slide_generation)")
        st.markdown("- [Tạo Bài Trắc Nghiệm](./quiz_generation)")
        st.markdown("- [Quản Lý Model](./model_management)")
        
        # Chuyển đổi chế độ debug
        if "debug_mode" not in st.session_state:
            st.session_state.debug_mode = False
        
        debug_enabled = st.checkbox("Bật Chế Độ Debug", 
                                   value=st.session_state.debug_mode,
                                   key="sidebar_debug_toggle")
        
        if debug_enabled != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_enabled
            st.experimental_rerun()
        
        # Hiển thị API URL (chỉ trong chế độ debug)
        if st.session_state.debug_mode:
            api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
            st.info(f"URL API: {api_url}")
          # Footer
        st.markdown("---")
        st.markdown("**Phiên bản**: 2.0.0")
        st.markdown("**Cập nhật**: Tháng 5 năm 2025")
        st.markdown("**Tính năng mới**: RAG cho Trắc Nghiệm")
        st.markdown("© 2025 AI NVCB")
