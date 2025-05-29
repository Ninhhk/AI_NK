import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from frontend.components.system_prompt import system_prompt_ui

# Set page config for better appearance
st.set_page_config(
    page_title="Tạo Slide AI",
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

def generate_slides(topic: str, num_slides: int, model_name: str = None, document_files=None, system_prompt: str = None) -> dict:
    """Gửi nội dung lên backend để tạo slide với nhiều tài liệu."""
    # Prepare files list for multi-file upload under 'documents'
    files = []
    if document_files:
        for f in document_files:
            files.append((
                "documents",
                (f.name, f.getvalue(), f.type)
            ))
    data = {
        "topic": topic, 
        "num_slides": num_slides
    }
    
    # Add model_name if specified
    if model_name:
        data["model_name"] = model_name
        
    # Add system_prompt if specified
    if system_prompt:
        data["system_prompt"] = system_prompt
        
    response = requests.post(
        "http://localhost:8000/api/slides/generate",
        files=files or None,
        data=data
    )
    response.raise_for_status()
    return response.json()

def get_available_models() -> list:
    """Lấy danh sách các model có sẵn từ backend."""
    try:
        response = requests.get("http://localhost:8000/api/ollama/models")
        response.raise_for_status()
        return response.json().get("models", [])
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []
    
def get_current_model() -> str:
    """Lấy model hiện tại được sử dụng để tạo slide."""
    try:
        response = requests.get("http://localhost:8000/api/slides/current-model")
        response.raise_for_status()
        return response.json().get("model_name", "")
    except Exception as e:
        print(f"Error fetching current model: {e}")
        return ""

def get_system_prompt() -> str:
    """Lấy system prompt hiện tại cho tạo slide."""
    try:
        response = requests.get("http://localhost:8000/api/slides/system-prompt")
        response.raise_for_status()
        return response.json().get("system_prompt", "")
    except Exception as e:
        print(f"Error fetching system prompt: {e}")
        return ""

def set_system_prompt(prompt: str) -> bool:
    """Đặt system prompt cho tạo slide."""
    try:
        response = requests.post(
            "http://localhost:8000/api/slides/system-prompt",
            data={"system_prompt": prompt}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error setting system prompt: {e}")
        return False

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

# Get available models for dropdown
available_models = get_available_models()
current_model = get_current_model()

# Model selection
with st.expander("🤖 Lựa Chọn Model AI", expanded=False):
    st.markdown("""
        Chọn model AI nào để sử dụng cho tất cả các tính năng của ứng dụng bao gồm tạo slide, phân tích tài liệu và tạo quiz.
        Mọi thay đổi tại đây sẽ áp dụng cho toàn bộ ứng dụng.
        Bạn có thể quản lý các model trong trang Quản Lý Model.
    """)
    
    # Create a list of model names for the dropdown
    model_names = [model.get('name') for model in available_models]
      # Only show dropdown if there are models available
    if model_names:
        selected_model = st.selectbox(
            "Chọn Model AI Toàn Cục",
            options=model_names,
            index=model_names.index(current_model) if current_model in model_names else 0,
            help="Chọn model AI để sử dụng cho tất cả tính năng (sẽ được áp dụng toàn cục)"
        )
        st.info(f"Đang sử dụng model: {selected_model} cho tất cả tính năng bao gồm phân tích tài liệu và tạo quiz")
    else:
        st.warning("Không có model nào khả dụng. Vui lòng truy cập trang Quản Lý Model để thêm model.")
        selected_model = None

# Input section with better layout
col1, col2 = st.columns([2,1])

with col1:
    topic = st.text_input(
        "📝 Chủ Đề Của Bạn",
        placeholder="Nhập chủ đề bạn muốn tạo slide...",
        help="Nhập chủ đề rõ ràng để AI tạo slide phù hợp"
    )

with col2:
    num_slides = st.number_input(
        "📊 Số Lượng Slide",
        min_value=1,
        max_value=20,
        value=5,
        help="Chọn số lượng slide bạn muốn tạo (tối đa 20 slide)"
    )

# System prompt section
with st.expander("💬 Cài Đặt System Prompt", expanded=False):
    # Get current system prompt
    current_system_prompt = get_system_prompt()
    
    # Add tabs for different sections
    prompt_tab, examples_tab, help_tab = st.tabs(["Chỉnh Sửa Prompt", "Prompt Mẫu", "Trợ Giúp"])
    with prompt_tab:
        # Use the reusable system prompt UI component
        custom_system_prompt = system_prompt_ui(default_prompt=current_system_prompt, key_prefix="slide_gen")
          # Save button for system prompt
        if st.button("💾 Lưu System Prompt"):
            if set_system_prompt(custom_system_prompt):
                st.success("✅ System prompt đã được lưu thành công!")
            else:
                st.error("❌ Không thể lưu system prompt. Vui lòng thử lại.")
                  # Use in current session only
        if 'use_custom_prompt' not in st.session_state:
            st.session_state['use_custom_prompt'] = False
            
        st.session_state['use_custom_prompt'] = st.checkbox(
            "Sử dụng prompt tùy chỉnh chỉ cho phiên này (không lưu)",
            value=st.session_state['use_custom_prompt'],
            key="slide_gen_use_custom_prompt",
            help="Áp dụng prompt tùy chỉnh chỉ cho phiên này mà không lưu làm mặc định"
        )
    with examples_tab:
        st.markdown("### Prompt Mẫu")
        st.markdown("Nhấp vào bất kỳ ví dụ nào để sử dụng nó:")
        
        # Technical presentation example
        if st.button("Bài Thuyết Trình Kỹ Thuật"):
            example_prompt = """Bạn là chuyên gia thuyết trình kỹ thuật. Tạo slide với nội dung chính xác, kỹ thuật. 
Sử dụng ngôn ngữ trang trọng, bao gồm thuật ngữ kỹ thuật phù hợp, và tổ chức thông tin phức tạp 
theo thứ bậc. Mỗi slide nên tập trung vào một khái niệm kỹ thuật duy nhất với chi tiết hỗ trợ.
Giới hạn mỗi slide tối đa 5 điểm chính, mỗi điểm có 7-10 từ."""
            st.session_state['custom_system_prompt'] = example_prompt
        st.rerun()
        
        # Educational presentation example
        if st.button("Bài Thuyết Trình Giáo Dục"):
            example_prompt = """Bạn là chuyên gia giáo dục tạo slide cho học sinh. Trình bày thông tin một cách 
rõ ràng, hấp dẫn với lời giải thích đơn giản về các khái niệm phức tạp. Bao gồm câu hỏi 
gợi suy nghĩ trong một số slide, và tổ chức nội dung theo trình tự học tập logic từ 
cơ bản đến nâng cao. Sử dụng ngôn ngữ thân thiện, dễ tiếp cận."""
            st.session_state['custom_system_prompt'] = example_prompt
        st.rerun()
        
        # Business presentation example
        if st.button("Bài Thuyết Trình Kinh Doanh"):
            example_prompt = """Bạn là chuyên gia thuyết trình kinh doanh tập trung vào slide thuyết phục, hướng hành động.
Tạo nội dung làm nổi bật các chỉ số kinh doanh chính, thông tin chiến lược, và 
khuyến nghị rõ ràng. Sử dụng ngôn ngữ chuyên nghiệp, nhấn mạnh lợi ích và tác động, và 
đảm bảo mỗi slide đóng góp vào câu chuyện kinh doanh thuyết phục. Bao gồm lời kêu gọi 
hành động rõ ràng trong kết luận."""
            st.session_state['custom_system_prompt'] = example_prompt
        st.rerun()
    
    with help_tab:
        st.markdown("### Mẹo Viết System Prompt Hiệu Quả")
        st.markdown("""
        1. **Cụ thể về định dạng**: Đề cập số điểm chính mỗi slide hoặc số từ mỗi điểm
        2. **Xác định đối tượng**: Nêu rõ bài thuyết trình dành cho ai
        3. **Đặt giọng điệu**: Chỉ ra bạn muốn ngôn ngữ trang trọng, thân thiện, kỹ thuật, hay đơn giản
        4. **Hướng dẫn cấu trúc**: Gợi ý cách tổ chức thông tin
        5. **Bao gồm chuyên môn**: Thêm quy tắc cụ thể phù hợp với chủ đề của bạn
        
        Để được hướng dẫn chi tiết hơn, xem [Hướng Dẫn System Prompt](https://github.com/your-username/AI_NVCB/blob/main/docs/system_prompt_guide.md).
        """)

# Reference document upload section supporting multiple files
st.markdown("""
    <div class="card fade-in">
        <h3 style='color: var(--text-secondary); margin-top: 0; display: flex; align-items: center; gap: 0.5em;'>
            📄 Tài Liệu Tham Khảo (tùy chọn)
        </h3>
    </div>
""", unsafe_allow_html=True)
document_files = st.file_uploader(
    "Tải lên một hoặc nhiều tài liệu để AI tham khảo",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Tải lên tài liệu để AI tham khảo khi tạo slide. Hỗ trợ PDF, DOCX và TXT"
)
if document_files:
    for doc in document_files:
        st.success(f"Đã tải lên: {doc.name}")

# Generate button with custom styling
if st.button("🚀 Tạo Slide", type="primary"):
    if not topic:
        st.error("⚠️ Vui lòng nhập chủ đề trước.")
    else:
        with st.status("🔄 Đang tạo slide...", expanded=True) as status:
            try:
                start_time = time.time()
                # Include selected model in the generation request
                result = generate_slides(
                    topic=topic, 
                    num_slides=num_slides, 
                    model_name=selected_model if 'selected_model' in locals() else None,
                    document_files=document_files,
                    system_prompt=st.session_state.get('slide_gen_system_prompt') if st.session_state.get('use_custom_prompt', False) else None
                )
                
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
                        label="📥 Tải Xuống PowerPoint",
                        data=file_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Performance metrics with better styling
                    st.markdown(f"""
                        <div class="card fade-in" style='margin-top: 1rem;'>
                            <p style='margin: 0; color: var(--text-primary);'>
                                <strong>⏱️ Thời Gian Thực Hiện:</strong> {time.time() - start_time:.2f} giây
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    status.update(label="⚠️ Slide đã được tạo nhưng tên file có thể quá dài để hiển thị, tìm file trong /output/slides", state="error", expanded=False)
                    st.error(f"⚠️ Không thể tìm thấy file {filename} do tên file quá dài. Vui lòng tìm file trong /output/slides.")
                
            except Exception as e:
                status.update(label="❌ Lỗi", state="error", expanded=False)
                st.error(f"⚠️ Đã xảy ra lỗi: {e}")

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Được Hỗ Trợ Bởi Công Nghệ AI | Được Tạo Với ❤️</p>
    </div>
""", unsafe_allow_html=True)
