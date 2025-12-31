# CHƯƠNG 3: CÔNG NGHỆ SỬ DỤNG

## Mở đầu chương

Chương này trình bày các công nghệ và nền tảng được sử dụng trong quá trình phát triển hệ thống AI NVCB. Mỗi công nghệ được lựa chọn đều nhằm giải quyết các yêu cầu cụ thể đã được xác định tại Chương 2, bao gồm: (i) xử lý ngôn ngữ tự nhiên và mô hình ngôn ngữ lớn (LLM), (ii) xây dựng backend API hiệu năng cao, (iii) phát triển giao diện người dùng thân thiện, (iv) lưu trữ và truy vấn vector cho RAG, và (v) tạo file PowerPoint tự động. Với mỗi công nghệ, sinh viên sẽ phân tích các lựa chọn thay thế và giải thích lý do lựa chọn.

---

## 3.1 Kiến trúc tổng quan hệ thống

Hệ thống AI NVCB được xây dựng theo kiến trúc phân lớp (Layered Architecture) kết hợp với kiến trúc microservices, bao gồm ba tầng chính: tầng trình bày (Presentation Layer), tầng nghiệp vụ (Business Logic Layer), và tầng dữ liệu (Data Layer). Kiến trúc này đáp ứng yêu cầu phi chức năng NFR18 về tính dễ bảo trì đã nêu tại mục 2.4.5.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TẦNG TRÌNH BÀY (Frontend)                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Streamlit Web Application                    │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │   │
│  │  │  Document   │ │    Slide    │ │    Quiz     │ │   Model    │ │   │
│  │  │  Analysis   │ │  Generation │ │  Generation │ │ Management │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      TẦNG NGHIỆP VỤ (Backend API)                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      FastAPI Application                         │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │   │
│  │  │  Document   │ │    Slide    │ │    Model    │ │   Health   │ │   │
│  │  │   Routes    │ │   Routes    │ │   Routes    │ │   Routes   │ │   │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────────────┘ │   │
│  │         │               │               │                        │   │
│  │  ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐               │   │
│  │  │  Document   │ │    Slide    │ │    Model    │               │   │
│  │  │   Service   │ │   Service   │ │   Manager   │               │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         TẦNG DỮ LIỆU VÀ AI                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │   LangChain  │  │    FAISS     │  │    Ollama    │  │   SQLite   │  │
│  │  Framework   │  │ Vector Store │  │  LLM Server  │  │  Database  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

Kiến trúc này mang lại nhiều lợi ích: (i) tách biệt rõ ràng các thành phần giúp dễ dàng bảo trì và mở rộng, (ii) cho phép thay đổi công nghệ ở một tầng mà không ảnh hưởng đến các tầng khác, và (iii) hỗ trợ triển khai độc lập các thành phần thông qua Docker container.

---

## 3.2 Công nghệ xử lý ngôn ngữ tự nhiên và LLM

### 3.2.1 Vấn đề cần giải quyết

Theo yêu cầu tại Chương 2, hệ thống cần thực hiện các tác vụ xử lý ngôn ngữ tự nhiên phức tạp bao gồm: (i) tóm tắt tài liệu tự động (UC01.2), (ii) hỏi đáp dựa trên ngữ cảnh tài liệu - RAG (UC01.3), (iii) sinh nội dung slide từ chủ đề hoặc tài liệu (UC02), và (iv) tạo câu hỏi trắc nghiệm tự động (UC03). Đây là các tác vụ đòi hỏi khả năng hiểu và sinh ngôn ngữ tự nhiên ở mức độ cao.

### 3.2.2 Các lựa chọn công nghệ

| Công nghệ | Mô tả | Ưu điểm | Nhược điểm |
|-----------|-------|---------|------------|
| **OpenAI GPT API** | API từ OpenAI | Chất lượng cao, dễ tích hợp | Chi phí cao, phụ thuộc internet, dữ liệu gửi lên cloud |
| **Google Gemini API** | API từ Google | Đa phương thức, tích hợp Google | Phụ thuộc cloud, chi phí theo usage |
| **Hugging Face Transformers** | Thư viện mã nguồn mở | Miễn phí, nhiều model | Yêu cầu GPU mạnh, cấu hình phức tạp |
| **Ollama + LangChain** | LLM server local + Framework orchestration | Miễn phí, chạy offline, bảo mật cao | Yêu cầu phần cứng, hiệu năng phụ thuộc model |

### 3.2.3 Lựa chọn: Ollama kết hợp LangChain

Hệ thống AI NVCB lựa chọn sử dụng **Ollama** làm LLM server và **LangChain** làm framework điều phối (orchestration) vì các lý do sau:

**Ollama** [1] là một nền tảng mã nguồn mở cho phép chạy các mô hình ngôn ngữ lớn (LLM) trực tiếp trên máy tính cá nhân. Ollama đóng gói model weights, cấu hình và dữ liệu vào một đơn vị duy nhất được định nghĩa trong Modelfile, giúp việc cài đặt và chạy model trở nên đơn giản. Một số đặc điểm nổi bật của Ollama bao gồm:

Thứ nhất, Ollama hỗ trợ triển khai on-premise, đáp ứng yêu cầu NFR14 về bảo mật dữ liệu. Toàn bộ quá trình xử lý diễn ra trên máy chủ nội bộ, không có dữ liệu nào được gửi ra ngoài. Điều này đặc biệt quan trọng khi người dùng làm việc với tài liệu nhạy cảm.

Thứ hai, Ollama cung cấp API tương thích với chuẩn OpenAI, cho phép dễ dàng tích hợp với các framework như LangChain. API endpoint mặc định tại `http://localhost:11434` cung cấp các endpoint `/api/generate`, `/api/chat`, và `/api/embeddings`.

Thứ ba, Ollama hỗ trợ nhiều model LLM phổ biến như Llama 2, Llama 3, Mistral, Gemma, Phi-3, và Qwen2.5. Người dùng có thể linh hoạt chọn model phù hợp với yêu cầu về chất lượng và tài nguyên phần cứng, đáp ứng yêu cầu UC04 về quản lý model AI.

**LangChain** [2] là một framework mã nguồn mở được thiết kế để xây dựng các ứng dụng sử dụng LLM. Framework này cung cấp các abstraction và component giúp đơn giản hóa việc phát triển ứng dụng AI phức tạp:

Về mặt kiến trúc, LangChain được tổ chức thành các module chính: (i) Models - giao tiếp với các LLM, (ii) Prompts - quản lý và tối ưu prompt templates, (iii) Chains - kết nối nhiều component thành pipeline xử lý, (iv) Memory - lưu trữ ngữ cảnh hội thoại, và (v) Retrieval - tích hợp với vector stores cho RAG.

Đối với tính năng RAG (Retrieval-Augmented Generation) phục vụ use case UC01.3, LangChain cung cấp pipeline hoàn chỉnh bao gồm: document loaders để đọc nhiều định dạng file, text splitters để chia nhỏ văn bản, embeddings để chuyển đổi text thành vector, và retrievers để tìm kiếm ngữ cảnh liên quan.

```python
# Ví dụ sử dụng LangChain với Ollama trong hệ thống
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = Ollama(model="qwen3:8b", base_url="http://localhost:11434")
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="Dựa trên ngữ cảnh: {context}\nTrả lời câu hỏi: {question}"
)
chain = LLMChain(llm=llm, prompt=prompt)
```

---

## 3.3 Công nghệ Backend API

### 3.3.1 Vấn đề cần giải quyết

Hệ thống cần một backend API có khả năng: (i) xử lý các request HTTP từ frontend một cách hiệu quả, (ii) hỗ trợ upload file đa định dạng, (iii) xử lý bất đồng bộ (async) cho các tác vụ AI tốn thời gian, và (iv) cung cấp tài liệu API tự động. Các yêu cầu này liên quan đến NFR01-03 về hiệu năng và NFR06-07 về độ tin cậy.

### 3.3.2 Các lựa chọn công nghệ

| Framework | Ngôn ngữ | Ưu điểm | Nhược điểm |
|-----------|----------|---------|------------|
| **Django** | Python | Full-featured, ORM mạnh, cộng đồng lớn | Nặng, learning curve cao, không tối ưu cho API |
| **Flask** | Python | Nhẹ, linh hoạt, dễ học | Không có async native, thiếu validation tự động |
| **Express.js** | Node.js | Nhanh, ecosystem lớn | Không phù hợp với AI/ML Python ecosystem |
| **FastAPI** | Python | Async native, tự động gen docs, validation mạnh | Còn mới, cộng đồng nhỏ hơn Django |

### 3.3.3 Lựa chọn: FastAPI

**FastAPI** [3] được lựa chọn làm framework backend chính vì các ưu điểm sau:

FastAPI là một web framework hiện đại, hiệu năng cao cho Python, được xây dựng trên nền tảng Starlette (cho web) và Pydantic (cho data validation). Theo benchmark chính thức, FastAPI là một trong những framework Python nhanh nhất, tương đương với NodeJS và Go.

Về hỗ trợ async/await, FastAPI được thiết kế với async-first approach, cho phép xử lý nhiều request đồng thời mà không block thread. Điều này đặc biệt quan trọng khi tích hợp với LLM vì các tác vụ AI thường có latency cao (10-60 giây theo NFR01-03).

```python
# Ví dụ endpoint async trong FastAPI
@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query_type: str = Form(...),
    model_name: Optional[str] = Form(None)
) -> Dict[str, Any]:
    content = await file.read()
    result = await document_service.analyze(content, query_type)
    return {"status": "success", "result": result}
```

Về tính năng tự động sinh tài liệu API, FastAPI tự động tạo OpenAPI (Swagger) documentation từ type hints và Pydantic models. Giao diện Swagger UI tại `/docs` cho phép developers và testers dễ dàng kiểm thử API mà không cần công cụ bên ngoài.

Về data validation, FastAPI sử dụng Pydantic để validate dữ liệu đầu vào tự động dựa trên type annotations. Khi dữ liệu không hợp lệ, hệ thống trả về response lỗi chi tiết với HTTP status code 422, giúp frontend dễ dàng xử lý và hiển thị thông báo cho người dùng.

---

## 3.4 Công nghệ Frontend

### 3.4.1 Vấn đề cần giải quyết

Giao diện người dùng cần đáp ứng các yêu cầu: (i) thân thiện và dễ sử dụng (NFR10), (ii) hỗ trợ tiếng Việt hoàn toàn (NFR11), (iii) hiển thị trạng thái xử lý realtime (NFR12), và (iv) có thể phát triển nhanh để tập trung vào logic nghiệp vụ.

### 3.4.2 Các lựa chọn công nghệ

| Công nghệ | Loại | Ưu điểm | Nhược điểm |
|-----------|------|---------|------------|
| **React** | SPA Framework | Linh hoạt, ecosystem lớn, hiệu năng tốt | Learning curve cao, cần build pipeline phức tạp |
| **Vue.js** | SPA Framework | Dễ học, documentation tốt | Cộng đồng nhỏ hơn React |
| **Gradio** | Python UI | Dành cho ML/AI, dễ dùng | Giới hạn tùy chỉnh giao diện |
| **Streamlit** | Python UI | Rapid prototyping, code Python thuần, tích hợp data science | Hiệu năng thấp hơn SPA, giới hạn layout |

### 3.4.3 Lựa chọn: Streamlit

**Streamlit** [4] được lựa chọn làm framework frontend vì các lý do sau:

Streamlit là một framework mã nguồn mở cho phép xây dựng ứng dụng web data science và machine learning chỉ với Python. Điểm mạnh của Streamlit nằm ở khả năng rapid development - từ ý tưởng đến prototype chỉ trong vài giờ thay vì vài ngày.

Về mô hình lập trình, Streamlit sử dụng declarative paradigm - developers khai báo UI elements và Streamlit tự động handle re-rendering khi state thay đổi. Script Python được chạy từ đầu đến cuối mỗi khi có interaction, với cơ chế caching thông minh để tối ưu hiệu năng.

```python
# Ví dụ code Streamlit trong hệ thống
import streamlit as st

st.set_page_config(page_title="Phân Tích Tài Liệu AI", page_icon="📄")
st.title("📄 Phân Tích Tài Liệu AI")

uploaded_file = st.file_uploader("Tải tài liệu", type=["pdf", "docx", "txt"])
if uploaded_file:
    with st.spinner("Đang phân tích..."):
        result = analyze_document(uploaded_file)
    st.success("Phân tích hoàn tất!")
    st.write(result)
```

Về tích hợp với Python ecosystem, Streamlit tích hợp seamless với các thư viện Python phổ biến như Pandas, NumPy, Matplotlib, và đặc biệt là các thư viện AI/ML. Điều này cho phép tận dụng toàn bộ code Python đã viết cho backend.

Về hỗ trợ realtime updates, Streamlit cung cấp các widget như `st.spinner()`, `st.progress()`, và `st.status()` để hiển thị trạng thái xử lý, đáp ứng yêu cầu NFR12. Session state cho phép lưu trữ dữ liệu giữa các lần rerun, hỗ trợ tính năng lịch sử hội thoại (UC01.4).

---

## 3.5 Công nghệ Vector Database và Embeddings

### 3.5.1 Vấn đề cần giải quyết

Tính năng RAG (Retrieval-Augmented Generation) trong use case UC01.3 yêu cầu: (i) chuyển đổi văn bản thành vector (embeddings), (ii) lưu trữ và index vector hiệu quả, và (iii) tìm kiếm semantic similarity nhanh chóng. Đây là thành phần cốt lõi để LLM có thể trả lời câu hỏi dựa trên nội dung tài liệu cụ thể thay vì kiến thức tổng quát.

### 3.5.2 Kỹ thuật RAG (Retrieval-Augmented Generation)

RAG [5] là một kỹ thuật kết hợp khả năng truy xuất thông tin (retrieval) với khả năng sinh văn bản (generation) của LLM. Thay vì chỉ dựa vào kiến thức được huấn luyện sẵn, LLM được cung cấp thêm ngữ cảnh (context) từ nguồn dữ liệu bên ngoài để tạo câu trả lời chính xác và cập nhật hơn.

Quy trình RAG bao gồm các bước: (i) Indexing - chia tài liệu thành chunks và chuyển thành embeddings, (ii) Retrieval - khi có câu hỏi, tìm các chunks liên quan nhất dựa trên similarity, và (iii) Generation - kết hợp câu hỏi với context để tạo prompt cho LLM.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     QUY TRÌNH RAG TRONG HỆ THỐNG                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
    ┌───────────────────────────┴───────────────────────────┐
    │                    GIAI ĐOẠN INDEXING                  │
    └───────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Tài liệu   │───►│  Text       │───►│  Embedding   │───►│    FAISS     │
│  (PDF/DOCX)  │    │  Splitter   │    │    Model     │    │ Vector Store │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                    │
    ┌───────────────────────────────────────────────────────────────┘
    │                   GIAI ĐOẠN RETRIEVAL + GENERATION
    └───────────────────────────────────────────────────────────────┐
                                                                    │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────▼───────┐
│   Câu hỏi    │───►│  Embedding   │───►│  Similarity  │───►│   Top-K      │
│  người dùng  │    │    Model     │    │   Search     │    │   Chunks     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    │
                    ▼
            ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
            │   Prompt     │───►│     LLM      │───►│   Câu trả    │
            │ (Q + Context)│    │   (Ollama)   │    │     lời      │
            └──────────────┘    └──────────────┘    └──────────────┘
```

### 3.5.3 Các lựa chọn Vector Database

| Công nghệ | Loại | Ưu điểm | Nhược điểm |
|-----------|------|---------|------------|
| **Pinecone** | Cloud managed | Scalable, dễ dùng | Chi phí cao, phụ thuộc cloud |
| **Weaviate** | Self-hosted | GraphQL API, multi-modal | Cấu hình phức tạp |
| **Chroma** | Embedded | Nhẹ, dễ tích hợp | Chưa mature, giới hạn scale |
| **FAISS** | Library | Nhanh, miễn phí, chạy local | Không có API server, cần code |

### 3.5.4 Lựa chọn: FAISS với HuggingFace Embeddings

**FAISS** (Facebook AI Similarity Search) [6] là thư viện mã nguồn mở của Meta AI, được thiết kế cho việc tìm kiếm similarity hiệu quả trên tập dữ liệu vector lớn. FAISS được lựa chọn vì:

Thứ nhất, FAISS hoạt động hoàn toàn offline, phù hợp với yêu cầu triển khai on-premise (NFR14). Không có dữ liệu vector nào được gửi ra ngoài hệ thống.

Thứ hai, FAISS cung cấp nhiều index types (Flat, IVF, HNSW) cho phép cân bằng giữa accuracy và speed. Với quy mô dữ liệu của hệ thống (tài liệu từng người dùng), IndexFlatL2 đơn giản là đủ hiệu quả.

Thứ ba, FAISS tích hợp sẵn với LangChain thông qua `langchain_community.vectorstores.FAISS`, giúp việc implementation đơn giản và nhất quán với architecture.

**Sentence Transformers** [7] với model `all-MiniLM-L6-v2` được sử dụng để tạo embeddings. Model này cân bằng tốt giữa chất lượng embedding và tốc độ xử lý, với kích thước vector 384 chiều và có thể chạy trên CPU.

```python
# Ví dụ sử dụng FAISS với LangChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)
vector_store = FAISS.from_documents(chunks, embeddings)
```

---

## 3.6 Công nghệ tạo file PowerPoint

### 3.6.1 Vấn đề cần giải quyết

Use case UC02 yêu cầu hệ thống tự động tạo file PowerPoint (.pptx) từ nội dung được sinh bởi LLM. File output cần đáp ứng: (i) định dạng chuẩn Microsoft PowerPoint, (ii) hỗ trợ Unicode tiếng Việt, và (iii) có thể mở và chỉnh sửa bằng các phần mềm trình chiếu phổ biến.

### 3.6.2 Các lựa chọn công nghệ

| Công nghệ | Ngôn ngữ | Ưu điểm | Nhược điểm |
|-----------|----------|---------|------------|
| **Apache POI** | Java | Full-featured, mature | Cần JVM, không phù hợp Python stack |
| **python-pptx** | Python | Native Python, API đơn giản | Một số tính năng nâng cao thiếu |
| **Aspose.Slides** | Multi | Enterprise-grade | Chi phí license cao |
| **Google Slides API** | Cloud | Tích hợp Google | Cần internet, phụ thuộc cloud |

### 3.6.3 Lựa chọn: python-pptx

**python-pptx** [8] là thư viện Python cho phép tạo và cập nhật file PowerPoint (.pptx). Thư viện này được lựa chọn vì:

Về tính tương thích, python-pptx tạo file .pptx chuẩn Office Open XML (OOXML) có thể mở bằng Microsoft PowerPoint, LibreOffice Impress, và Google Slides. Điều này đảm bảo file output có thể sử dụng trên nhiều nền tảng.

Về API design, python-pptx cung cấp object model trực quan: Presentation → Slides → Shapes → Text Frames → Paragraphs → Runs. Developers có thể dễ dàng tạo slide, thêm title, content, và định dạng text.

```python
# Ví dụ tạo slide với python-pptx
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
slide_layout = prs.slide_layouts[1]  # Title and Content layout
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Tiêu đề Slide"

content = slide.placeholders[1]
tf = content.text_frame
tf.text = "Nội dung chính"
p = tf.add_paragraph()
p.text = "• Điểm 1"
p.level = 1

prs.save('output.pptx')
```

Về hỗ trợ Unicode, python-pptx xử lý tốt các ký tự Unicode bao gồm tiếng Việt có dấu, đáp ứng yêu cầu NFR11 về hỗ trợ tiếng Việt hoàn toàn.

---

## 3.7 Công nghệ xử lý tài liệu

### 3.7.1 Vấn đề cần giải quyết

Theo yêu cầu UC01.1, hệ thống cần đọc và trích xuất nội dung từ nhiều định dạng tài liệu: PDF, DOCX, TXT, và MD. Mỗi định dạng có cấu trúc và encoding khác nhau, đòi hỏi các công cụ xử lý chuyên biệt.

### 3.7.2 Các thư viện được sử dụng

**PyPDF** (pypdf) [9] được sử dụng để đọc file PDF. Đây là thư viện pure Python, không yêu cầu dependencies bên ngoài, hỗ trợ đọc text, metadata, và có thể xử lý file PDF được encrypt.

**python-docx** [10] được sử dụng để đọc file Microsoft Word (.docx). Thư viện này parse file DOCX (thực chất là file ZIP chứa XML) và extract nội dung text từ paragraphs, tables, và headers.

Đối với file TXT và MD, hệ thống sử dụng Python built-in file I/O với encoding UTF-8 để đảm bảo hỗ trợ tiếng Việt.

```python
# Ví dụ đọc các định dạng file
from pypdf import PdfReader
import docx

def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() for page in reader.pages)
    elif file_type == "docx":
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    else:  # txt, md
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
```

---

## 3.8 Công nghệ triển khai và vận hành

### 3.8.1 Docker và Containerization

**Docker** [11] được sử dụng để đóng gói ứng dụng và dependencies vào container, đáp ứng yêu cầu NFR21 về containerization. Dockerfile được thiết kế với multi-stage build để tối ưu image size.

Lợi ích của việc sử dụng Docker bao gồm: (i) môi trường nhất quán giữa development và production, (ii) dễ dàng scale và deploy, (iii) isolation giữa các service, và (iv) version control cho infrastructure.

```dockerfile
# Multi-stage Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 8000 8501
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.8.2 Nginx Reverse Proxy

**Nginx** [12] được sử dụng làm reverse proxy phía trước FastAPI và Streamlit servers. Nginx đảm nhiệm: (i) load balancing nếu cần scale, (ii) SSL termination cho HTTPS, (iii) caching static files, và (iv) request routing dựa trên URL path.

### 3.8.3 SQLite Database

**SQLite** [13] được chọn làm database chính cho lưu trữ metadata tài liệu và lịch sử hội thoại. SQLite là embedded database, không cần setup server riêng, phù hợp với quy mô triển khai single-server của hệ thống.

---

## 3.9 Tổng hợp công nghệ và yêu cầu

Bảng dưới đây tổng hợp mối quan hệ giữa các công nghệ được sử dụng và các yêu cầu chức năng/phi chức năng đã xác định tại Chương 2:

| Yêu cầu | Công nghệ giải quyết |
|---------|---------------------|
| UC01: Phân tích tài liệu | PyPDF, python-docx, LangChain |
| UC01.3: RAG Q&A | FAISS, HuggingFace Embeddings, LangChain |
| UC02: Tạo slide | python-pptx, Ollama/LLM |
| UC03: Tạo quiz | Ollama/LLM, LangChain |
| UC04: Quản lý model | Ollama API |
| NFR01-03: Hiệu năng | FastAPI async, caching |
| NFR10-12: Usability | Streamlit |
| NFR14-17: Bảo mật | Ollama (on-premise), FAISS (local) |
| NFR18-21: Bảo trì | Docker, kiến trúc phân lớp |

---

## Kết luận chương

Chương 3 đã trình bày chi tiết các công nghệ được sử dụng trong hệ thống AI NVCB và lý giải sự lựa chọn của từng công nghệ. Kiến trúc phân lớp với FastAPI backend, Streamlit frontend, và Ollama/LangChain cho AI processing tạo nên một hệ thống module hóa, dễ bảo trì và mở rộng.

Điểm nổi bật của stack công nghệ là khả năng triển khai hoàn toàn on-premise với Ollama và FAISS, đảm bảo bảo mật dữ liệu người dùng. Việc sử dụng Python xuyên suốt từ frontend đến backend và AI layer giúp team development có thể làm việc hiệu quả với một ngôn ngữ duy nhất.

Các công nghệ này sẽ được áp dụng cụ thể trong quá trình thiết kế và triển khai hệ thống ở Chương 4.

---

## Tài liệu tham khảo

[1] Ollama Documentation, "Get up and running with large language models locally," https://ollama.com/

[2] LangChain Documentation, "Build context-aware reasoning applications," https://python.langchain.com/

[3] S. Ramírez, "FastAPI - Modern, Fast Web Framework for Python," https://fastapi.tiangolo.com/

[4] Streamlit Documentation, "A faster way to build and share data apps," https://docs.streamlit.io/

[5] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 2020.

[6] J. Johnson, M. Douze, H. Jégou, "Billion-scale similarity search with GPUs," IEEE Transactions on Big Data, 2019.

[7] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," EMNLP 2019.

[8] python-pptx Documentation, "Create Open XML PowerPoint documents in Python," https://python-pptx.readthedocs.io/

[9] pypdf Documentation, "A pure-python PDF library," https://pypdf.readthedocs.io/

[10] python-docx Documentation, "Create and modify Word documents," https://python-docx.readthedocs.io/

[11] Docker Documentation, "Develop faster. Run anywhere," https://docs.docker.com/

[12] Nginx Documentation, "Advanced Load Balancer, Web Server," https://nginx.org/en/docs/

[13] SQLite Documentation, "Small. Fast. Reliable," https://www.sqlite.org/docs.html
