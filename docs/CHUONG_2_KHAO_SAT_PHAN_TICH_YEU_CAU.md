# CHƯƠNG 2: KHẢO SÁT VÀ PHÂN TÍCH YÊU CẦU

## Mở đầu chương

Chương này trình bày quá trình khảo sát hiện trạng và phân tích yêu cầu cho hệ thống **AI NVCB - Hệ thống Phân tích Tài liệu và Tạo Slide thông minh**. Nội dung chương bao gồm: (1) Khảo sát hiện trạng các hệ thống tương tự trên thị trường, (2) Tổng quan chức năng thông qua biểu đồ use case, (3) Đặc tả chi tiết các use case quan trọng, và (4) Các yêu cầu phi chức năng của hệ thống. Qua đó, xác định rõ ràng phạm vi và yêu cầu cần phát triển cho hệ thống.

---

## 2.1 Khảo sát hiện trạng

### 2.1.1 Nhu cầu thực tế

Trong bối cảnh chuyển đổi số và ứng dụng trí tuệ nhân tạo (AI) ngày càng phổ biến, nhu cầu về các công cụ hỗ trợ phân tích tài liệu và tạo nội dung tự động ngày càng tăng cao. Các đối tượng sử dụng chính bao gồm:

- **Giáo viên/Giảng viên**: Cần công cụ tạo slide bài giảng nhanh chóng từ tài liệu có sẵn, tạo bài kiểm tra trắc nghiệm tự động
- **Sinh viên/Học sinh**: Cần công cụ tóm tắt tài liệu, hỏi đáp với nội dung học tập
- **Nhân viên văn phòng**: Cần phân tích báo cáo, tạo bản trình bày từ tài liệu dự án
- **Nghiên cứu sinh**: Cần công cụ phân tích, tổng hợp nhiều tài liệu nghiên cứu

### 2.1.2 Khảo sát các hệ thống tương tự

| Tiêu chí | ChatGPT (OpenAI) | Google Gemini | Gamma.app | Beautiful.ai | **AI NVCB** |
|----------|------------------|---------------|-----------|--------------|-------------|
| **Phân tích tài liệu** | ✓ (giới hạn) | ✓ | ✗ | ✗ | ✓ (đa định dạng) |
| **Tạo slide tự động** | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Tạo quiz trắc nghiệm** | ✓ (thủ công) | ✓ (thủ công) | ✗ | ✗ | ✓ (tự động) |
| **Hỏi đáp tài liệu (RAG)** | ✓ (có phí) | ✓ | ✗ | ✗ | ✓ |
| **Triển khai nội bộ** | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Tùy chỉnh model AI** | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Chi phí** | Cao | Trung bình | Cao | Cao | Miễn phí/Thấp |
| **Bảo mật dữ liệu** | Cloud | Cloud | Cloud | Cloud | On-premise |
| **Hỗ trợ tiếng Việt** | Tốt | Tốt | Trung bình | Kém | Tốt |
| **Xuất file PPTX** | ✗ | ✗ | ✓ | ✓ | ✓ |

### 2.1.3 Đánh giá ưu nhược điểm các hệ thống hiện có

**ChatGPT/Google Gemini:**
- *Ưu điểm*: Khả năng xử lý ngôn ngữ tự nhiên mạnh mẽ, giao diện thân thiện
- *Nhược điểm*: Chi phí cao, dữ liệu được gửi lên cloud, không tạo slide trực tiếp, giới hạn kích thước file

**Gamma.app/Beautiful.ai:**
- *Ưu điểm*: Tạo slide đẹp, nhiều template
- *Nhược điểm*: Không phân tích tài liệu, không hỏi đáp, chi phí cao, không triển khai nội bộ

### 2.1.4 Tính năng cần phát triển cho AI NVCB

Dựa trên khảo sát, hệ thống AI NVCB cần đáp ứng các tính năng chính:

1. **Phân tích tài liệu đa định dạng**: Hỗ trợ PDF, DOCX, TXT, MD
2. **Hỏi đáp thông minh (RAG)**: Trả lời câu hỏi dựa trên nội dung tài liệu
3. **Tạo slide tự động**: Sinh bản trình bày PowerPoint từ nội dung
4. **Tạo bài trắc nghiệm**: Tự động tạo câu hỏi kiểm tra từ tài liệu
5. **Quản lý model AI**: Cho phép thay đổi model LLM linh hoạt
6. **Triển khai on-premise**: Bảo mật dữ liệu, không cần internet

---

## 2.2 Tổng quan chức năng

### 2.2.1 Biểu đồ use case tổng quát

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HỆ THỐNG AI NVCB                                  │
│                                                                             │
│  ┌─────────────────────┐    ┌─────────────────────┐                        │
│  │  Phân tích tài liệu │    │   Tạo Slide AI      │                        │
│  └─────────────────────┘    └─────────────────────┘                        │
│            ▲                          ▲                                     │
│            │                          │                                     │
│  ┌─────────┴─────────────────────────┴─────────┐                           │
│  │                                              │                           │
│  │              ┌──────────────┐               │                           │
│  │              │  Người dùng  │               │                           │
│  │              └──────────────┘               │                           │
│  │                    │                        │                           │
│  └────────────────────┼────────────────────────┘                           │
│                       │                                                     │
│            ▼                          ▼                                     │
│  ┌─────────────────────┐    ┌─────────────────────┐                        │
│  │ Tạo bài trắc nghiệm │    │   Quản lý Model AI  │                        │
│  └─────────────────────┘    └─────────────────────┘                        │
│                                       ▲                                     │
│                                       │                                     │
│                              ┌────────┴────────┐                           │
│                              │  Quản trị viên  │                           │
│                              └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Các tác nhân (Actors):**

| Tác nhân | Vai trò | Mô tả |
|----------|---------|-------|
| **Người dùng (User)** | Tác nhân chính | Sử dụng các chức năng phân tích tài liệu, tạo slide, tạo quiz, hỏi đáp với hệ thống |
| **Quản trị viên (Admin)** | Tác nhân quản trị | Quản lý model AI, cấu hình hệ thống, theo dõi hiệu suất |

**Mô tả các use case chính:**

| Use Case | Mô tả |
|----------|-------|
| **UC01: Phân tích tài liệu** | Người dùng tải lên tài liệu để hệ thống phân tích, tóm tắt và hỏi đáp |
| **UC02: Tạo Slide AI** | Hệ thống tự động tạo bản trình bày PowerPoint từ nội dung tài liệu |
| **UC03: Tạo bài trắc nghiệm** | Tự động sinh câu hỏi trắc nghiệm từ nội dung tài liệu đã tải lên |
| **UC04: Quản lý Model AI** | Quản trị viên quản lý, cài đặt và cấu hình các model LLM |

---

### 2.2.2 Biểu đồ use case phân rã - Phân tích tài liệu

```
┌───────────────────────────────────────────────────────────────────┐
│                    PHÂN TÍCH TÀI LIỆU                             │
│                                                                   │
│    ┌─────────────────┐                                           │
│    │  Tải tài liệu   │ ◄─────────────────────┐                   │
│    └─────────────────┘                       │                   │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐              ┌────────┴───────┐           │
│    │  Tóm tắt nội    │              │   Người dùng   │           │
│    │     dung        │ ◄────────────┤                │           │
│    └─────────────────┘              └────────┬───────┘           │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐                       │                   │
│    │  Hỏi đáp tài    │ ◄─────────────────────┘                   │
│    │     liệu (Q&A)  │                                           │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Xem lịch sử    │                                           │
│    │  hội thoại      │                                           │
│    └─────────────────┘                                           │
└───────────────────────────────────────────────────────────────────┘
```

**Mô tả các use case phân rã:**

| Use Case | Mô tả |
|----------|-------|
| **UC01.1: Tải tài liệu** | Người dùng tải lên 1 hoặc nhiều tài liệu (PDF, DOCX, TXT, MD) |
| **UC01.2: Tóm tắt nội dung** | Hệ thống AI tự động tóm tắt nội dung chính của tài liệu |
| **UC01.3: Hỏi đáp tài liệu (Q&A)** | Người dùng đặt câu hỏi và nhận câu trả lời dựa trên nội dung tài liệu (RAG) |
| **UC01.4: Xem lịch sử hội thoại** | Xem lại các câu hỏi và trả lời trước đó |

---

### 2.2.3 Biểu đồ use case phân rã - Tạo Slide AI

```
┌───────────────────────────────────────────────────────────────────┐
│                      TẠO SLIDE AI                                 │
│                                                                   │
│    ┌─────────────────┐                                           │
│    │  Nhập chủ đề/   │ ◄─────────────────────┐                   │
│    │  tải tài liệu   │                       │                   │
│    └─────────────────┘                       │                   │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐              ┌────────┴───────┐           │
│    │  Cấu hình số    │              │   Người dùng   │           │
│    │  lượng slide    │ ◄────────────┤                │           │
│    └─────────────────┘              └────────┬───────┘           │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐                       │                   │
│    │  Chọn model AI  │ ◄─────────────────────┘                   │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Tạo và xem     │                                           │
│    │  trước slide    │                                           │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Tải xuống file │                                           │
│    │  PPTX           │                                           │
│    └─────────────────┘                                           │
└───────────────────────────────────────────────────────────────────┘
```

**Mô tả các use case phân rã:**

| Use Case | Mô tả |
|----------|-------|
| **UC02.1: Nhập chủ đề/tải tài liệu** | Người dùng nhập chủ đề hoặc tải tài liệu làm nguồn nội dung |
| **UC02.2: Cấu hình số lượng slide** | Chọn số lượng slide mong muốn (1-20 slide) |
| **UC02.3: Chọn model AI** | Lựa chọn model AI phù hợp để tạo nội dung |
| **UC02.4: Tạo và xem trước slide** | Hệ thống tạo slide và hiển thị preview |
| **UC02.5: Tải xuống file PPTX** | Tải file PowerPoint về máy |

---

### 2.2.4 Biểu đồ use case phân rã - Tạo bài trắc nghiệm

```
┌───────────────────────────────────────────────────────────────────┐
│                   TẠO BÀI TRẮC NGHIỆM                             │
│                                                                   │
│    ┌─────────────────┐                                           │
│    │  Tải tài liệu   │ ◄─────────────────────┐                   │
│    │  nguồn          │                       │                   │
│    └─────────────────┘                       │                   │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐              ┌────────┴───────┐           │
│    │  Cấu hình số    │              │   Người dùng   │           │
│    │  câu hỏi        │ ◄────────────┤                │           │
│    └─────────────────┘              └────────┬───────┘           │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐                       │                   │
│    │  Chọn độ khó    │ ◄─────────────────────┘                   │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Tạo bài trắc   │                                           │
│    │  nghiệm         │                                           │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Xem kết quả    │                                           │
│    │  và đáp án      │                                           │
│    └─────────────────┘                                           │
└───────────────────────────────────────────────────────────────────┘
```

**Mô tả các use case phân rã:**

| Use Case | Mô tả |
|----------|-------|
| **UC03.1: Tải tài liệu nguồn** | Tải lên 1 hoặc nhiều tài liệu làm nguồn tạo câu hỏi |
| **UC03.2: Cấu hình số câu hỏi** | Chọn số lượng câu hỏi (5-20 câu) |
| **UC03.3: Chọn độ khó** | Chọn mức độ: Dễ, Trung bình, Khó |
| **UC03.4: Tạo bài trắc nghiệm** | Hệ thống AI tự động tạo câu hỏi và đáp án |
| **UC03.5: Xem kết quả và đáp án** | Hiển thị bài trắc nghiệm với đáp án đúng |

---

### 2.2.5 Biểu đồ use case phân rã - Quản lý Model AI

```
┌───────────────────────────────────────────────────────────────────┐
│                    QUẢN LÝ MODEL AI                               │
│                                                                   │
│    ┌─────────────────┐                                           │
│    │  Xem danh sách  │ ◄─────────────────────┐                   │
│    │  model          │                       │                   │
│    └─────────────────┘                       │                   │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐              ┌────────┴───────┐           │
│    │  Tải model mới  │              │  Quản trị viên │           │
│    │  (Pull)         │ ◄────────────┤                │           │
│    └─────────────────┘              └────────┬───────┘           │
│            │                                 │                   │
│            ▼                                 │                   │
│    ┌─────────────────┐                       │                   │
│    │  Chọn model     │ ◄─────────────────────┘                   │
│    │  mặc định       │                                           │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Xóa model      │                                           │
│    └─────────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  Cấu hình       │                                           │
│    │  System Prompt  │                                           │
│    └─────────────────┘                                           │
└───────────────────────────────────────────────────────────────────┘
```

**Mô tả các use case phân rã:**

| Use Case | Mô tả |
|----------|-------|
| **UC04.1: Xem danh sách model** | Hiển thị tất cả model đã cài đặt với thông tin chi tiết |
| **UC04.2: Tải model mới (Pull)** | Tải model mới từ Ollama registry |
| **UC04.3: Chọn model mặc định** | Đặt model mặc định cho hệ thống |
| **UC04.4: Xóa model** | Gỡ bỏ model không sử dụng để giải phóng bộ nhớ |
| **UC04.5: Cấu hình System Prompt** | Tùy chỉnh hành vi AI thông qua system prompt |

---

### 2.2.6 Quy trình nghiệp vụ

#### Quy trình 1: Tạo bài giảng từ tài liệu

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    QUY TRÌNH TẠO BÀI GIẢNG TỪ TÀI LIỆU                       │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│  Bắt đầu         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  Tải tài liệu    │────►│  Phân tích và    │
│  lên hệ thống    │     │  tóm tắt nội dung│
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Nội dung đã     │
                         │  phù hợp?        │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │ Không       │             │ Có
                    ▼             │             ▼
           ┌──────────────┐       │    ┌──────────────────┐
           │  Hỏi đáp để  │───────┘    │  Tạo Slide AI    │
           │  bổ sung     │            │  từ nội dung     │
           └──────────────┘            └────────┬─────────┘
                                                │
                                                ▼
                                       ┌──────────────────┐
                                       │  Tải file PPTX   │
                                       └────────┬─────────┘
                                                │
                                                ▼
                                       ┌──────────────────┐
                                       │  Tạo bài trắc    │
                                       │  nghiệm kiểm tra │
                                       └────────┬─────────┘
                                                │
                                                ▼
                                       ┌──────────────────┐
                                       │  Kết thúc        │
                                       └──────────────────┘
```

**Mô tả quy trình:**
1. Giáo viên tải tài liệu bài giảng (PDF, DOCX) lên hệ thống
2. Hệ thống phân tích và tóm tắt nội dung chính
3. Nếu cần bổ sung thông tin, sử dụng chức năng hỏi đáp Q&A
4. Tạo slide bài giảng tự động từ nội dung đã phân tích
5. Tải xuống file PowerPoint
6. Tạo bài trắc nghiệm để kiểm tra học viên

---

## 2.3 Đặc tả chức năng

### 2.3.1 Đặc tả use case: Tải và phân tích tài liệu (UC01.1, UC01.2)

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên use case** | Tải và phân tích tài liệu |
| **Mã use case** | UC01 |
| **Tác nhân** | Người dùng |
| **Mô tả** | Người dùng tải lên tài liệu và hệ thống phân tích, tóm tắt nội dung |

**Tiền điều kiện:**
- Hệ thống đang hoạt động bình thường
- Model AI đã được cấu hình và sẵn sàng
- File tài liệu có định dạng hỗ trợ (PDF, DOCX, TXT, MD)

**Luồng sự kiện chính:**
1. Người dùng truy cập trang "Phân tích tài liệu"
2. Người dùng chọn file tài liệu từ máy tính (1 hoặc nhiều file)
3. Hệ thống kiểm tra định dạng và kích thước file
4. Hệ thống tải file lên server và lưu trữ tạm thời
5. Người dùng chọn loại phân tích "Tóm tắt"
6. Hệ thống trích xuất nội dung văn bản từ tài liệu
7. Hệ thống gửi nội dung đến model AI để phân tích
8. Model AI xử lý và tạo bản tóm tắt
9. Hệ thống hiển thị kết quả tóm tắt cho người dùng
10. Hệ thống lưu document_id để sử dụng cho các thao tác tiếp theo

**Luồng sự kiện phát sinh:**

| Bước | Điều kiện | Xử lý |
|------|-----------|-------|
| 3a | File không đúng định dạng | Hiển thị thông báo lỗi, yêu cầu chọn file khác |
| 3b | File vượt quá kích thước cho phép | Hiển thị cảnh báo, đề xuất chia nhỏ file |
| 7a | Model AI không phản hồi | Hiển thị lỗi kết nối, đề xuất thử lại hoặc đổi model |
| 8a | Nội dung chứa ký tự không hợp lệ | Hệ thống tự động làm sạch (sanitize) nội dung |

**Hậu điều kiện:**
- Tài liệu được lưu trữ trong hệ thống với document_id duy nhất
- Bản tóm tắt được hiển thị và lưu vào lịch sử
- Người dùng có thể tiếp tục hỏi đáp với tài liệu

---

### 2.3.2 Đặc tả use case: Hỏi đáp tài liệu (UC01.3)

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên use case** | Hỏi đáp tài liệu (Q&A với RAG) |
| **Mã use case** | UC01.3 |
| **Tác nhân** | Người dùng |
| **Mô tả** | Người dùng đặt câu hỏi và nhận câu trả lời dựa trên nội dung tài liệu |

**Tiền điều kiện:**
- Tài liệu đã được tải lên và phân tích (UC01.1 hoàn thành)
- Document_id hợp lệ tồn tại trong hệ thống

**Luồng sự kiện chính:**
1. Người dùng nhập câu hỏi vào ô chat
2. Hệ thống nhận câu hỏi và document_id hiện tại
3. Hệ thống sử dụng kỹ thuật RAG (Retrieval-Augmented Generation):
   - Tạo embedding cho câu hỏi
   - Tìm kiếm các đoạn văn bản liên quan từ vector store
   - Kết hợp câu hỏi với context để tạo prompt
4. Gửi prompt đến model AI
5. Model AI phân tích và tạo câu trả lời
6. Hệ thống hiển thị câu trả lời cho người dùng
7. Lưu câu hỏi và câu trả lời vào lịch sử hội thoại

**Luồng sự kiện phát sinh:**

| Bước | Điều kiện | Xử lý |
|------|-----------|-------|
| 2a | Document_id không hợp lệ | Yêu cầu tải lại tài liệu |
| 3a | Không tìm thấy context liên quan | Trả lời dựa trên kiến thức chung với disclaimer |
| 5a | Câu trả lời chứa ký tự không mong muốn | Tự động sanitize output |

**Hậu điều kiện:**
- Câu trả lời được hiển thị trong giao diện chat
- Lịch sử hội thoại được cập nhật
- Người dùng có thể tiếp tục đặt câu hỏi

---

### 2.3.3 Đặc tả use case: Tạo Slide AI (UC02)

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên use case** | Tạo Slide AI |
| **Mã use case** | UC02 |
| **Tác nhân** | Người dùng |
| **Mô tả** | Tự động tạo bản trình bày PowerPoint từ chủ đề hoặc tài liệu |

**Tiền điều kiện:**
- Model AI đã sẵn sàng
- Người dùng có chủ đề hoặc tài liệu nguồn

**Luồng sự kiện chính:**
1. Người dùng truy cập trang "Tạo Slide AI"
2. Người dùng nhập chủ đề slide HOẶC tải tài liệu nguồn
3. Người dùng cấu hình số lượng slide (mặc định: 5, tối đa: 20)
4. Người dùng chọn model AI (tùy chọn)
5. Người dùng nhấn nút "Tạo Slide"
6. Hệ thống xử lý:
   - Nếu có tài liệu: Trích xuất nội dung
   - Tạo prompt với cấu trúc JSON yêu cầu
   - Gửi đến model AI
7. Model AI tạo nội dung slide theo cấu trúc JSON
8. Hệ thống parse JSON và validate nội dung
9. Hệ thống gọi PowerPointGenerator để tạo file PPTX
10. Hiển thị preview nội dung slide
11. Người dùng tải xuống file PPTX

**Luồng sự kiện phát sinh:**

| Bước | Điều kiện | Xử lý |
|------|-----------|-------|
| 7a | JSON response không hợp lệ | Retry với prompt cải tiến |
| 8a | Nội dung slide có ký tự lỗi | Sanitize và tiếp tục |
| 9a | Lỗi tạo file PPTX | Hiển thị lỗi, đề xuất thử lại |

**Hậu điều kiện:**
- File PPTX được tạo và lưu trong thư mục output/slides
- Người dùng có thể tải xuống file
- Log được ghi nhận cho việc theo dõi

**Biểu đồ hoạt động:**

```
┌─────────┐
│  Bắt đầu│
└────┬────┘
     │
     ▼
┌─────────────────┐
│ Nhập chủ đề/    │
│ tải tài liệu    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cấu hình số     │
│ lượng slide     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Nhấn "Tạo Slide"│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Có tài liệu?    │─Yes─► Trích xuất      │
└────────┬────────┘     │ nội dung        │
         │ No           └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Tạo prompt và   │
            │ gửi đến AI      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Parse JSON      │
            │ response        │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Valid JSON?     │
            └────────┬────────┘
                     │
         ┌───────────┼───────────┐
         │ No        │           │ Yes
         ▼           │           ▼
┌─────────────────┐  │  ┌─────────────────┐
│ Retry/Báo lỗi   │──┘  │ Tạo file PPTX   │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Hiển thị preview│
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Tải xuống PPTX  │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    Kết thúc     │
                        └─────────────────┘
```

---

### 2.3.4 Đặc tả use case: Tạo bài trắc nghiệm (UC03)

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên use case** | Tạo bài trắc nghiệm |
| **Mã use case** | UC03 |
| **Tác nhân** | Người dùng |
| **Mô tả** | Tự động tạo câu hỏi trắc nghiệm từ nội dung tài liệu |

**Tiền điều kiện:**
- Tài liệu nguồn đã sẵn sàng
- Model AI đang hoạt động

**Luồng sự kiện chính:**
1. Người dùng truy cập trang "Tạo bài trắc nghiệm"
2. Người dùng tải lên tài liệu nguồn (1 hoặc nhiều file)
3. Người dùng cấu hình:
   - Số lượng câu hỏi (5-20 câu)
   - Độ khó (Dễ/Trung bình/Khó)
4. Người dùng nhấn "Tạo bài trắc nghiệm"
5. Hệ thống trích xuất nội dung từ tài liệu
6. Hệ thống tạo prompt yêu cầu tạo quiz với format chuẩn
7. Model AI tạo câu hỏi, đáp án và giải thích
8. Hệ thống parse và format kết quả
9. Hiển thị bài trắc nghiệm với đáp án

**Luồng sự kiện phát sinh:**

| Bước | Điều kiện | Xử lý |
|------|-----------|-------|
| 5a | Tài liệu quá ngắn | Cảnh báo và đề xuất thêm nội dung |
| 7a | Format câu hỏi không chuẩn | Sanitize và reformat tự động |
| 7b | Câu hỏi không bằng tiếng Việt | Thêm system prompt bắt buộc tiếng Việt |

**Hậu điều kiện:**
- Bài trắc nghiệm được hiển thị với format rõ ràng
- Đáp án đúng được đánh dấu
- Người dùng có thể copy hoặc xuất kết quả

---

### 2.3.5 Đặc tả use case: Quản lý Model AI (UC04)

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên use case** | Quản lý Model AI |
| **Mã use case** | UC04 |
| **Tác nhân** | Quản trị viên |
| **Mô tả** | Quản lý các model LLM: xem, tải, xóa, cấu hình |

**Tiền điều kiện:**
- Ollama server đang chạy
- Người dùng có quyền quản trị

**Luồng sự kiện chính:**
1. Quản trị viên truy cập trang "Quản lý Model AI"
2. Hệ thống hiển thị danh sách model đã cài đặt với thông tin:
   - Tên model
   - Kích thước
   - Thời gian sửa đổi
3. Quản trị viên có thể:
   - **Xem chi tiết**: Click vào model để xem thông tin
   - **Đặt mặc định**: Chọn model làm mặc định cho hệ thống
   - **Tải model mới**: Nhập tên model từ Ollama registry và pull
   - **Xóa model**: Xóa model không sử dụng
   - **Cấu hình System Prompt**: Thiết lập hành vi AI mặc định

**Luồng sự kiện phát sinh:**

| Bước | Điều kiện | Xử lý |
|------|-----------|-------|
| 3a | Ollama server không phản hồi | Hiển thị lỗi kết nối |
| 3b | Model pull thất bại | Hiển thị chi tiết lỗi, đề xuất kiểm tra tên model |
| 3c | Không đủ dung lượng để tải model | Cảnh báo và đề xuất xóa model cũ |

**Hậu điều kiện:**
- Danh sách model được cập nhật
- Model mặc định được lưu vào cấu hình
- System prompt được áp dụng cho các request tiếp theo

---

### 2.3.6 Đặc tả use case: Xem lịch sử hội thoại (UC01.4)

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên use case** | Xem lịch sử hội thoại |
| **Mã use case** | UC01.4 |
| **Tác nhân** | Người dùng |
| **Mô tả** | Xem lại các câu hỏi và trả lời trước đó |

**Tiền điều kiện:**
- Có ít nhất một cuộc hội thoại đã thực hiện
- Document_id hợp lệ

**Luồng sự kiện chính:**
1. Người dùng vào trang phân tích tài liệu
2. Hệ thống tự động load lịch sử hội thoại theo document_id
3. Hiển thị danh sách các câu hỏi và câu trả lời theo thời gian
4. Người dùng có thể:
   - Cuộn xem các tin nhắn cũ
   - Tiếp tục hội thoại từ context trước

**Hậu điều kiện:**
- Lịch sử hội thoại được hiển thị đầy đủ
- Context được duy trì cho các câu hỏi tiếp theo

---

## 2.4 Yêu cầu phi chức năng

### 2.4.1 Yêu cầu về hiệu năng

| Yêu cầu | Mô tả | Chỉ tiêu |
|---------|-------|----------|
| **NFR01** | Thời gian phản hồi tóm tắt tài liệu | < 30 giây cho file < 10MB |
| **NFR02** | Thời gian tạo slide | < 60 giây cho 10 slide |
| **NFR03** | Thời gian tạo quiz | < 45 giây cho 10 câu hỏi |
| **NFR04** | Số người dùng đồng thời | Tối thiểu 10 users |
| **NFR05** | Kích thước file tối đa | 50MB cho mỗi file |

### 2.4.2 Yêu cầu về độ tin cậy

| Yêu cầu | Mô tả |
|---------|-------|
| **NFR06** | Hệ thống hoạt động 99% uptime trong giờ làm việc |
| **NFR07** | Tự động retry khi model AI không phản hồi (tối đa 3 lần) |
| **NFR08** | Backup dữ liệu định kỳ (daily) |
| **NFR09** | Auto cleanup file tạm sau 24 giờ |

### 2.4.3 Yêu cầu về tính dễ dùng

| Yêu cầu | Mô tả |
|---------|-------|
| **NFR10** | Giao diện thân thiện, responsive trên desktop |
| **NFR11** | Hỗ trợ hoàn toàn tiếng Việt (UI và output) |
| **NFR12** | Hiển thị trạng thái xử lý realtime (loading, progress) |
| **NFR13** | Thông báo lỗi rõ ràng, có hướng dẫn khắc phục |

### 2.4.4 Yêu cầu về bảo mật

| Yêu cầu | Mô tả |
|---------|-------|
| **NFR14** | Triển khai on-premise, dữ liệu không gửi ra ngoài |
| **NFR15** | File tải lên được lưu trữ tạm và tự động xóa |
| **NFR16** | API có CORS protection |
| **NFR17** | Không log nội dung nhạy cảm của tài liệu |

### 2.4.5 Yêu cầu về tính dễ bảo trì

| Yêu cầu | Mô tả |
|---------|-------|
| **NFR18** | Code được tổ chức theo kiến trúc phân lớp (Frontend/Backend/Services) |
| **NFR19** | Logging đầy đủ cho debugging và monitoring |
| **NFR20** | Hỗ trợ hot-reload cho development |
| **NFR21** | Docker containerization cho deployment dễ dàng |

### 2.4.6 Yêu cầu về công nghệ

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| **Backend Framework** | FastAPI | 0.115.0+ |
| **Frontend Framework** | Streamlit | 1.40.0+ |
| **AI/LLM Framework** | LangChain + Ollama | Latest |
| **Vector Database** | FAISS | Latest |
| **Embedding Model** | sentence-transformers | all-MiniLM-L6-v2 |
| **Database** | SQLite/PostgreSQL | - |
| **Cache** | Redis (optional) | - |
| **Container** | Docker | 20.0+ |
| **Reverse Proxy** | Nginx | Latest |
| **Programming Language** | Python | 3.11+ |

---

## Kết luận chương

Chương 2 đã trình bày chi tiết quá trình khảo sát hiện trạng và phân tích yêu cầu cho hệ thống AI NVCB. Qua việc khảo sát các hệ thống tương tự trên thị trường (ChatGPT, Google Gemini, Gamma.app, Beautiful.ai), đã xác định được các tính năng cần phát triển để tạo nên lợi thế cạnh tranh: phân tích tài liệu đa định dạng, tạo slide tự động, tạo quiz trắc nghiệm, và khả năng triển khai on-premise.

Biểu đồ use case tổng quát và các biểu đồ phân rã đã mô tả đầy đủ các chức năng của hệ thống với hai tác nhân chính: Người dùng và Quản trị viên. Đặc tả chi tiết 6 use case quan trọng nhất đã làm rõ luồng sự kiện chính, luồng phát sinh, tiền điều kiện và hậu điều kiện cho từng chức năng.

Các yêu cầu phi chức năng về hiệu năng, độ tin cậy, tính dễ dùng, bảo mật, bảo trì và công nghệ đã được xác định cụ thể với các chỉ tiêu đo lường (NFR01-NFR21). Bảng yêu cầu công nghệ tại mục 2.4.6 đã liệt kê sơ bộ các công nghệ dự kiến sử dụng, sẽ được phân tích chi tiết và giải thích lý do lựa chọn trong Chương 3.

Các yêu cầu chức năng (UC01-UC04) và phi chức năng (NFR01-NFR21) được xác định trong chương này là cơ sở để tiến hành lựa chọn công nghệ (Chương 3), thiết kế kiến trúc và triển khai hệ thống (Chương 4).
