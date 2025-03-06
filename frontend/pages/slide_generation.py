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

st.title("Tri thức bảo an AI - Slide Generation")
st.write(
    "AI-powered presentation slide generation"
)

topic = st.text_input(
    "Enter your topic",
    placeholder="Enter the topic you want to create slides for..."
)

num_slides = st.number_input(
    "Number of slides",
    min_value=1,
    max_value=20,
    value=5
)

if st.button("Generate Slides"):
    if not topic:
        st.error("Please enter a topic first.")
    else:
        with st.status("Generating slides...", expanded=True) as status:
            try:
                start_time = time.time()
                result = generate_slides(topic, num_slides)
                status.update(label="Done!", state="complete", expanded=False)
                
                # Show success message
                st.success(f"Successfully generated {len(result['slides'])} slides!")
                
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
                            label="Download PowerPoint",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                            
                st.info(f"Time taken: {time.time() - start_time:.2f} seconds", icon="⏱️")
                
            except Exception as e:
                status.update(label="Error", state="error", expanded=False)
                st.error(f"An error occurred: {e}") 