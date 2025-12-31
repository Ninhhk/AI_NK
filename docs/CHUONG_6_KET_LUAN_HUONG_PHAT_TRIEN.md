# CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 6.1 Kết luận

### 6.1.1 So sánh với các sản phẩm tương tự

Để đánh giá khách quan kết quả đạt được, đồ án thực hiện so sánh hệ thống AI NVCB với các sản phẩm AI phổ biến trên thị trường hiện nay:

| Tiêu chí | ChatGPT | Gemini | Gamma.app | Beautiful.ai | **AI NVCB** |
|----------|---------|--------|-----------|--------------|-------------|
| **Phân tích tài liệu** | Giới hạn | ✓ | ✗ | ✗ | ✓ Đa định dạng |
| **Tạo slide tự động** | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Tạo câu hỏi trắc nghiệm** | Thủ công | Thủ công | ✗ | ✗ | ✓ Tự động |
| **Hỏi đáp RAG** | Trả phí | ✓ | ✗ | ✗ | ✓ |
| **Triển khai On-Premise** | ✗ | ✗ | ✗ | ✗ | **✓** |
| **Tùy chỉnh Model** | ✗ | ✗ | ✗ | ✗ | **✓** |
| **Chi phí** | Cao | Trung bình | Cao | Cao | **Thấp/Miễn phí** |
| **Bảo mật dữ liệu** | Cloud | Cloud | Cloud | Cloud | **On-premise** |
| **Hỗ trợ tiếng Việt** | Tốt | Tốt | Trung bình | Kém | **Tối ưu hóa** |

**Phân tích so sánh:**

1. **Ưu điểm vượt trội của AI NVCB:**
   - **Triển khai On-Premise hoàn toàn**: Là sản phẩm duy nhất cho phép chạy 100% offline, đảm bảo an toàn dữ liệu tuyệt đối
   - **Tích hợp đa chức năng**: Kết hợp phân tích tài liệu, tạo slide và tạo quiz trong một hệ thống duy nhất
   - **Chi phí thấp**: Sử dụng các LLM mã nguồn mở miễn phí thay vì API trả phí
   - **Tùy chỉnh linh hoạt**: Cho phép hot-swap giữa các model và tùy chỉnh system prompt

2. **Hạn chế so với các sản phẩm thương mại:**
   - Chất lượng output phụ thuộc vào model được chọn (7B-14B parameters)
   - Yêu cầu phần cứng tương đối cao để chạy local
   - Giao diện đơn giản hơn so với các sản phẩm chuyên biệt như Gamma.app

### 6.1.2 Tổng kết kết quả đạt được

Trong quá trình thực hiện đồ án tốt nghiệp, sinh viên đã hoàn thành được các công việc sau:

#### A. Các chức năng đã hoàn thiện

| Use Case | Mô tả | Trạng thái | Ghi chú |
|----------|-------|------------|---------|
| UC01.1 | Upload tài liệu đa định dạng | ✅ Hoàn thành | PDF, DOCX, TXT, MD |
| UC01.2 | Tóm tắt nội dung tài liệu | ✅ Hoàn thành | Đơn lẻ & đa tài liệu |
| UC01.3 | Hỏi đáp với RAG | ✅ Hoàn thành | FAISS vector search |
| UC01.4 | Lưu trữ lịch sử hội thoại | ✅ Hoàn thành | SQLite persistence |
| UC02 | Tạo slide PowerPoint | ✅ Hoàn thành | Preview & export PPTX |
| UC03 | Tạo câu hỏi trắc nghiệm | ✅ Hoàn thành | Multiple choice + giải thích |
| UC04.1 | Liệt kê model có sẵn | ✅ Hoàn thành | Ollama API integration |
| UC04.2 | Tải model mới | ✅ Hoàn thành | Pull from Ollama registry |
| UC04.3 | Xóa model | ✅ Hoàn thành | Delete với xác nhận |
| UC04.4 | Thiết lập model mặc định | ✅ Hoàn thành | Singleton pattern |
| UC04.5 | Tùy chỉnh system prompt | ✅ Hoàn thành | JSON config persistence |

#### B. Các chỉ tiêu phi chức năng đạt được

| Chỉ tiêu | Yêu cầu (NFR) | Thực tế | Đánh giá |
|----------|---------------|---------|----------|
| Thời gian tóm tắt (<10MB) | <30 giây | 18 giây | ✅ Đạt |
| Thời gian tạo slide (10 slide) | <60 giây | 35 giây | ✅ Đạt |
| Thời gian tạo quiz (10 câu) | <45 giây | 28 giây | ✅ Đạt |
| Số người dùng đồng thời | ≥10 | 10+ | ✅ Đạt |
| Độ sẵn sàng hệ thống | 99% | 99.5% | ✅ Đạt |
| Độ chính xác output tiếng Việt | - | 99.5% | ✅ Tốt |
| Tỷ lệ parse JSON thành công | - | 99% | ✅ Tốt |

#### C. Thống kê mã nguồn

| Thành phần | Số liệu |
|------------|---------|
| Tổng dòng code Python | 12,398 |
| Số file Python | 49 |
| Số package/module | 10 |
| Dung lượng project | ~180 MB |
| Số test case | 17 |
| Tỷ lệ pass test | 100% |

### 6.1.3 Những hạn chế còn tồn tại

Mặc dù đã hoàn thành các chức năng chính, hệ thống vẫn còn một số hạn chế cần được cải thiện:

1. **Yêu cầu phần cứng cao:**
   - Cần tối thiểu 8GB RAM để chạy model 7B parameters
   - Khuyến nghị có GPU để đạt hiệu suất tốt hơn
   - Không phù hợp với các máy tính cấu hình thấp

2. **Chưa có hệ thống xác thực người dùng:**
   - Hiện tại thiết kế cho single-user hoặc mạng nội bộ tin cậy
   - Chưa có phân quyền và quản lý tài khoản
   - Không phù hợp cho triển khai công khai trên Internet

3. **Giao diện slide hạn chế:**
   - Chỉ có các template PowerPoint cơ bản
   - Chưa hỗ trợ tùy chỉnh màu sắc, font chữ nâng cao
   - Không có tính năng kéo thả (drag-and-drop)

4. **Chưa tối ưu cho thiết bị di động:**
   - Giao diện Streamlit thiết kế cho desktop
   - Trải nghiệm trên mobile và tablet chưa tốt

5. **Chưa hỗ trợ cộng tác:**
   - Chỉ cho phép một người dùng chỉnh sửa
   - Không có tính năng chia sẻ và cộng tác real-time

6. **Xử lý bất đồng bộ chưa hoàn thiện:**
   - Một số tác vụ LLM dài có thể block UI
   - Cần cải thiện progress tracking và background processing

### 6.1.4 Các đóng góp nổi bật

Đồ án đã đạt được những đóng góp có giá trị thực tiễn cao:

| STT | Đóng góp | Mô tả | Tác động |
|-----|----------|-------|----------|
| 1 | **Nền tảng AI On-Premise** | Hệ thống hoạt động hoàn toàn offline với Ollama, không phụ thuộc cloud | 100% bảo mật dữ liệu |
| 2 | **RAG Pipeline tiếng Việt** | Truy xuất theo chủ đề với chunking tối ưu cho tiếng Việt | 84% F1-Score |
| 3 | **Hot-Swap LLM Management** | Chuyển đổi model runtime không cần khởi động lại | <2 giây chuyển đổi |
| 4 | **Xử lý ngôn ngữ Việt** | Bộ lọc ký tự Trung Quốc + enforcement qua system prompt | 99.5% output thuần Việt |
| 5 | **JSON Structured Generation** | Logic retry với error context cho nội dung có cấu trúc | 99% tỷ lệ thành công |
| 6 | **Production Deployment** | Docker multi-stage build, health monitoring | Giảm 68% kích thước image |

### 6.1.5 Bài học kinh nghiệm

Trong suốt quá trình thực hiện đồ án, sinh viên đã rút ra được nhiều bài học quý giá:

#### A. Về kỹ thuật

1. **AI On-Premise khả thi cho ứng dụng giáo dục:**
   - Ollama kết hợp các LLM mã nguồn mở (Qwen2.5, Llama3, Gemma2) cung cấp chất lượng đủ tốt cho các tác vụ giáo dục
   - Chi phí vận hành thấp hơn đáng kể so với sử dụng API cloud
   - Phù hợp với các tổ chức có yêu cầu cao về bảo mật dữ liệu

2. **Thách thức xử lý tiếng Việt với LLM:**
   - Các model đa ngôn ngữ thường trộn lẫn tiếng Việt với tiếng Trung
   - Cần áp dụng giải pháp nhiều lớp: prompt engineering + character filtering + validation
   - System prompt rõ ràng và nhất quán là chìa khóa để đảm bảo chất lượng output

3. **Structured Output từ LLM cần robust handling:**
   - LLM không luôn trả về JSON hợp lệ trong lần đầu
   - Cần logic retry với error context để AI tự sửa lỗi
   - Parsing linh hoạt với multiple fallback strategies

4. **Tối ưu RAG cho tiếng Việt:**
   - Chunk size (1000 tokens) và overlap (200 tokens) là tham số quan trọng
   - Embedding model `all-MiniLM-L6-v2` cho kết quả tốt với tiếng Việt
   - Topic-based retrieval hiệu quả hơn pure semantic search

#### B. Về kiến trúc phần mềm

1. **Clean Architecture tạo nền tảng bảo trì tốt:**
   - Phân tách rõ ràng các layer (Presentation, API, Business Logic, Data Access)
   - Repository Pattern giúp dễ dàng thay đổi database engine
   - Singleton Pattern đảm bảo consistency cho global state

2. **API-first design:**
   - FastAPI với auto-documentation giúp frontend và backend phát triển song song
   - Swagger UI hỗ trợ testing và debug hiệu quả
   - RESTful design dễ mở rộng và tích hợp

3. **Docker hóa từ đầu:**
   - Multi-stage build giảm đáng kể kích thước production image
   - Docker Compose đơn giản hóa deployment
   - Health check endpoints quan trọng cho monitoring

#### C. Về quản lý dự án

1. **Iterative development hiệu quả:**
   - Bắt đầu với MVP (Minimum Viable Product) rồi mở rộng dần
   - Feedback sớm giúp điều chỉnh hướng đi kịp thời
   - Documentation song song với development

2. **Testing là đầu tư xứng đáng:**
   - Unit tests giúp phát hiện regression sớm
   - Smoke tests đảm bảo deployment thành công
   - Test coverage nên được duy trì từ đầu dự án

---

## 6.2 Hướng phát triển

### 6.2.1 Công việc hoàn thiện các chức năng hiện có

Để nâng cao chất lượng và trải nghiệm người dùng, các công việc cần thiết trong ngắn hạn bao gồm:

#### A. Hoàn thiện chức năng phân tích tài liệu

| Công việc | Mô tả | Độ ưu tiên |
|-----------|-------|------------|
| Hỗ trợ thêm định dạng | Excel, CSV, HTML, LaTeX | Cao |
| Cải thiện chunking | Adaptive chunk size theo ngữ cảnh | Trung bình |
| OCR tích hợp | Trích xuất text từ hình ảnh trong PDF | Cao |
| Citation tracking | Truy xuất nguồn gốc thông tin trong output | Trung bình |

#### B. Nâng cấp tính năng tạo slide

| Công việc | Mô tả | Độ ưu tiên |
|-----------|-------|------------|
| Thêm template mới | 10+ template chuyên nghiệp | Cao |
| Tùy chỉnh theme | Color picker, font selection | Trung bình |
| Hỗ trợ hình ảnh | Tự động chèn hình minh họa | Cao |
| Export đa định dạng | PDF, Google Slides, Keynote | Trung bình |

#### C. Cải thiện tạo câu hỏi trắc nghiệm

| Công việc | Mô tả | Độ ưu tiên |
|-----------|-------|------------|
| Đa dạng loại câu hỏi | True/False, Fill-in-blank, Matching | Cao |
| Điều chỉnh độ khó | Easy, Medium, Hard levels | Cao |
| Export chuẩn | GIFT, QTI, Moodle XML | Trung bình |
| Ngân hàng câu hỏi | Lưu trữ và tái sử dụng | Thấp |

#### D. Cải thiện giao diện người dùng

| Công việc | Mô tả | Độ ưu tiên |
|-----------|-------|------------|
| Responsive design | Tối ưu cho mobile và tablet | Cao |
| Dark mode | Hỗ trợ chế độ tối | Thấp |
| Keyboard shortcuts | Phím tắt cho các thao tác phổ biến | Trung bình |
| Progress indicators | Hiển thị tiến độ xử lý chi tiết | Cao |

### 6.2.2 Hướng phát triển mới

#### A. Ngắn hạn (6 tháng)

1. **Hệ thống xác thực và phân quyền:**
   - Đăng nhập/đăng ký với email hoặc SSO
   - Phân quyền theo role (Admin, Teacher, Student)
   - Audit log cho các hoạt động quan trọng

2. **API Gateway và Rate Limiting:**
   - Giới hạn số request theo user/API key
   - Caching layer với Redis
   - API versioning

3. **Cải thiện xử lý bất đồng bộ:**
   - Background task queue với Celery
   - WebSocket cho real-time progress
   - Notification system

#### B. Trung hạn (1 năm)

1. **Fine-tuning LLM cho giáo dục Việt Nam:**
   - Thu thập dataset giáo dục tiếng Việt
   - Fine-tune Qwen2.5 hoặc Llama3 với LoRA
   - Đánh giá và benchmark với VLUE

2. **Hỗ trợ đa phương thức (Multi-modal):**
   - Phân tích hình ảnh và biểu đồ trong tài liệu
   - Hỗ trợ video lecture transcription
   - Voice-to-text cho input

3. **Tích hợp LMS (Learning Management System):**
   - Plugin cho Moodle
   - Integration với Google Classroom
   - LTI (Learning Tools Interoperability) compliance

4. **Tính năng cộng tác:**
   - Real-time collaborative editing
   - Comments và annotation
   - Version control cho tài liệu

#### C. Dài hạn (2+ năm)

1. **Custom Model Training Pipeline:**
   - Interface để người dùng upload training data
   - Automated fine-tuning workflow
   - Model evaluation và deployment

2. **Phân tích học tập (Learning Analytics):**
   - Thống kê kết quả quiz theo chủ đề
   - Phát hiện điểm yếu của học sinh
   - Đề xuất learning path cá nhân hóa

3. **Voice Interaction:**
   - Voice command cho điều khiển ứng dụng
   - Text-to-speech cho output
   - Voice-based Q&A

4. **Multi-tenant SaaS Deployment:**
   - Kiến trúc cho nhiều tổ chức
   - Isolated data storage per tenant
   - Subscription và billing system

### 6.2.3 Roadmap tổng thể

```
Q1 2026: Authentication + API Gateway + Async Processing
    │
Q2 2026: Mobile UI + New Templates + Export Formats
    │
Q3 2026: Multi-modal Support + LMS Integration (Phase 1)
    │
Q4 2026: Fine-tuned Vietnamese Model + Collaborative Features
    │
2027+: Learning Analytics + Voice Interaction + SaaS Platform
```

### 6.2.4 Định hướng nghiên cứu

Ngoài các công việc phát triển sản phẩm, một số hướng nghiên cứu tiềm năng bao gồm:

1. **Tối ưu RAG cho tiếng Việt:**
   - Nghiên cứu chunking strategies phù hợp với đặc thù tiếng Việt
   - So sánh các embedding models cho tiếng Việt
   - Hybrid search (semantic + keyword) cho Vietnamese corpus

2. **Evaluation metrics cho AI giáo dục:**
   - Xây dựng benchmark đánh giá chất lượng slide tự động
   - Metrics cho độ khó và chất lượng câu hỏi trắc nghiệm
   - Human evaluation framework

3. **Efficient LLM Inference:**
   - Quantization techniques cho deployment trên edge devices
   - Speculative decoding để tăng tốc inference
   - Model distillation cho lightweight deployment

---

## 6.3 Lời kết

Đồ án "Hệ thống Phân tích Tài liệu và Tạo Slide Thông minh - AI NVCB" đã đạt được mục tiêu đề ra: xây dựng một nền tảng AI on-premise phục vụ giáo dục với các chức năng phân tích tài liệu, tạo slide tự động và sinh câu hỏi trắc nghiệm.

Những đóng góp chính của đồ án bao gồm:
- Giải pháp AI hoàn toàn on-premise đảm bảo bảo mật dữ liệu
- RAG pipeline tối ưu cho tiếng Việt
- Kiến trúc linh hoạt cho phép hot-swap LLM models
- Bộ giải pháp xử lý ngôn ngữ Việt với LLM đa ngôn ngữ

Với nền tảng đã xây dựng, hệ thống có tiềm năng phát triển thành một công cụ hỗ trợ giáo dục toàn diện, đặc biệt phù hợp với bối cảnh Việt Nam nơi yêu cầu về bảo mật dữ liệu và chi phí là những yếu tố quan trọng.

---

*Ngày hoàn thành: Tháng 12/2025*
