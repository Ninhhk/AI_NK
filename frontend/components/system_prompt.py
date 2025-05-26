import streamlit as st

def system_prompt_ui(default_prompt="", key_prefix=""):
    """
    Component UI system prompt có thể tái sử dụng.
    
    Args:
        default_prompt: System prompt mặc định để hiển thị
        key_prefix: Tiền tố cho session state keys để tránh xung đột
    
    Returns:
        Giá trị system prompt hiện tại
    """
    # Khởi tạo session state cho instance component này
    session_key = f"{key_prefix}_system_prompt"
    if session_key not in st.session_state:
        st.session_state[session_key] = default_prompt
        
    st.markdown("""
        <div>
            <h3 style='color: var(--text-secondary); margin-top: 0;'>
                Tùy Chỉnh Hành Vi AI
            </h3>
            <p>
                System prompt cung cấp hướng dẫn cho AI về cách xử lý yêu cầu của bạn.
                Bạn có thể tùy chỉnh nó để kiểm soát phong cách, giọng điệu và nội dung phản hồi.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state[session_key],
        height=100,
        help="Hướng dẫn cho AI",
        placeholder="Nhập hướng dẫn cho AI...",
        key=f"{key_prefix}_prompt_textarea"
    )
    
    # Lưu trữ trong session state
    st.session_state[session_key] = system_prompt
    
    # Phần ví dụ với các ví dụ khác nhau dựa trên prefix
    st.markdown("### Ví Dụ System Prompt")
    
    col1, col2 = st.columns(2)
    
    if "doc" in key_prefix:
        # Ví dụ phân tích tài liệu
        with col1:
            if st.button("Phân Tích Kỹ Thuật", key=f"{key_prefix}_tech"):
                example_prompt = """Tập trung vào các khía cạnh kỹ thuật và thuật ngữ. Cung cấp phân tích chi tiết 
với các thuật ngữ kỹ thuật chính xác. Sử dụng giọng điệu trang trọng và cấu trúc thông tin theo thứ bậc."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
        
        with col2:
            if st.button("Phân Tích Giáo Dục", key=f"{key_prefix}_edu"):
                example_prompt = """Phân tích trong bối cảnh giáo dục. Đơn giản hóa các khái niệm phức tạp 
và giải thích chúng theo cách dễ tiếp cận. Tập trung vào kết quả học tập."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
    
    elif "quiz" in key_prefix:
        # Ví dụ quiz
        with col1:
            if st.button("Câu Hỏi Thực Tế", key=f"{key_prefix}_fact"):
                example_prompt = """Tạo câu hỏi kiểm tra khả năng nhớ thực tế và hiểu biết cơ bản.
Tập trung vào câu hỏi rõ ràng, không mơ hồ với câu trả lời đúng cụ thể."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
        
        with col2:
            if st.button("Câu Hỏi Phân Tích", key=f"{key_prefix}_analyt"):
                example_prompt = """Tạo câu hỏi yêu cầu tư duy phản biện và phân tích.
Bao gồm câu hỏi kiểm tra việc áp dụng khái niệm và hiểu biết về mối quan hệ."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
    
    else:
        # Ví dụ chung cho các bối cảnh khác
        with col1:
            if st.button("Phản Hồi Ngắn Gọn", key=f"{key_prefix}_concise"):
                example_prompt = """Cung cấp phản hồi ngắn gọn, trực tiếp mà không có chi tiết không cần thiết.
Chỉ tập trung vào các điểm chính và sử dụng ngôn ngữ đơn giản."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()
        
        with col2:
            if st.button("Phản Hồi Chi Tiết", key=f"{key_prefix}_detailed"):
                example_prompt = """Cung cấp phản hồi chi tiết, toàn diện với các ví dụ.
Giải thích khái niệm một cách kỹ lưỡng và xem xét nhiều góc độ."""
                st.session_state[session_key] = example_prompt
                st.experimental_rerun()

    return system_prompt
