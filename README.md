# AI-NVCB

An AI-powered application that combines document analysis and presentation generation capabilities.

## Features

- Document Analysis
  - PDF document processing and analysis
  - LLM-powered document summarization
  - Question answering on documents
  
- Presentation Generation
  - Automatic slide generation from content
  - Support for various input formats
  - Customizable presentation templates

## Project Structure

```
AI_NVCB/
├── frontend/        # Streamlit and Flask frontend applications
├── backend/         # Core backend services and API
├── utils/          # Shared utilities and helper functions
├── data/           # Data storage and resources
└── tests/          # Test suite
```

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **CPU**: Minimum 4 cores (8+ cores recommended for better performance)
- **RAM**: Minimum 8GB (16GB+ recommended)
- **GPU**: Optional but recommended for faster model inference (NVIDIA GPU with CUDA support)
- **Disk Space**: At least 10GB free space
- **Network**: Stable internet connection for model downloads

## Prerequisites

- **Python**: Version 3.8 or higher
- **Ollama**: Latest version for running local LLMs
- **Git**: For cloning the repository
- **Node.js**: Version 14+ (if using any JavaScript components)
- **PDF processing libraries**: System libraries for PyMuPDF/pdf2image (e.g., poppler on Linux/macOS)

## Installation

1. Install prerequisite software:
   - Install [Python 3.8+](https://www.python.org/downloads/)
   - Install [Ollama](https://ollama.ai/download)
   - Install [Git](https://git-scm.com/downloads)
   - Install system dependencies:
     - **Windows**: No additional steps needed
     - **macOS**: `brew install poppler`
     - **Linux**: `sudo apt-get install poppler-utils`

2. Clone the repository
   ```bash
   git clone https://github.com/Ninhhk/AI_NK.git
   cd AI_NK
   ```

3. Install Poetry (if not already installed):
   ```bash
   pip install poetry
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Set up environment variables(if there is no .env file):
   Create a `.env` file with:
   ```
   MODEL_NAME=qwen2.5:7b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

## Usage

1. Start Ollama server and ensure your model is available:
   ```bash
   ollama run qwen2.5:7b
   ```
   Wait for ollama to download the model(~5Gb). You can test prompt or press Ctrl+
<<<<<<< HEAD
   Wait for ollama to download the model(~5Gb). You can test prompt or press Ctrl+D to exit.

=======
   After successful run, you can try prompt the model with "hi" to check its response. Press Ctrl+D to quit.
>>>>>>> 534bf6eee10a45a0673dcf39ba6679f4c15b9472
2. Start the backend server:
   ```bash
   python run_backend.py
   ```
<<<<<<< HEAD
3. Start the frontend application on a different terminal(Ctrl+Shift+5 in VSCode):
=======
   Wait until the application finished startup.
3. Start the frontend application:
>>>>>>> 534bf6eee10a45a0673dcf39ba6679f4c15b9472
   ```bash
   streamlit run frontend/app.py
   ```
4. Access the application in your browser at http://localhost:8501
5. You may have to wait 1-2m for the backend server complete its startup.

## Development

- Use Poetry for dependency management
- Follow PEP 8 style guidelines
- Write tests for new features

## License

<<<<<<< HEAD
MIT License - See LICENSE file for details

## Vietnamese Translation / Bản dịch tiếng Việt

# AI-NVCB

Ứng dụng được hỗ trợ bởi AI kết hợp khả năng phân tích tài liệu và tạo bài thuyết trình.

## Tính năng

- Phân tích Tài liệu
  - Xử lý và phân tích tài liệu PDF
  - Tóm tắt tài liệu được hỗ trợ bởi LLM
  - Trả lời câu hỏi dựa trên tài liệu
  
- Tạo Bài Thuyết trình
  - Tự động tạo slide từ nội dung
  - Hỗ trợ nhiều định dạng đầu vào
  - Mẫu thuyết trình có thể tùy chỉnh

## Cấu trúc Dự án

```
AI_NVCB/
├── frontend/        # Ứng dụng frontend Streamlit và Flask
├── backend/         # Dịch vụ backend và API cốt lõi
├── utils/          # Tiện ích và hàm trợ giúp
├── data/           # Lưu trữ dữ liệu và tài nguyên
└── tests/          # Bộ kiểm thử
```

## Yêu cầu Hệ thống

- **Hệ điều hành**: Windows 10/11, macOS 10.15+, hoặc Linux (khuyến nghị Ubuntu 20.04+)
- **CPU**: Tối thiểu 4 lõi (khuyến nghị 8+ lõi để hiệu suất tốt hơn)
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB+)
- **GPU**: Tùy chọn nhưng được khuyến nghị để suy luận mô hình nhanh hơn (NVIDIA GPU hỗ trợ CUDA)
- **Dung lượng ổ đĩa**: Ít nhất 10GB không gian trống
- **Mạng**: Kết nối internet ổn định để tải mô hình

## Cài đặt

1. Cài đặt phần mềm tiên quyết:
   - Cài đặt [Python 3.8+](https://www.python.org/downloads/)
   - Cài đặt [Ollama](https://ollama.ai/download)
   - Cài đặt [Git](https://git-scm.com/downloads)

2. Sao chép kho lưu trữ
   ```bash
   git clone https://github.com/Ninhhk/AI_NK.git
   cd AI_NK
   ```

3. Cài đặt Poetry:
   ```bash
   pip install poetry
   ```

4. Cài đặt các phụ thuộc:
   ```bash
   poetry install
   ```

5. Khởi chạy ứng dụng:
   ```bash
   streamlit run frontend/app.py
   ```

## Sử dụng

1. Khởi động máy chủ Ollama và đảm bảo mô hình của bạn có sẵn:
   ```bash
   ollama run qwen2.5:7b
   ```
   Chờ Ollama tải xuống mô hình (~5Gb). Bạn có thể thử nhắc hoặc nhấn Ctrl+D để thoát.

2. Khởi động máy chủ backend:
   ```bash
   python run_backend.py
   ```

3. Khởi động ứng dụng frontend trên một terminal khác (Ctrl+Shift+5 trong VSCode):
   ```bash
   streamlit run frontend/app.py
   ```

4. Truy cập ứng dụng trong trình duyệt của bạn tại http://localhost:8501
5. Bạn có thể sẽ phải chờ 1-2p để backend hoàn thành việc khởi chạy.

## Phát triển

- Sử dụng Poetry để quản lý phụ thuộc
- Tuân theo các hướng dẫn phong cách PEP 8
- Viết kiểm thử cho các tính năng mới

## Giấy phép

Giấy phép MIT - Xem tệp LICENSE để biết chi tiết
=======
MIT License - See LICENSE file for details 
>>>>>>> 534bf6eee10a45a0673dcf39ba6679f4c15b9472
