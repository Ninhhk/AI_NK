import streamlit as st
import requests
import time
from typing import Optional

def analyze_document(
    file,
    query_type: str,
    user_query: Optional[str] = None,
    start_page: int = 0,
    end_page: int = -1,
) -> dict:
    """Send document to backend for analysis."""
    files = {"file": file}
    data = {
        "query_type": query_type,
        "start_page": str(start_page),
        "end_page": str(end_page),
    }
    
    if user_query:
        data["user_query"] = user_query
        
    response = requests.post(
        "http://localhost:8000/api/documents/analyze",
        files=files,
        data=data,
    )
    response.raise_for_status()
    return response.json()

st.title("Tri thức bảo an AI - Phân Tích Tài Liệu")
st.write(
    "Phân tích tài liệu bằng AI để xử lý thông tin hiệu quả"
)

with st.sidebar:
    st.header("Cài Đặt Tài Liệu")
    
    st.subheader("Tải Lên Tài Liệu")
    file = st.file_uploader("Tải lên tài liệu", type=["pdf"])
    if file:
        st.write("Tài liệu đã được tải lên thành công")

    st.subheader("Phạm Vi Trang")
    st.write(
        "Chọn phạm vi trang. Các trang được đánh số từ 0. Đối với trang cuối cùng, bạn cũng có thể sử dụng số âm để đếm từ cuối, ví dụ: -1 là trang cuối cùng, -2 là trang gần cuối, v.v."
    )
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input("Trang bắt đầu:", value=0, min_value=0)
    with col2:
        end_page = st.number_input("Trang kết thúc:", value=-1)

    st.subheader("Loại Phân Tích")
    query_type = st.radio("Chọn chức năng", ["summary", "qa"])

if query_type == "qa":
    user_query = st.text_area(
        "Câu hỏi của bạn", value="Dữ liệu nào được sử dụng trong phân tích này?"
    )

if st.button("Phân Tích"):
    result = None
    start = time.time()
    if file is None:
        st.error("Vui lòng tải lên tệp.")
    else:
        with st.status("Đang phân tích...", expanded=True) as status:
            try:
                result = analyze_document(
                    file=file,
                    query_type=query_type,
                    user_query=user_query if query_type == "qa" else None,
                    start_page=start_page,
                    end_page=end_page,
                )
                status.update(label="Hoàn thành!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Lỗi", state="error", expanded=False)
                st.error(f"Đã xảy ra lỗi: {e}")
                result = None

        if result:
            with st.container(border=True):
                st.header("Kết Quả")
                st.markdown(result["result"])
                st.info(f"Thời gian thực hiện: {time.time() - start:.2f} giây", icon="⏱️")