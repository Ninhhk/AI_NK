# 📖 Hướng Dẫn Sử Dụng Scripts Tiện Ích

Tài liệu này hướng dẫn cách sử dụng các scripts tiện ích để thiết lập và dọn dẹp hệ thống AI NVCB.

## 🔧 1. Script Thiết Lập Môi Trường (`copy_env.py`)

### Mục đích
Script này sao chép cấu hình từ file `.env.example` sang `.env` để thiết lập môi trường làm việc.

### Khi nào sử dụng
- ✅ Lần đầu tiên cài đặt ứng dụng
- ✅ Khi muốn reset cấu hình về mặc định
- ✅ Khi file `.env` bị lỗi hoặc mất
- ✅ Khi thiết lập trên máy tính mới

### Cách sử dụng

#### Bước 1: Mở PowerShell
```powershell
# Nhấn Windows + R, gõ "powershell" và nhấn Enter
```

#### Bước 2: Di chuyển đến thư mục dự án(nếu chưa vào)
```powershell
cd ".\AI_NVCB"
```

#### Bước 3: Chạy script
```powershell
python copy_env.py
```

### Ví dụ chạy script
```
🔧 AI NVCB Environment Setup
========================================
Copying .env.example to .env...

⚠️  Warning: .env file already exists!
   Do you want to overwrite it? (y/N): y

✅ Successfully copied .env.example to .env

📄 Content of .env file:
----------------------------------------
MODEL_NAME=qwen3:8b
OLLAMA_BASE_URL=http://localhost:11434
----------------------------------------

🎉 Environment setup completed!
💡 You can now run the application with:
   python run_backend.py
   python run_frontend.py
```

### Lưu ý quan trọng
- ⚠️ Nếu đã có file `.env`, script sẽ hỏi có muốn ghi đè không
- ✅ Trả lời `y` hoặc `yes` để ghi đè <- khuyến khích 
- ✅ Trả lời `n` hoặc `no` để hủy bỏ

---

## 🧹 2. Script Dọn Dẹp Model (`simple_cleanup.py`)

### Mục đích
Script này giúp dọn dẹp các AI model không sử dụng trong Ollama để tiết kiệm dung lượng ổ cứng.

### Khi nào sử dụng
- ✅ Khi ổ cứng sắp đầy
- ✅ Khi có quá nhiều model không dùng
- ✅ Khi muốn chỉ giữ lại model đang sử dụng
- ✅ Để tối ưu hóa hiệu suất hệ thống

### Cách sử dụng

#### Bước 1: Mở PowerShell
```powershell
# Nhấn Windows + R, gõ "powershell" và nhấn Enter
```

#### Bước 2: Di chuyển đến thư mục dự án
```powershell
cd ".\AI_NVCB"
```

#### Bước 3: Chạy script
```powershell
python simple_cleanup.py
```

### Ví dụ chạy script
```
🧹 Ollama Model Cleanup Tool
============================

📋 Tìm thấy các model:
1. qwen3:8b (đang sử dụng) ✅
2. qwen2.5:7b (không sử dụng) ❌
3. mistral:7b (không sử dụng) ❌

🗑️ Model sẽ bị xóa:
- qwen2.5:7b
- mistral:7b

⚠️ Bạn có chắc chắn muốn xóa? (y/N): y

✅ Đã xóa: qwen2.5:7b
✅ Đã xóa: mistral:7b

🎉 Dọn dẹp hoàn tất! Tiết kiệm được ~8.5 GB
```

### Các tùy chọn nâng cao
```powershell
# Chỉ xem danh sách model (không xóa)
python simple_cleanup.py --dry-run

# Bỏ qua xác nhận (cẩn thận!)
python simple_cleanup.py --force

# Giữ lại model cụ thể
python simple_cleanup.py --keep mistral:7b
```

### Lưu ý quan trọng
- ⚠️ **QUAN TRỌNG**: Script sẽ XÓA VĨNH VIỄN các model không sử dụng
- ✅ Model đang được cấu hình trong `.env` sẽ được bảo vệ
- ✅ Có thể sử dụng `--dry-run` để xem trước không xóa
- 🔄 Có thể tải lại model đã xóa bằng `ollama pull <tên_model>`

---

## 🚀 3. Quy Trình Thiết Lập Hoàn Chỉnh

### Cho người dùng mới
```powershell
# 1. Thiết lập môi trường
python copy_env.py

# 2. Khởi động backend
python run_backend.py

# 3. Mở terminal mới và khởi động frontend
python run_frontend.py

# 4. Truy cập ứng dụng tại: http://localhost:8501
```

### Cho việc bảo trì định kỳ
```powershell
# 1. Dọn dẹp model không cần thiết
python simple_cleanup.py

# 2. Kiểm tra cấu hình môi trường
python copy_env.py

# 3. Khởi động lại ứng dụng
python run_backend.py
python run_frontend.py
```

---

## ❓ Khắc Phục Sự Cố

### Lỗi phổ biến và cách khắc phục

#### 1. Lỗi "File not found"
```
❌ Error: .env.example file not found!
```
**Giải pháp**: Đảm bảo bạn đang ở đúng thư mục dự án
vd:
```powershell
cd "c:\Users\ADMIN\Test_Gen_slide\AI_NVCB\AI_NVCB"
```

#### 2. Lỗi "Permission denied"
```
❌ Error: Permission denied!
```
**Giải pháp**: Chạy PowerShell với quyền Administrator
```powershell
# Nhấn chuột phải vào PowerShell và chọn "Run as Administrator"
```

#### 3. Lỗi "Python command not found"
```
'python' is not recognized...
```
**Giải pháp**: Cài đặt Python hoặc sử dụng `py` thay vì `python`
```powershell
py copy_env.py
py simple_cleanup.py
```

#### 4. Ollama không khả dụng
```
❌ Error: Could not connect to Ollama
```
**Giải pháp**: Khởi động Ollama trước khi chạy cleanup
```powershell
ollama ps
```

---

## 📞 Hỗ Trợ

### Khi cần trợ giúp
1. **Kiểm tra log**: Đọc thông báo lỗi chi tiết
2. **Thử lại**: Một số lỗi có thể tạm thời
3. **Khởi động lại**: Restart terminal và thử lại
4. **Kiểm tra quyền**: Đảm bảo có quyền ghi file

### File quan trọng cần backup
- 📄 `.env` - Cấu hình môi trường
- 📄 `documents.db` - Cơ sở dữ liệu tài liệu
- 📁 `storage/` - Dữ liệu người dùng

---

## 🔒 Bảo Mật

### Lưu ý bảo mật
- 🔐 File `.env` chứa thông tin nhạy cảm, không chia sẻ
- 🗑️ Script cleanup xóa vĩnh viễn, cẩn thận khi sử dụng
- 💾 Backup dữ liệu quan trọng trước khi dọn dẹp

---

*Tài liệu này được tạo cho AI NVCB - Hệ thống Phân tích Tài liệu và Tạo Slide Thông minh*
