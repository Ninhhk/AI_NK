import streamlit as st
import requests
import time
import re  # Added for regex pattern matching
from typing import Optional

# Set page config for better appearance
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def generate_quiz(
    file,
    num_questions: int = 5,
    difficulty: str = "medium",
    start_page: int = 0,
    end_page: int = -1,
) -> dict:
    """Send document to backend for quiz generation."""
    files = {"file": file}
    data = {
        "num_questions": str(num_questions),
        "difficulty": difficulty,
        "start_page": str(start_page),
        "end_page": str(end_page),
    }
        
    response = requests.post(
        "http://localhost:8000/api/documents/generate-quiz",
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
                ❓ Tạo Bài Kiểm Tra
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Tạo Bài Kiểm Tra Tự Động Từ Tài Liệu Với AI
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
                Chọn phạm vi trang để tạo câu hỏi. Sử dụng -1 cho trang cuối cùng.
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
                🎯 Tùy Chọn Bài Kiểm Tra
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    num_questions = st.slider(
        "Số câu hỏi:",
        min_value=1,
        max_value=20,
        value=5,
        help="Chọn số lượng câu hỏi cho bài kiểm tra"
    )
    
    difficulty = st.select_slider(
        "Độ khó:",
        options=["easy", "medium", "hard"],
        value="medium",
        format_func=lambda x: {"easy": "Dễ", "medium": "Trung bình", "hard": "Khó"}[x],
        help="Chọn độ khó cho các câu hỏi"
    )

# Main content area
if st.button("🚀 Tạo Bài Kiểm Tra", type="primary"):
    if file is None:
        st.error("⚠️ Vui lòng tải lên tệp PDF trước khi tạo bài kiểm tra.")
    else:
        # Variables to store results outside the status block
        quiz_result = None
        elapsed_time = 0
        actual_questions = 0
        
        # Process the file and generate quiz
        with st.status("🔄 Đang tạo bài kiểm tra...", expanded=True) as status:
            status.update(label="🔄 Đang xử lý tài liệu...", state="running")
            try:
                start_time = time.time()
                
                # Add progress updates
                time.sleep(0.5)  # Brief pause for visual feedback
                status.update(label="🔄 Đang phân tích nội dung...", state="running")
                time.sleep(0.5)  # Brief pause for visual feedback
                status.update(label="🔄 Đang tạo câu hỏi... Quá trình này có thể mất vài phút.", state="running")
                
                result = generate_quiz(
                    file=file,
                    num_questions=num_questions,
                    difficulty=difficulty,
                    start_page=start_page,
                    end_page=end_page,
                )
                elapsed_time = time.time() - start_time
                status.update(label=f"✅ Hoàn thành trong {elapsed_time:.1f} giây!", state="complete", expanded=False)

                # Store results for use outside the status block
                quiz_result = result
                actual_questions = result["result"].count("Câu ")
                
            except Exception as e:
                status.update(label="❌ Lỗi", state="error", expanded=True)
                st.error(f"⚠️ Đã xảy ra lỗi: {str(e)}")
                st.error("Vui lòng thử lại hoặc điều chỉnh các tham số.")
        
        # Display results only if we have a valid quiz_result
        if quiz_result is not None:
            # Display quiz in a card with better formatting
            st.markdown(f"""
                <div class="card fade-in">
                    <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                        📝 Bài Kiểm Tra ({actual_questions} câu hỏi)
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Split questions by pattern and display them in separate containers
            quiz_content = quiz_result["result"]
            questions = []
            current = ""
            
            # Split the content by lines
            lines = quiz_content.split('\n')
            for line in lines:
                if line.strip().startswith("Câu "):
                    if current:
                        questions.append(current.strip())
                    current = line
                elif current:
                    current += "\n" + line
                    
            # Add the last question
            if current:
                questions.append(current.strip())
            
            # Display each question in styled containers (not expanders)
            for i, question in enumerate(questions, 1):
                st.markdown(f"""
                    <div style='background-color: #1e2130; padding: 15px; 
                         border-radius: 10px; border-left: 4px solid var(--primary-color); 
                         margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                        <h4 style='color: var(--primary-color); margin-top: 0;'>Câu hỏi {i}</h4>
                        <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{question}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Show performance metrics
            st.markdown(f"""
                <div class="card fade-in" style='margin-top: 1rem;'>
                    <p style='margin: 0; color: var(--text-primary);'>
                        <strong>⏱️ Thời gian thực hiện:</strong> {elapsed_time:.2f} giây
                    </p>
                    <p style='margin: 0; color: var(--text-primary);'>
                        <strong>📊 Câu hỏi được tạo:</strong> {actual_questions}/{num_questions} câu hỏi
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Add download button for the quiz
            quiz_text = quiz_result["result"]
            st.download_button(
                label="📥 Tải xuống bài kiểm tra",
                data=quiz_text,
                file_name=f"quiz_{num_questions}q_{difficulty}.txt",
                mime="text/plain",
            )

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Powered by AI Technology | Made with ❤️</p>
    </div>
""", unsafe_allow_html=True)