import streamlit as st
import requests
import json
import time
import os
from datetime import datetime

def generate_slides(topic: str, num_slides: int) -> dict:
    """Send content to backend for slide generation."""
    response = requests.post(
        "http://localhost:8000/api/slides/generate",
        json={"topic": topic, "num_slides": num_slides}
    )
    response.raise_for_status()
    return response.json()

st.title("Tri thức bảo an AI - Tạo Slide")
st.write(
    "Tạo slide thuyết trình bằng AI"
)

topic = st.text_input(
    "Nhập chủ đề của bạn",
    placeholder="Nhập chủ đề bạn muốn tạo slide cho..."
)

num_slides = st.number_input(
    "Số lượng slide",
    min_value=1,
    max_value=20,
    value=5
)

if st.button("Tạo Slide"):
    if not topic:
        st.error("Vui lòng nhập chủ đề trước.")
    else:
        with st.status("Đang tạo slide...", expanded=True) as status:
            try:
                start_time = time.time()
                result = generate_slides(topic, num_slides)
                status.update(label="Hoàn thành!", state="complete", expanded=False)
                
                # Show success message
                st.success(f"Đã tạo thành công {len(result['slides'])} slide!")
                
                # Generate filename based on topic and timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_topic = safe_topic.replace(' ', '_')
                filename = f"{safe_topic}_{timestamp}.pptx"
                
                # Get the output directory path
                output_dir = os.path.join("output", "slides")
                pptx_path = os.path.join(output_dir, filename)
                
                # Download PowerPoint if file exists
                if os.path.exists(pptx_path):
                    with open(pptx_path, "rb") as f:
                        st.download_button(
                            label="Tải PowerPoint",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                            
                st.info(f"Thời gian thực hiện: {time.time() - start_time:.2f} giây", icon="⏱️")
                
            except Exception as e:
                status.update(label="Lỗi", state="error", expanded=False)
                st.error(f"Đã xảy ra lỗi: {e}")