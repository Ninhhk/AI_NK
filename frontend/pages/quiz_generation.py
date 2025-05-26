import streamlit as st
import requests
import time
import re  # Added for regex pattern matching
from typing import Optional
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from frontend.components.system_prompt import system_prompt_ui

# API Base URL (can be customized via environment variable)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Set page config for better appearance
st.set_page_config(
    page_title="Tạo Bài Trắc Nghiệm AI",
    page_icon="❓",
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
        response = requests.get(f"{API_BASE_URL}/api/slides/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        st.error(f"Lỗi khi lấy model hiện tại: {e}")
        return None

def get_system_prompt():
    """Lấy system prompt hiện tại."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/system-prompt")
        response.raise_for_status()
        return response.json()["system_prompt"]
    except Exception as e:
        st.error(f"Lỗi khi lấy system prompt: {e}")
        return ""

def set_system_prompt(prompt: str):
    """Đặt system prompt."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/documents/system-prompt",
            data={"system_prompt": prompt}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Lỗi khi đặt system prompt: {e}")
        return None

def generate_quiz(
    files: list,
    num_questions: int = 5,
    difficulty: str = "medium",
    model_name: str = None,
    system_prompt: str = None,
    use_multiple_endpoint: bool = False,
) -> dict:
    """Gửi tài liệu đến backend để tạo bài trắc nghiệm."""
    # Chuẩn bị multipart payload cho nhiều files
    files_dict = {}
    
    # Always use the single endpoint for now
    endpoint = "/api/documents/generate-quiz"
    
    if len(files) == 1:
        # Single file quiz endpoint
        f0 = files[0]
        files_dict['file'] = (f0.name, f0.read(), f0.type)
    else:
        # Multi-file handling with proper parameter names
        # Main file
        f0 = files[0]
        files_dict['file'] = (f0.name, f0.read(), f0.type)
        
        # Extra files (up to 5)
        for i, f in enumerate(files[1:6], start=1):
            if i <= 5:  # Ensure we don't exceed the limit
                files_dict[f'extra_files_{i}'] = (f.name, f.read(), f.type)
    
    data = {
        "num_questions": str(num_questions),
        "difficulty": difficulty,
    }
    
    # Thêm model_name nếu được chỉ định
    if model_name:
        data["model_name"] = model_name
    # Thêm system_prompt nếu được chỉ định
    if system_prompt:
        # Đảm bảo yêu cầu tiếng Việt được bao gồm trong system prompt
        if "vietnam" not in system_prompt.lower() and "tiếng việt" not in system_prompt.lower():
            system_prompt = f"Phải trả lời bằng tiếng Việt. {system_prompt}"
        data["system_prompt"] = system_prompt
    else:
        # Thêm system prompt tiếng Việt mặc định nếu không có
        data["system_prompt"] = "Phải trả lời bằng tiếng Việt. Tạo bài trắc nghiệm theo định dạng rõ ràng."
        
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        files=files_dict,
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
                ❓ Tạo Bài Trắc Nghiệm AI
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Tự động tạo bài trắc nghiệm từ tài liệu của bạn
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
    
    files = st.file_uploader("Chọn file PDF", type=["pdf"], accept_multiple_files=True)
    if files:
        st.markdown(f"""
            <div style='background-color: var(--success-color); color: white; padding: 0.5rem; border-radius: 5px; margin-top: 0.5em;'>
                ✅ {len(files)} file đã được tải lên thành công
            </div>
        """, unsafe_allow_html=True)
        
        # Option to use multiple document mode for RAG
        if len(files) > 1:
            use_multiple = st.checkbox(
                "Sử dụng chế độ nhiều tài liệu (RAG)", 
                value=True,
                help="Khi chọn, hệ thống sẽ phân tích và tạo câu hỏi dựa trên mối quan hệ giữa các tài liệu."
            )
        else:
            use_multiple = False
        
    st.markdown("""
        <div class="card fade-in">
            <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                🎯 Tùy Chọn Bài Trắc Nghiệm
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    num_questions = st.slider(
        "Số lượng câu hỏi:",
        min_value=1,
        max_value=20,
        value=5,
        help="Chọn số lượng câu hỏi cho bài trắc nghiệm"
    )
    
    difficulty_options = ["easy", "medium", "hard"]
    difficulty_labels = ["Dễ", "Trung bình", "Khó"]
    difficulty = st.select_slider(
        "Độ khó:",
        options=difficulty_options,
        value="medium",
        format_func=lambda x: difficulty_labels[difficulty_options.index(x)],
        help="Chọn mức độ khó cho các câu hỏi"
    )
    
    # Hiển thị thông tin model hiện tại
    current_model = get_current_model()
    if current_model:
        st.info(f"🤖 Đang sử dụng model: **{current_model}**. Bạn có thể thay đổi model trong trang Quản Lý Model.", icon="ℹ️")
        
    # Thêm system prompt UI - trước tiên thử lấy system prompt hiện tại
    current_system_prompt = ""
    try:
        current_system_prompt = get_system_prompt()
    except:
        # Nếu API không khả dụng, sử dụng prompt mặc định trống
        pass
        
    # Hiển thị component system prompt UI
    system_prompt = system_prompt_ui(default_prompt=current_system_prompt, key_prefix="quiz_gen")
    
    # Thêm nút để lưu system prompt toàn cục
    if st.button("💾 Lưu System Prompt Toàn Cục"):
        result = set_system_prompt(system_prompt)
        if result:
            st.success("✅ System prompt đã được lưu toàn cục")
        else:
            st.error("❌ Không thể lưu system prompt")

# Main content area
if st.button("🚀 Tạo Bài Trắc Nghiệm", type="primary"):
    if not files:
        st.error("⚠️ Vui lòng tải lên ít nhất một file PDF trước khi tạo bài trắc nghiệm.")
    else:
        # Biến để lưu trữ kết quả bên ngoài status block
        quiz_result = None
        elapsed_time = 0
        actual_questions = 0
        is_multi_document = False

        # Xử lý file và tạo bài trắc nghiệm
        with st.status("🔄 Đang tạo bài trắc nghiệm...", expanded=True) as status:
            status.update(label="🔄 Đang xử lý tài liệu...", state="running")
            try:
                start_time = time.time()
                is_multi_document = len(files) > 1 and 'use_multiple' in locals() and use_multiple

                # Thêm cập nhật tiến trình
                time.sleep(0.5)  # Tạm dừng ngắn để phản hồi trực quan
                if is_multi_document:
                    status.update(label=f"🔄 Đang phân tích {len(files)} tài liệu và tìm mối liên hệ...", state="running")
                else:
                    status.update(label="🔄 Đang phân tích nội dung...", state="running")
                    
                time.sleep(0.5)  # Tạm dừng ngắn để phản hồi trực quan
                status.update(label="🔄 Đang tạo câu hỏi... Có thể mất vài phút.", state="running")
                model_name = get_current_model()
                
                # Gọi API với cờ để sử dụng endpoint nhiều tài liệu nếu cần
                result = generate_quiz(
                    files=files,
                    num_questions=num_questions,
                    difficulty=difficulty,
                    model_name=model_name,
                    system_prompt=st.session_state.get('quiz_gen_system_prompt', ""),
                    use_multiple_endpoint=is_multi_document
                )
                
                elapsed_time = time.time() - start_time
                
                if is_multi_document:
                    status.update(label=f"✅ Hoàn thành trong {elapsed_time:.1f} giây! Đã tạo bài trắc nghiệm từ {len(files)} tài liệu.", state="complete", expanded=False)
                else:
                    status.update(label=f"✅ Hoàn thành trong {elapsed_time:.1f} giây!", state="complete", expanded=False)
                
                # Lưu trữ kết quả để sử dụng bên ngoài status block
                quiz_result = result
                quiz_text = quiz_result.get("result", "")
                
                # Trích xuất văn bản quiz và bảo vệ chống nội dung bị thiếu
                if not quiz_text.strip():
                    st.error("⚠️ Backend không trả về nội dung bài trắc nghiệm. Phản hồi đầy đủ:")
                    st.json(quiz_result)
                    st.stop()

                # Đếm câu hỏi - kiểm tra cả định dạng tiếng Anh và tiếng Việt
                english_questions = quiz_text.count("Question ")
                vietnamese_questions = quiz_text.count("Câu ")
                option_count = quiz_text.count("A. ")
                actual_questions = max(english_questions, vietnamese_questions)
                if actual_questions == 0 and option_count > 0:
                    actual_questions = option_count

            except Exception as e:
                status.update(label="❌ Lỗi", state="error", expanded=True)
                st.error(f"⚠️ Đã xảy ra lỗi: {str(e)}")
                st.error("Vui lòng thử lại hoặc điều chỉnh các tham số.")

        # Hiển thị kết quả chỉ khi chúng ta có quiz_text hợp lệ
        if quiz_result and 'quiz_text' in locals() and quiz_text:
            title_text = "📝 Bài Trắc Nghiệm"
            if is_multi_document:
                title_text += f" (Đa tài liệu - {len(files)} tài liệu)"
            title_text += f" ({actual_questions} câu hỏi)"
            
            st.markdown(f"""
                <div class="card fade-in">
                    <h2 style='color: var(--primary-color); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
                        {title_text}
                    </h2>
                </div>
            """, unsafe_allow_html=True)

            quiz_content = quiz_text
            questions = []
            current = ""

            lines = quiz_content.split('\n')
            for line in lines:
                if re.match(r'^Question\s+\d+', line.strip()) or line.strip().startswith("Câu "):
                    if current:
                        questions.append(current.strip())
                    current = line
                elif re.match(r'^[A-D]\.', line.strip()) and not current:
                    current = f"Câu {len(questions) + 1}:\n{line}"
                elif current:
                    current += "\n" + line

            if current:
                questions.append(current.strip())

            cleaned_questions = []
            for q in questions:
                if "Questions generated" in q or "generated:" in q or "📊" in q:
                    continue
                cleaned_questions.append(q)

            if cleaned_questions:
                for i, question in enumerate(cleaned_questions, 1):
                    st.markdown(f"""
                        <div style='background-color: #1e2130; padding: 15px; 
                             border-radius: 10px; border-left: 4px solid var(--primary-color); 
                             margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                            <h4 style='color: var(--primary-color); margin-top: 0;'>Câu Hỏi {i}</h4>
                            <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{question}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Không thể phân tích câu hỏi thành các phần riêng biệt. Hiển thị nội dung đầy đủ dưới đây:", icon="ℹ️")
                option_pattern = r'([A-D]\.\s.*?)(?=[A-D]\.\s|$)'
                option_parts = re.findall(option_pattern, quiz_text, re.DOTALL)
                if option_parts:
                    for i, part in enumerate(option_parts):
                        st.markdown(f"""
                            <div style='background-color: #1e2130; padding: 15px; 
                                border-radius: 10px; border-left: 4px solid var(--accent-color); 
                                margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                                <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{part.strip()}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='background-color: #1e2130; padding: 15px; 
                             border-radius: 10px; border-left: 4px solid var(--primary-color); 
                             margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                            <h4 style='color: var(--primary-color); margin-top: 0;'>Nội Dung Bài Trắc Nghiệm</h4>
                            <div style='font-size: 1.1em; white-space: pre-line; color: #e6e6e6;'>{quiz_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="card fade-in" style='margin-top: 1rem;'>
                    <p style='margin: 0; color: var(--text-primary);'>
                        <strong>⏱️ Thời Gian Thực Hiện:</strong> {elapsed_time:.2f} giây
                    </p>
                </div>
            """, unsafe_allow_html=True)

            download_label = "📥 Tải Xuống Bài Trắc Nghiệm"
            if is_multi_document:
                download_label = "📥 Tải Xuống Bài Trắc Nghiệm Đa Tài Liệu"
                
            st.download_button(
                label=download_label,
                data=quiz_text,
                file_name=f"bai_trac_nghiem_{num_questions}cau_{difficulty_labels[difficulty_options.index(difficulty)]}{'_da_tai_lieu' if is_multi_document else ''}.txt",
                mime="text/plain",
            )

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Được Hỗ Trợ Bởi Công Nghệ AI | Được Tạo Với ❤️</p>
    </div>
""", unsafe_allow_html=True)
