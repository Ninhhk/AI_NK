import streamlit as st
import requests
import json
import time
import os
from io import BytesIO
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from frontend.components.system_prompt import system_prompt_ui

# Set page config for better appearance
st.set_page_config(
    page_title="Quản Lý Model AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('frontend/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)       

# Add custom styles for model management
st.markdown("""
    <style>
    .model-card {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    .model-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
    }
    .model-progress {
        background-color: var(--primary-color-light);
        border-radius: 5px;
        height: 12px;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    .model-progress-inner {
        background: linear-gradient(to right, var(--primary-color), var(--accent-color));
        height: 100%;
        transition: width 0.3s ease;
    }
    .model-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .model-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .model-header {
        display: flex;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoints
OLLAMA_API_URL = "http://localhost:8000/api/ollama"
SLIDES_API_URL = "http://localhost:8000/api/slides"

def get_models():
    """Lấy tất cả models có sẵn từ API"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/models")
        response.raise_for_status()
        return response.json()["models"]
    except Exception as e:
        st.error(f"Lỗi khi lấy models: {e}")
        return []

def get_current_model():
    """Lấy model đang hoạt động hiện tại cho việc tạo slide"""
    try:
        response = requests.get(f"{SLIDES_API_URL}/current-model")
        response.raise_for_status()
        return response.json()["model_name"]
    except Exception as e:
        st.error(f"Lỗi khi lấy model hiện tại: {e}")
        return None

def set_model(model_name):
    """Đặt model cho việc tạo slide"""
    try:
        response = requests.post(
            f"{SLIDES_API_URL}/set-model",
            data={"model_name": model_name}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Lỗi khi đặt model: {e}")
        return None

def pull_model(model_name):
    """Bắt đầu tải model từ Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/models/pull",
            data={"model_name": model_name}
        )
        response.raise_for_status()
        return model_name  # Trả về tên model làm task ID
    except Exception as e:
        st.error(f"Lỗi khi tải model: {e}")
        return None

def get_download_progress(task_id):
    """Lấy tiến trình tải xuống cho một task cụ thể"""
    try:
        # Trong phiên bản đơn giản, chúng ta không theo dõi tiến trình
        # Nên chúng ta sẽ chỉ trả về một object giả
        return {"done": True, "pull_progress": 1000, "error": None}
    except Exception as e:
        return {"done": False, "pull_progress": 0, "error": str(e)}

def get_all_progress():
    """Lấy tất cả tiến trình tải xuống"""
    try:
        # Trong phiên bản đơn giản, chúng ta không theo dõi tiến trình
        return {}
    except Exception as e:
        return {}

def cancel_model_pull(task_id):
    """Hủy việc tải model"""
    # Trong phiên bản đơn giản, chúng ta không hỗ trợ hủy
    return True

def delete_model(model_name):
    """Xóa một model"""
    try:
        response = requests.delete(f"{OLLAMA_API_URL}/models/{model_name}") 
        response.raise_for_status()
        return response.json()["success"]
    except Exception as e:
        st.error(f"Lỗi khi xóa model: {e}")
        return False

def upload_model(file, model_name=None):
    """Tải lên file model"""
    # Trong phiên bản đơn giản, chúng ta không hỗ trợ tải lên file
    st.warning("Tải lên file model không được hỗ trợ trong phiên bản này")      
    return False

def get_system_prompt():
    """Lấy system prompt hiện tại."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/system-prompt")
        response.raise_for_status()
        return response.json()["system_prompt"]
    except Exception as e:
        st.error(f"Lỗi khi lấy system prompt: {e}")
        return ""

def set_system_prompt(prompt):
    """Đặt system prompt."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/system-prompt",
            data={"system_prompt": prompt}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Lỗi khi đặt system prompt: {e}")
        return None

# Header section with animated logo and title
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div class="fade-in">
            <h1 style='text-align: center; color: var(--primary-color); font-size: 2.5em; margin-bottom: 0.5em;'>
                🤖 Quản Lý Model
            </h1>
            <h3 style='text-align: center; color: var(--text-secondary); font-size: 1.2em;'>
                Quản Lý Các Model AI Cho Tất Cả Tính Năng Ứng Dụng
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Main content area with animated separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
""", unsafe_allow_html=True)

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Models Có Sẵn", "Thêm Model Mới", "System Prompt", "Đang Tải Xuống"])

with tab1:
    # Lấy model hiện tại
    current_model = get_current_model()
      # Nút làm mới
    if st.button("🔄 Làm Mới Models", type="primary"):
        st.rerun()
    
    # Lấy models
    models = get_models()
    
    if not models:
        st.info("Không có models nào có sẵn. Thêm models trong tab 'Thêm Model Mới'.")
    else:
        st.markdown(f"### Models Có Sẵn ({len(models)})")
        st.markdown("Chọn một model để sử dụng cho tất cả tính năng (tạo slide, phân tích tài liệu và tạo quiz)")
        
        # Hiển thị thông báo toàn cục về model hiện tại
        if current_model:
            st.info(f"🔄 **Model Đang Hoạt động: {current_model}** - Model này hiện đang được sử dụng cho tất cả tính năng ứng dụng.", icon="ℹ️")
        
        for model in models:
            with st.container():
                st.markdown(f"""
                <div class="model-card">
                    <div class="model-header">
                        <div class="model-icon">🧠</div>
                        <div>
                            <h3 style="margin: 0;">{model['name']}</h3>     
                            <p style="margin: 0; color: var(--text-secondary);">
                                Kích thước: {model['size'] / (1024*1024):.1f} MB | Sửa đổi: {model['modified_at']}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Các nút hành động trong cột
                col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
                with col1:
                    if st.button(f"Chọn", key=f"select_{model['name']}"):
                        result = set_model(model['name'])
                        if result:
                            st.success(f"Model đã được thay đổi thành {model['name']} và sẽ được sử dụng cho tất cả tính năng")
                            time.sleep(1)
                            st.rerun()
                
                with col2:
                    if st.button(f"Thông tin", key=f"info_{model['name']}"):
                        st.json(model['details'] if 'details' in model else model)
                with col3:
                    if st.button(f"Xóa", key=f"delete_{model['name']}"):
                        if model['name'] == current_model:
                            st.error("Không thể xóa model đang hoạt động")
                        else:
                            if delete_model(model['name']):
                                st.success(f"Model {model['name']} đã được xóa")
                                time.sleep(1)
                                st.rerun()
                
                with col4:
                    if model['name'] == current_model:
                        st.success("✅ Model toàn cục hiện tại")

with tab2:
    st.markdown("### Thêm Model Mới")
    
    # Phần tải model
    with st.expander("Tải Model từ Ollama", expanded=True):
        st.markdown("""
        Nhập tên của một model Ollama để tải xuống. Ví dụ:
        - `llama3:8b`
        - `gemma3:1b`
        - `mistral:latest`
        """)
        
        with st.form("pull_model_form"):
            model_name = st.text_input("Tên Model", placeholder="ví dụ: llama3:8b")
            submitted = st.form_submit_button("Bắt Đầu Tải Xuống")
            if submitted and model_name:
                task_id = pull_model(model_name)
                if task_id:
                    st.success(f"Đã bắt đầu tải xuống {model_name}")
                    time.sleep(1)
                    st.rerun()
    
    # Phần tải lên model
    with st.expander("Tải Lên File Model GGUF", expanded=False):
        st.markdown("""
        Tải lên trực tiếp file model GGUF. File này sẽ được thêm vào Ollama.
        """)
        
        with st.form("upload_model_form"):
            uploaded_file = st.file_uploader("Chọn file GGUF", type=["gguf"])
            custom_name = st.text_input("Tên Model Tùy Chỉnh (tùy chọn)")
            upload_submitted = st.form_submit_button("Tải Lên Model")
            
            if upload_submitted and uploaded_file:
                success = upload_model(uploaded_file, custom_name if custom_name else None)
                if success:
                    st.success(f"Model đã được tải lên thành công")
                    time.sleep(1)
                    st.experimental_rerun()

with tab3:
    st.markdown("### System Prompt Toàn Cục")
    st.markdown("""
    <div class="card fade-in">
        <p>
            System prompt được sử dụng cho tất cả tính năng của ứng dụng để kiểm soát cách AI phản hồi. 
            Đây là cài đặt toàn cục ảnh hưởng đến việc tạo slide, phân tích tài liệu và tất cả tương tác AI khác.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Trước tiên lấy system prompt hiện tại từ API
    current_system_prompt = ""
    try:
        current_system_prompt = get_system_prompt()
    except:
        # Nếu API không khả dụng, sử dụng prompt mặc định trống
        pass
        
    # Hiển thị component system prompt UI
    system_prompt = system_prompt_ui(default_prompt=current_system_prompt, key_prefix="model_management")
    
    # Thêm nút để lưu system prompt toàn cục
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Lưu System Prompt Toàn Cục", type="primary"):
            result = set_system_prompt(system_prompt)
            if result:
                st.success("✅ System prompt đã được lưu toàn cục và sẽ được sử dụng cho tất cả tính năng")
            else:
                st.error("❌ Không thể lưu system prompt")
    
    with col2:
        st.warning("Điều này sẽ cập nhật system prompt cho **tất cả tính năng** của ứng dụng.")
    
    # Thêm nút để chạy script set_system_prompt.py
    st.markdown("---")
    st.markdown("### Đặt Lại Thành Prompt Tiếng Việt")
    
    if st.button("🔄 Đặt Lại Thành Prompt Tiếng Việt"):
        try:
            vietnamese_prompt = "\\no_think must answer in vietnamese, phải trả lời bằng tiếng việt"
            result = set_system_prompt(vietnamese_prompt)
            if result:
                st.success("✅ System prompt đã được đặt lại thành yêu cầu phản hồi tiếng Việt")
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("❌ Không thể đặt lại system prompt")
        except Exception as e:
            st.error(f"Lỗi khi đặt lại system prompt: {e}")

with tab4:
    st.markdown("### Đang Tải Xuống")
    
    # Tự động làm mới cho tiến trình tải xuống
    auto_refresh = st.checkbox("Tự động làm mới (mỗi 2 giây)", value=True)
    
    # Lấy tất cả tiến trình tải xuống
    download_progress = get_all_progress()
    
    if not download_progress:
        st.info("Không có tải xuống nào đang hoạt động. Bắt đầu tải xuống trong tab 'Thêm Model Mới'.")
    else:
        for model_name, progress in download_progress.items():
            with st.container():
                # Tính toán phần trăm để hiển thị
                percentage = progress.get("pull_progress", 0) / 10 if progress.get("pull_progress") is not None else 0
                
                st.markdown(f"""
                <div class="model-card">
                    <h3>{model_name}</h3>
                    <p>Trạng thái: {"Hoàn thành" if progress.get("done", False) else "Đang tải xuống..."}</p>
                    <div class="model-progress">
                        <div class="model-progress-inner" style="width: {percentage}%;"></div>
                    </div>
                    <p>{percentage:.1f}% hoàn thành</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Nút hủy
                if not progress.get("done", False):
                    if st.button(f"Hủy", key=f"cancel_{model_name}"):
                        if cancel_model_pull(model_name):
                            st.success(f"Đã hủy tải xuống {model_name}")
                            time.sleep(1)
                            st.experimental_rerun()
    
    # Logic tự động làm mới
    if auto_refresh and download_progress:
        time.sleep(2)
        st.experimental_rerun()

# Footer with gradient separator
st.markdown("""
    <div style='height: 2px; background: linear-gradient(90deg, transparent, var(--primary-color), transparent);'></div>
    <div class="footer fade-in">
        <p style='margin: 0.5em 0;'>Được Hỗ Trợ Bởi Ollama | Được Tạo Với ❤️</p>
    </div>
""", unsafe_allow_html=True)
