# 📖 Hướng Dẫn Sử Dụng Script Tiện Ích AI NVCB

Tài liệu này hướng dẫn cách sử dụng script tiện ích để thiết lập và bảo trì hệ thống AI NVCB.

## 🌟 Script Chính - KHUYẾN NGHỊ SỬ DỤNG

### 🛠️ Script Tổng Hợp (`ai_nvcb_utility.py`) - ⭐ CHÍNH

Script **ALL-IN-ONE** này là công cụ chính được khuyến nghị, kết hợp tất cả chức năng cần thiết:

#### Chức năng
1. **Thiết lập môi trường**: Sao chép `.env.example` → `.env`
2. **Dọn dẹp AI models**: Xóa models không sử dụng để tiết kiệm dung lượng
3. **Menu tương tác**: Giao diện thân thiện, dễ sử dụng
4. **Tùy chọn dòng lệnh**: Hỗ trợ automation và scripting

#### Khi nào sử dụng
- ✅ **LẦN ĐẦU CÀI ĐẶT** - Thiết lập toàn bộ hệ thống
- ✅ **BẢO TRÌ ĐỊNH KỲ** - Dọn dẹp và tối ưu hóa
- ✅ **KHI GẶP LỖI** - Reset cấu hình về trạng thái ổn định
- ✅ **TIẾT KIỆM DUNG LƯỢNG** - Xóa models không cần thiết
- ✅ **TỰ ĐỘNG HÓA** - Sử dụng với scripts khác

## 🚀 Cách Sử Dụng Script Chính

### ⭐ Phương pháp 1: Chế độ Tương Tác (Khuyến nghị cho người mới)

#### Bước 1: Mở PowerShell
```powershell
# Nhấn Windows + R, gõ "powershell" và nhấn Enter
# HOẶC nhấn Windows + X và chọn "PowerShell"
```

#### Bước 2: Di chuyển đến thư mục dự án
```powershell
cd "c:\Users\ADMIN\Test_Gen_slide\AI_NVCB\AI_NVCB"
# HOẶC nếu bạn đã ở trong thư mục:
cd ".\AI_NVCB"
```

#### Bước 3: Chạy script tương tác
```powershell
python ai_nvcb_utility.py
```

#### Menu tương tác sẽ hiện ra:
```
🛠️  AI NVCB Utility Tool
==================================================
Công cụ tiện ích cho thiết lập và bảo trì hệ thống

📋 Chọn chức năng:
1. 🔧 Thiết lập môi trường (.env.example → .env)
2. 🧹 Dọn dẹp AI models không sử dụng
3. 🚀 Thực hiện cả hai (thiết lập + dọn dẹp)
4. ❌ Thoát

Nhập lựa chọn (1-4):
```

#### Chi tiết từng lựa chọn:

**🔧 Lựa chọn 1 - Thiết lập môi trường**
- Sao chép `.env.example` thành `.env`
- Hiển thị nội dung file `.env` để kiểm tra
- Thông báo kết quả thành công/thất bại

**🧹 Lựa chọn 2 - Dọn dẹp models**
- Liệt kê tất cả models hiện có
- Hiển thị model nào sẽ được giữ lại/xóa
- Ước tính dung lượng tiết kiệm được
- Yêu cầu xác nhận trước khi xóa

**🚀 Lựa chọn 3 - Thực hiện cả hai**
- Chạy thiết lập môi trường trước
- Sau đó chạy dọn dẹp models
- Tự động hoàn thành toàn bộ quá trình

### ⚡ Phương pháp 2: Dòng Lệnh (Cho người dùng nâng cao)

#### Các tùy chọn có sẵn:
```powershell
# Xem tất cả tùy chọn
python ai_nvcb_utility.py --help

# Chỉ thiết lập môi trường
python ai_nvcb_utility.py --env-only

# Chỉ dọn dẹp models
python ai_nvcb_utility.py --cleanup-only

# Thực hiện cả hai
python ai_nvcb_utility.py --both

# Xem trước models sẽ bị xóa (không xóa thực tế)
python ai_nvcb_utility.py --cleanup-only --dry-run

# Dọn dẹp models nhưng giữ lại model cụ thể
python ai_nvcb_utility.py --cleanup-only --keep mistral:7b

# Tự động thực hiện không cần xác nhận (CẨN THẬN!)
python ai_nvcb_utility.py --cleanup-only --force
```

#### Ví dụ thực tế:
```powershell
# Thiết lập lần đầu tiên (môi trường + dọn dẹp)
python ai_nvcb_utility.py --both

# Bảo trì định kỳ (chỉ dọn dẹp models)
python ai_nvcb_utility.py --cleanup-only

# Kiểm tra trước khi dọn dẹp
python ai_nvcb_utility.py --cleanup-only --dry-run

# Giữ lại nhiều models
python ai_nvcb_utility.py --cleanup-only --keep llama2:7b --keep mistral:7b
```

---

## 📚 Scripts Phụ Trợ (Tùy Chọn)

> **Lưu ý**: Các script dưới đây vẫn có thể sử dụng riêng lẻ, nhưng khuyến nghị dùng script chính `ai_nvcb_utility.py` ở trên.

### 🔧 1. Script Thiết Lập Môi Trường (`copy_env.py`)

#### Mục đích
Script riêng lẻ để sao chép file `.env.example` thành `.env`.

#### Cách sử dụng
```powershell
python copy_env.py
```

#### Ví dụ kết quả
```
🔧 AI NVCB Environment Setup
========================================
Copying .env.example to .env...

✅ Successfully copied .env.example to .env

📄 Content of .env file:
----------------------------------------
MODEL_NAME=qwen3:8b
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001
FRONTEND_PORT=8501
----------------------------------------

🎉 Environment setup completed!
💡 You can now run the application with:
   python run_backend.py
   python run_frontend.py
```

### Phương pháp 2: Chế độ Dòng Lệnh (Nâng cao)

```powershell
# Chỉ thiết lập môi trường
python ai_nvcb_utility.py --env-only

# Chỉ dọn dẹp models
python ai_nvcb_utility.py --cleanup-only

# Thực hiện cả hai
python ai_nvcb_utility.py --both

# Xem trước models sẽ bị xóa (không xóa thực tế)
python ai_nvcb_utility.py --cleanup-only --dry-run

# Giữ lại model cụ thể
python ai_nvcb_utility.py --cleanup-only --keep mistral:7b

# Bỏ qua xác nhận (cẩn thận!)
python ai_nvcb_utility.py --cleanup-only --force
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

## ✨ Thực Tiễn Tốt Nhất

### 🎯 Khi nào sử dụng script nào

#### Script Chính (`ai_nvcb_utility.py`) - Sử dụng cho:
- ✅ **Lần đầu cài đặt** → Chọn option 3 (thực hiện cả hai)
- ✅ **Bảo trì hàng tuần** → Chọn option 2 (dọn dẹp models)
- ✅ **Khi gặp lỗi** → Chọn option 1 (thiết lập môi trường)
- ✅ **Kiểm tra trước khi xóa** → `--dry-run`

#### Scripts riêng lẻ - Sử dụng khi:
- 🔧 Chỉ cần thiết lập môi trường: `copy_env.py`
- 🧹 Chỉ cần dọn dẹp models: `simple_cleanup.py`
- 🔀 Tích hợp vào script khác

### 📋 Quy trình khuyến nghị

#### Lần đầu cài đặt:
```powershell
# 1. Thiết lập toàn bộ hệ thống
python ai_nvcb_utility.py --both

# 2. Kiểm tra kết quả
python run_backend.py   # Test backend
python run_frontend.py  # Test frontend
```

#### Bảo trì định kỳ (hàng tuần):
```powershell
# 1. Kiểm tra trước khi dọn dẹp
python ai_nvcb_utility.py --cleanup-only --dry-run

# 2. Dọn dẹp nếu hài lòng với kết quả
python ai_nvcb_utility.py --cleanup-only
```

#### Khi gặp lỗi:
```powershell
# 1. Reset cấu hình môi trường
python ai_nvcb_utility.py --env-only

# 2. Nếu vẫn lỗi, dọn dẹp models
python ai_nvcb_utility.py --cleanup-only
```

### 🛡️ An Toàn Dữ Liệu

#### Trước khi dọn dẹp models:
1. **Kiểm tra trước**: Luôn chạy `--dry-run` trước
2. **Backup quan trọng**: Sao lưu file `.env` và `documents.db`
3. **Ghi nhớ models**: Note lại tên models quan trọng để `--keep`

#### Models nên giữ lại:
```powershell
# Giữ lại model backup
python ai_nvcb_utility.py --cleanup-only --keep qwen2.5:7b

# Giữ lại nhiều models
python ai_nvcb_utility.py --cleanup-only --keep llama2:7b --keep mistral:7b
```

---

## ❓ Khắc Phục Sự Cố

### Lỗi phổ biến và cách khắc phục

#### 1. Lỗi "File not found" hoặc "Permission denied"
```
❌ Error: .env.example file not found!
❌ Error: Permission denied!
```
**Giải pháp**:
```powershell
# Kiểm tra đường dẫn hiện tại
pwd

# Di chuyển đến đúng thư mục
cd "c:\Users\ADMIN\Test_Gen_slide\AI_NVCB\AI_NVCB"

# Chạy PowerShell với quyền Administrator nếu cần
# (Nhấn chuột phải vào PowerShell và chọn "Run as Administrator")
```

#### 2. Lỗi "Python command not found"
```
'python' is not recognized...
```
**Giải pháp**:
```powershell
# Thử với 'py' thay vì 'python'
py ai_nvcb_utility.py

# Hoặc kiểm tra Python đã cài đặt chưa
python --version
```

#### 3. Ollama không khả dụng
```
❌ Lỗi: Không thể kết nối với Ollama
❌ Error: Could not connect to Ollama
```
**Giải pháp**:
```powershell
# Khởi động Ollama
ollama serve

# Kiểm tra trong terminal khác
ollama ps
ollama list
```

#### 4. Script bị treo hoặc không phản hồi
```
# Script đang chạy mà không có output
```
**Giải pháp**:
```powershell
# Nhấn Ctrl+C để dừng
# Thử lại với --force để bỏ qua confirmations
python ai_nvcb_utility.py --cleanup-only --force

# Hoặc kiểm tra Ollama có đang tải model không
ollama ps
```

#### 5. Models không bị xóa
```
❌ Lỗi khi xóa model: ...
```
**Giải pháp**:
```powershell
# Kiểm tra model có đang chạy không
ollama ps

# Dừng tất cả models đang chạy
# (Ctrl+C trong terminal đang chạy Ollama)

# Thử xóa thủ công
ollama rm <model_name>

# Sau đó chạy lại script
python ai_nvcb_utility.py --cleanup-only
```

### 🔧 Debug và Monitoring

#### Kiểm tra trạng thái hệ thống:
```powershell
# Kiểm tra Python
python --version

# Kiểm tra Ollama
ollama --version
ollama list
ollama ps

# Kiểm tra file cấu hình
type .env
```

#### Log files quan trọng:
- **Terminal output**: Tất cả messages hiển thị trong terminal
- **Ollama logs**: Thường ở `%APPDATA%\ollama\logs\`
- **Application logs**: Trong thư mục `storage/` hoặc `logs/`

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
