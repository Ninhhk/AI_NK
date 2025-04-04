I'll examine the repository and create a comprehensive document about the application following your outline. Let me start by exploring the codebase.

Ran tool
Let's look at the README.md file to understand the application better:

Read file: README.md
Now let's look at the structure of the backend:

Ran tool
Let's examine the frontend structure:

Ran tool
Let's look at the main frontend app:

Read file: frontend/app.py
Let's check the frontend pages:

Ran tool
Now let's check the backend document analysis module:

Ran tool
Let's examine the document service:

Read file: backend/document_analysis/document_service.py
Now let's check the slide generation module:

Ran tool
Let's examine the slide service:

Read file: backend/slide_generation/slide_service.py
Let's examine the PowerPoint generator:

Read file: backend/slide_generation/pptx_generator.py
Let's examine the structure of the frontend pages:

Read file: frontend/pages/document_analysis.py
Based on the examination of the codebase, I'll now create a comprehensive documentation following your outline.

# ĐỒ ÁN: ỨNG DỤNG PHÂN TÍCH TÀI LIỆU VÀ TẠO BÀI THUYẾT TRÌNH AI_NVCB

## Chương 1: Giới thiệu đề tài

### 1.1 Đặt vấn đề
Trong thời đại số hóa hiện nay, việc phân tích tài liệu và tạo bài thuyết trình đòi hỏi nhiều thời gian và công sức. Các nhà giáo dục, học sinh, sinh viên và doanh nghiệp cần các công cụ hiệu quả để xử lý tài liệu, trích xuất thông tin quan trọng và tạo ra các bài thuyết trình chuyên nghiệp một cách nhanh chóng. Tuy nhiên, các công cụ hiện có thường thiếu sự tích hợp giữa phân tích nội dung và tạo bài thuyết trình, đồng thời chưa tận dụng triệt để khả năng của trí tuệ nhân tạo.

### 1.2 Mục tiêu và phạm vi đề tài
Dự án AI_NVCB nhằm mục tiêu phát triển một ứng dụng tích hợp cung cấp các khả năng sau:
1. Phân tích tài liệu PDF với khả năng tóm tắt và trả lời câu hỏi dựa trên nội dung
2. Tạo bài thuyết trình tự động từ chủ đề hoặc tài liệu được cung cấp
3. Tạo bài kiểm tra tự động từ nội dung tài liệu
4. Giao diện người dùng thân thiện và dễ sử dụng

Phạm vi đề tài bao gồm:
- Hỗ trợ tài liệu đầu vào định dạng PDF
- Phân tích và tóm tắt nội dung bằng tiếng Việt
- Tạo bài thuyết trình PowerPoint với nội dung có cấu trúc
- Tạo bài kiểm tra trắc nghiệm từ tài liệu
- Triển khai ứng dụng web dễ sử dụng

### 1.3 Định hướng giải pháp
Để đạt được mục tiêu đề ra, dự án tập trung vào các định hướng giải pháp sau:
1. Sử dụng mô hình ngôn ngữ lớn (LLM) cho phân tích nội dung, tóm tắt và sinh văn bản
2. Xây dựng kiến trúc phân tách rõ ràng giữa backend và frontend
3. Tận dụng thư viện xử lý PDF và tạo bài thuyết trình mạnh mẽ
4. Thiết kế giao diện thân thiện với người dùng bằng Streamlit
5. Tối ưu hóa hiệu suất thông qua phân đoạn tài liệu và xử lý bất đồng bộ

### 1.4 Bố cục đồ án
Bố cục của đồ án gồm 5 chương chính:
1. Chương 1: Giới thiệu đề tài - Trình bày mục tiêu, phạm vi và định hướng giải pháp
2. Chương 2: Khảo sát và phân tích yêu cầu - Mô tả hiện trạng, usecase, quy trình và đặc tả chức năng
3. Chương 3: Công nghệ sử dụng - Chi tiết về các công nghệ và ứng dụng trong hệ thống
4. Chương 4: Phát triển và triển khai ứng dụng - Mô tả thiết kế, xây dựng và triển khai ứng dụng
5. Chương 5: Kết luận và hướng phát triển - Tổng kết kết quả đạt được và đề xuất hướng phát triển

## Chương 2: Khảo sát và phân tích yêu cầu

### 2.1 Khảo sát hiện trạng
Hiện nay, người dùng thường phải sử dụng nhiều công cụ riêng lẻ để thực hiện các tác vụ liên quan đến xử lý tài liệu và tạo bài thuyết trình:

1. **Phân tích tài liệu**: Người dùng phải đọc tài liệu thủ công, tự tóm tắt hoặc sử dụng các công cụ trích xuất nội dung cơ bản.
2. **Tạo bài thuyết trình**: Người dùng phải sử dụng Microsoft PowerPoint hoặc các công cụ tương tự để tạo thủ công các slide, thiết kế giao diện và tổ chức nội dung.
3. **Tạo bài kiểm tra**: Giáo viên phải tự soạn thảo câu hỏi kiểm tra dựa trên tài liệu, mất nhiều thời gian và công sức.

Các hạn chế của phương pháp truyền thống:
- Tốn thời gian và công sức
- Thiếu sự tích hợp giữa các công cụ
- Khó duy trì tính nhất quán
- Chất lượng phụ thuộc vào kỹ năng cá nhân
- Chưa tận dụng được sức mạnh của trí tuệ nhân tạo

Hệ thống AI_NVCB giải quyết các vấn đề trên bằng cách tích hợp các chức năng vào một nền tảng duy nhất, sử dụng AI để tự động hóa các tác vụ thời gian.

### 2.2 Tổng quan chức năng

#### 2.2.1 Biểu đồ use case tổng quan

**Use Case 1: Phân tích tài liệu**
- Actor: Người dùng
- Mô tả: Người dùng tải lên tài liệu PDF để phân tích, tóm tắt và trích xuất thông tin.
- Tiền điều kiện: Người dùng đã truy cập vào hệ thống.
- Hậu điều kiện: Hệ thống hiển thị kết quả phân tích tài liệu.

**Use Case 2: Tạo bài thuyết trình**
- Actor: Người dùng
- Mô tả: Người dùng cung cấp chủ đề và tùy chọn để hệ thống tạo bài thuyết trình.
- Tiền điều kiện: Người dùng đã truy cập vào hệ thống.
- Hậu điều kiện: Hệ thống tạo và hiển thị bài thuyết trình PowerPoint.

**Use Case 3: Tạo bài kiểm tra**
- Actor: Người dùng
- Mô tả: Người dùng tải lên tài liệu PDF và cấu hình để hệ thống tạo bài kiểm tra.
- Tiền điều kiện: Người dùng đã truy cập vào hệ thống.
- Hậu điều kiện: Hệ thống tạo và hiển thị bài kiểm tra cùng đáp án.

**Use Case 4: Đặt câu hỏi về tài liệu**
- Actor: Người dùng
- Mô tả: Người dùng đặt câu hỏi cụ thể về nội dung tài liệu đã tải lên.
- Tiền điều kiện: Người dùng đã tải lên tài liệu.
- Hậu điều kiện: Hệ thống hiển thị câu trả lời dựa trên nội dung tài liệu.

#### 2.2.2 Quy trình nghiệp vụ

**Quy trình 1: Phân tích và tóm tắt tài liệu**
1. Người dùng truy cập trang "Phân tích Tài liệu"
2. Tải lên tài liệu PDF
3. Chọn phạm vi trang cần phân tích (tùy chọn)
4. Chọn loại phân tích "summary"
5. Nhấn nút "Phân tích"
6. Hệ thống xử lý tài liệu và hiển thị bản tóm tắt

**Quy trình 2: Đặt câu hỏi về tài liệu**
1. Người dùng truy cập trang "Phân tích Tài liệu"
2. Tải lên tài liệu PDF
3. Chọn phạm vi trang cần phân tích (tùy chọn)
4. Chọn loại phân tích "qa"
5. Nhập câu hỏi cụ thể
6. Nhấn nút "Phân tích"
7. Hệ thống xử lý tài liệu và hiển thị câu trả lời

**Quy trình 3: Tạo bài thuyết trình**
1. Người dùng truy cập trang "Tạo Slide"
2. Nhập chủ đề bài thuyết trình
3. Chọn số lượng slide mong muốn
4. Nhấn nút "Tạo Bài Thuyết Trình"
5. Hệ thống tạo bài thuyết trình và hiển thị xem trước
6. Người dùng tải xuống file PowerPoint (tùy chọn)

**Quy trình 4: Tạo bài kiểm tra từ tài liệu**
1. Người dùng truy cập trang "Tạo Bài Kiểm Tra"
2. Tải lên tài liệu PDF
3. Chọn số lượng câu hỏi
4. Chọn độ khó
5. Chọn phạm vi trang (tùy chọn)
6. Nhấn nút "Tạo Bài Kiểm Tra"
7. Hệ thống tạo bài kiểm tra và hiển thị câu hỏi cùng đáp án

**Quy trình 5: Quản lý kết quả đã tạo**
1. Hệ thống lưu trữ kết quả phân tích, bài thuyết trình và bài kiểm tra
2. Người dùng có thể tải xuống bài thuyết trình dưới dạng PowerPoint
3. Người dùng có thể tải xuống bài kiểm tra dưới dạng PDF

### 2.3 Đặc tả chức năng

**Đặc tả 1: Tải lên và xử lý tài liệu PDF**
- Mô tả: Hệ thống cho phép người dùng tải lên tài liệu PDF và xử lý để trích xuất nội dung.
- Đầu vào: File PDF, phạm vi trang (tùy chọn)
- Xử lý: Sử dụng PyPDFLoader để đọc và trích xuất văn bản từ file PDF
- Đầu ra: Nội dung văn bản đã trích xuất

**Đặc tả 2: Tóm tắt tài liệu**
- Mô tả: Hệ thống phân tích và tóm tắt nội dung tài liệu PDF.
- Đầu vào: Nội dung văn bản đã trích xuất từ PDF
- Xử lý: Sử dụng mô hình LLM để tạo bản tóm tắt
- Đầu ra: Bản tóm tắt chi tiết bằng tiếng Việt

**Đặc tả 3: Trả lời câu hỏi dựa trên tài liệu**
- Mô tả: Hệ thống trả lời câu hỏi người dùng dựa trên nội dung tài liệu.
- Đầu vào: Nội dung văn bản đã trích xuất từ PDF, câu hỏi của người dùng
- Xử lý: Sử dụng kết hợp vector embeddings và mô hình LLM để tìm kiếm thông tin liên quan và tạo câu trả lời
- Đầu ra: Câu trả lời chi tiết bằng tiếng Việt

**Đặc tả 4: Tạo bài thuyết trình**
- Mô tả: Hệ thống tạo bài thuyết trình PowerPoint từ chủ đề người dùng cung cấp.
- Đầu vào: Chủ đề bài thuyết trình, số lượng slide
- Xử lý: Sử dụng mô hình LLM để tạo nội dung có cấu trúc cho các slide, sau đó sử dụng thư viện python-pptx để tạo file PowerPoint
- Đầu ra: File PowerPoint và xem trước nội dung

**Đặc tả 5: Tạo bài kiểm tra trắc nghiệm**
- Mô tả: Hệ thống tạo bài kiểm tra trắc nghiệm từ nội dung tài liệu.
- Đầu vào: Nội dung văn bản đã trích xuất từ PDF, số lượng câu hỏi, độ khó
- Xử lý: Sử dụng mô hình LLM để tạo câu hỏi trắc nghiệm và đáp án
- Đầu ra: Danh sách câu hỏi trắc nghiệm và đáp án

### 2.4 Yêu cầu phi chức năng

#### 2.4.1 Hiệu năng
- Hệ thống phải xử lý tài liệu PDF lên đến 100 trang trong thời gian hợp lý
- Thời gian phản hồi cho phân tích tài liệu trong khoảng 30-60 giây
- Thời gian tạo bài thuyết trình không quá 2 phút

#### 2.4.2 Tính dễ dùng
- Giao diện người dùng trực quan, dễ sử dụng
- Hỗ trợ ngôn ngữ tiếng Việt
- Phản hồi trực quan về tiến trình xử lý
- Hỗ trợ hiển thị lỗi rõ ràng, dễ hiểu

#### 2.4.3 Các yêu cầu khác
- Bảo mật: Dữ liệu người dùng tải lên không được lưu trữ lâu dài
- Khả năng mở rộng: Hệ thống dễ dàng mở rộng với các tính năng mới
- Độ tin cậy: Hệ thống phải ổn định và có cơ chế xử lý lỗi thích hợp
- Khả năng tích hợp: Dễ dàng tích hợp với các hệ thống khác thông qua API

## Chương 3: Công nghệ sử dụng

### 3.1 Ngôn ngữ lập trình
**Python**: Dự án sử dụng Python làm ngôn ngữ lập trình chính vì khả năng xử lý dữ liệu mạnh mẽ và hệ sinh thái phong phú cho AI/ML và xử lý văn bản. Python 3.8 trở lên được sử dụng để đảm bảo tương thích với các thư viện hiện đại.

### 3.2 Frameworks và thư viện chính

#### 3.2.1 Backend
**LangChain**: Framework hỗ trợ phát triển ứng dụng AI, được sử dụng để tích hợp mô hình LLM, xử lý tài liệu và tạo chuỗi xử lý (chains). LangChain cung cấp các component như:
- Document Loaders: PyPDFLoader để đọc file PDF
- Text Splitters: RecursiveCharacterTextSplitter để phân đoạn văn bản
- Embeddings: HuggingFaceEmbeddings để tạo vector nhúng
- Vector Stores: FAISS để lưu trữ và tìm kiếm vector
- Chains: LLMChain để tạo chuỗi xử lý

**Ollama**: Công cụ triển khai mô hình ngôn ngữ lớn cục bộ, được sử dụng để chạy mô hình LLM (Qwen 2.5 7B) trên máy cục bộ. Ollama giúp giảm phụ thuộc vào API bên ngoài và cải thiện bảo mật dữ liệu.

**FastAPI**: Framework phát triển Web API hiệu năng cao, được sử dụng để xây dựng các API endpoint cho backend.

**PyMuPDF/pdf2image**: Thư viện xử lý PDF, được sử dụng để trích xuất và xử lý nội dung từ file PDF.

**python-pptx**: Thư viện tạo và chỉnh sửa file PowerPoint, được sử dụng để tạo bài thuyết trình từ dữ liệu đã sinh.

#### 3.2.2 Frontend
**Streamlit**: Framework xây dựng ứng dụng web cho khoa học dữ liệu và machine learning, được sử dụng để xây dựng giao diện người dùng trực quan và tương tác. Streamlit được chọn vì:
- Dễ phát triển và triển khai
- Hỗ trợ tốt cho ứng dụng dữ liệu
- Tích hợp sẵn các thành phần UI như file uploader, sliders, forms
- Cập nhật trực tiếp (hot reloading)

**CSS tùy chỉnh**: Được sử dụng để nâng cao giao diện người dùng và tạo trải nghiệm thẩm mỹ hơn.

### 3.3 Mô hình AI

**Qwen 2.5 7B**: Mô hình ngôn ngữ lớn phát triển bởi Alibaba, được sử dụng làm core AI cho hệ thống. Mô hình này được chọn vì:
- Hỗ trợ tốt tiếng Việt
- Hiệu suất tốt trên phần cứng tiêu chuẩn
- Có thể chạy cục bộ qua Ollama
- Khả năng xử lý và sinh văn bản chất lượng cao

### 3.4 Công cụ phát triển và Quản lý dự án

**Poetry**: Công cụ quản lý phụ thuộc và đóng gói cho Python, được sử dụng để quản lý các phụ thuộc dự án và môi trường ảo.

**Git**: Hệ thống quản lý phiên bản, được sử dụng để theo dõi thay đổi mã nguồn và cộng tác phát triển.

**VS Code**: Môi trường phát triển tích hợp, được sử dụng để viết và debug mã nguồn.

## Chương 4: Phát triển và triển khai ứng dụng

### 4.1 Thiết kế kiến trúc

#### 4.1.1 Lựa chọn kiến trúc phần mềm
Dự án AI_NVCB áp dụng kiến trúc phần mềm microservices để tách biệt các thành phần chức năng và cải thiện khả năng mở rộng. Kiến trúc gồm các thành phần chính:

1. **Frontend Service**: Xây dựng bằng Streamlit, cung cấp giao diện người dùng và tương tác.
2. **Backend API Service**: Xây dựng bằng FastAPI, cung cấp các API cho frontend.
3. **Document Analysis Service**: Xử lý tài liệu, tóm tắt và trả lời câu hỏi.
4. **Slide Generation Service**: Tạo bài thuyết trình từ chủ đề.
5. **Quiz Generation Service**: Tạo bài kiểm tra từ tài liệu.
6. **LLM Service**: Tích hợp và quản lý mô hình ngôn ngữ lớn.

Ưu điểm của kiến trúc này:
- Tách biệt rõ ràng giữa frontend và backend
- Dễ dàng mở rộng và cập nhật từng thành phần
- Khả năng chịu lỗi tốt hơn
- Khả năng mở rộng quy mô và hiệu suất

#### 4.1.2 Thiết kế tổng quan
Luồng dữ liệu và tương tác giữa các thành phần:

1. **Phân tích tài liệu**:
   - Frontend: Người dùng tải lên tài liệu PDF và chọn loại phân tích
   - API Gateway: Chuyển tiếp yêu cầu đến Document Analysis Service
   - Document Analysis Service: Xử lý tài liệu và trả về kết quả
   - Frontend: Hiển thị kết quả phân tích

2. **Tạo bài thuyết trình**:
   - Frontend: Người dùng nhập chủ đề và cấu hình
   - API Gateway: Chuyển tiếp yêu cầu đến Slide Generation Service
   - Slide Generation Service: Tạo nội dung slide và file PowerPoint
   - Frontend: Hiển thị xem trước và cung cấp link tải xuống

3. **Tạo bài kiểm tra**:
   - Frontend: Người dùng tải lên tài liệu và cấu hình
   - API Gateway: Chuyển tiếp yêu cầu đến Quiz Generation Service
   - Quiz Generation Service: Phân tích tài liệu và tạo câu hỏi
   - Frontend: Hiển thị bài kiểm tra và đáp án

#### 4.1.3 Thiết kế chi tiết các chức năng

**Document Analysis Service**:
- **DocumentLoader**: Đọc và trích xuất nội dung từ PDF
- **TextSplitter**: Phân đoạn văn bản thành các đoạn nhỏ hơn
- **Embeddings**: Tạo vector nhúng cho các đoạn văn bản
- **VectorStore**: Lưu trữ và tìm kiếm vector
- **SummaryChain**: Tóm tắt nội dung tài liệu
- **QAChain**: Trả lời câu hỏi dựa trên tài liệu

**Slide Generation Service**:
- **SlideGenerator**: Tạo nội dung cho các slide
- **PowerPointGenerator**: Tạo file PowerPoint từ nội dung slide
- **FileStorage**: Lưu trữ file đã tạo

**Quiz Generation Service**:
- **QuizGenerator**: Tạo câu hỏi trắc nghiệm từ tài liệu
- **QuizFormatter**: Định dạng bài kiểm tra

### 4.2 Thiết kế chi tiết

#### 4.2.1 Thiết kế giao diện
Giao diện người dùng được thiết kế với nguyên tắc trực quan, dễ sử dụng và phản hồi nhanh. Các trang chính:

1. **Trang chủ**: Giới thiệu ứng dụng và các chức năng.
2. **Phân tích Tài liệu**: Cho phép tải lên PDF, chọn loại phân tích và hiển thị kết quả.
3. **Tạo Slide**: Cho phép nhập chủ đề, cấu hình và tạo bài thuyết trình.
4. **Tạo Bài Kiểm Tra**: Cho phép tải lên PDF, cấu hình và tạo bài kiểm tra.

Thiết kế giao diện sử dụng các nguyên tắc:
- Bố cục rõ ràng, trực quan
- Phản hồi trực quan về trạng thái xử lý
- Hiển thị lỗi rõ ràng
- Tương thích với các thiết bị khác nhau

#### 4.2.2 Thiết kế lớp
Mô hình lớp chính của hệ thống:

1. **Document Analysis Module**:
   - `DocumentAnalysisService`: Quản lý xử lý tài liệu
   - `DocumentRoutes`: Định nghĩa API endpoints

2. **Slide Generation Module**:
   - `SlideGenerationService`: Quản lý tạo slide
   - `PowerPointGenerator`: Tạo file PowerPoint
   - `SlideRoutes`: Định nghĩa API endpoints

3. **Quiz Generation Module**:
   - `QuizGenerationService`: Quản lý tạo bài kiểm tra
   - `QuizRoutes`: Định nghĩa API endpoints

4. **Shared Module**:
   - `LLMService`: Quản lý mô hình ngôn ngữ
   - `FileService`: Quản lý tệp tin

#### 4.2.3 Thiết kế cơ sở dữ liệu
Hệ thống sử dụng lưu trữ tệp tin thay vì cơ sở dữ liệu quan hệ:

1. **Cấu trúc thư mục**:
   - `output/slides/`: Lưu trữ các bài thuyết trình đã tạo
   - `output/quizzes/`: Lưu trữ các bài kiểm tra đã tạo
   - `output/documents/`: Lưu trữ kết quả phân tích tài liệu

2. **Định dạng dữ liệu**:
   - JSON: Lưu trữ cấu trúc dữ liệu như nội dung slide, câu hỏi
   - PPTX: Lưu trữ bài thuyết trình
   - PDF: Lưu trữ tài liệu gốc

### 4.3 Xây dựng ứng dụng

#### 4.3.1 Thư viện và công cụ sử dụng
Các thư viện và công cụ chính:
- **Backend**:
  - FastAPI: Framework web API
  - LangChain: Framework ứng dụng AI
  - Ollama: Triển khai mô hình LLM
  - PyMuPDF: Xử lý PDF
  - python-pptx: Tạo PowerPoint

- **Frontend**:
  - Streamlit: Framework UI
  - requests: Gọi API
  - CSS tùy chỉnh: Giao diện người dùng

- **DevOps**:
  - Poetry: Quản lý phụ thuộc
  - Git: Quản lý phiên bản


