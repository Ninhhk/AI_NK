import os
from typing import Optional, Union, Dict, List, Any, Tuple
from pathlib import Path
import tempfile
import re
import unicodedata
import time
import uuid
import langdetect

from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from .config import OLLAMA_CONFIG, CHAT_HISTORY_ENABLED, MAX_CHAT_HISTORY_ITEMS

def is_chinese(char: str) -> bool:
    """Check if a character is Chinese."""
    try:
        return 'CJK' in unicodedata.name(char)
    except ValueError:
        return False

def contains_chinese(text: str) -> bool:
    """Check if text contains any Chinese characters."""
    return any(is_chinese(char) for char in text)

def is_predominantly_vietnamese(text: str) -> bool:
    """Check if text is predominantly Vietnamese."""
    try:
        # Use a sample of the text for language detection
        sample = text[:1000] if len(text) > 1000 else text
        detected_lang = langdetect.detect(sample)
        return detected_lang == 'vi'
    except:
        # If language detection fails, check for Vietnamese diacritics as a fallback
        vietnamese_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
        text_lower = text.lower()
        # Count Vietnamese specific characters
        vi_char_count = sum(1 for c in text_lower if c in vietnamese_chars)
        return vi_char_count > 0

def ensure_vietnamese_response(response: str) -> str:
    """Ensure the response is in Vietnamese or return a fallback message."""
    if not response or not is_predominantly_vietnamese(response):
        return """Xin lỗi, hệ thống không thể cung cấp câu trả lời bằng tiếng Việt cho yêu cầu của bạn.
Vui lòng thử lại với một văn bản hoặc câu hỏi khác.

(Lỗi: Phản hồi không phải bằng tiếng Việt như yêu cầu)"""
    return response

def sanitize_text(text: str) -> str:
    """Remove Chinese characters and clean up text."""
    # Remove Chinese characters
    cleaned = ''.join(char for char in text if not is_chinese(char))
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Remove multiple newlines
    cleaned = re.sub(r'\n+', '\n', cleaned)
    return cleaned.strip()

def sanitize_quiz_content(content: str) -> str:
    """Sanitize quiz content and ensure proper formatting."""
    # Only remove actual Chinese characters while preserving Vietnamese diacritics
    lines = content.split('\n')
    sanitized_lines = []
    
    for line in lines:
        if not line.strip():
            sanitized_lines.append('')
            continue
            
        # Remove only Chinese characters (not Vietnamese with diacritics)
        cleaned_line = ''.join(char for char in line if not is_chinese(char))
        cleaned_line = cleaned_line.strip()
        
        if not cleaned_line:
            continue
            
        # Format based on line type
        if re.match(r'^Câu\s+\d+', cleaned_line):
            sanitized_lines.extend(['', cleaned_line])  # Add blank line before question
        elif re.match(r'^[A-D]\.', cleaned_line):
            sanitized_lines.append(cleaned_line)
        elif 'Đáp án đúng:' in cleaned_line:
            sanitized_lines.extend([cleaned_line, ''])  # Add blank line after answer
        else:
            sanitized_lines.append(cleaned_line)
    
    # Join lines with proper newlines and ensure consistent spacing
    result = '\n'.join(sanitized_lines)
    
    # Clean up any multiple consecutive newlines
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()

class DocumentAnalysisService:
    def __init__(
        self,
        model_name: str = OLLAMA_CONFIG["model_name"],
        base_url: str = OLLAMA_CONFIG["base_url"],
        temperature: float = OLLAMA_CONFIG["temperature"],
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.base_url = base_url
        self.llm = self._initialize_model()
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        # Initialize chat history storage
        self.chat_histories = {}  # Document ID -> List of chat messages
        
    def _initialize_model(self) -> Ollama:
        return Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature
        )

    def _load_document(self, file_path: str, start_page: int = 0, end_page: int = -1) -> List[Any]:
        """Load and split document into pages."""
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        if end_page == -1:
            end_page = len(pages)
        
        return pages[start_page:end_page]

    def _generate_document_id(self, file_content: bytes) -> str:
        """Generate a unique ID for a document based on content hash"""
        import hashlib
        return hashlib.md5(file_content).hexdigest()
    
    def get_chat_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a specific document"""
        if not CHAT_HISTORY_ENABLED:
            return []
            
        return self.chat_histories.get(document_id, [])
        
    def add_to_chat_history(
        self, 
        document_id: str, 
        user_query: str, 
        system_response: str
    ) -> None:
        """Add a new entry to the chat history"""
        if not CHAT_HISTORY_ENABLED:
            return
            
        if document_id not in self.chat_histories:
            self.chat_histories[document_id] = []
            
        # Add new chat entry
        chat_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "user_query": user_query,
            "system_response": system_response
        }
        
        # Add to history
        self.chat_histories[document_id].append(chat_entry)
        
        # Limit history length
        if len(self.chat_histories[document_id]) > MAX_CHAT_HISTORY_ITEMS:
            self.chat_histories[document_id] = self.chat_histories[document_id][-MAX_CHAT_HISTORY_ITEMS:]
    
    def analyze_document(
        self,
        file_content: bytes,
        query_type: str = "summary",
        user_query: Optional[str] = None,
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, str]:
        # Generate document ID for chat history
        document_id = self._generate_document_id(file_content)
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            pages = self._load_document(temp_path, start_page, end_page)
            text_splitter = RecursiveCharacterTextSplitter()
            texts = text_splitter.split_documents(pages)
            
            # Combine all text content
            combined_text = "\n\n".join([doc.page_content for doc in texts])
            
            if query_type == "summary":
                summary_template = """Analyze and summarize the following text in Vietnamese. 
Focus on key points and main ideas.
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY. DO NOT USE ANY OTHER LANGUAGE.

Hãy phân tích và tóm tắt văn bản sau bằng tiếng Việt.
Tập trung vào các điểm chính và ý tưởng chính.
YÊU CẦU BẮT BUỘC: CHỈ TRẢ LỜI BẰNG TIẾNG VIỆT. KHÔNG DÙNG NGÔN NGỮ KHÁC.

Văn bản cần phân tích:
{text}

Yêu cầu:
1. Cung cấp bản tóm tắt toàn diện bằng tiếng Việt
2. Làm nổi bật các điểm chính và phát hiện quan trọng
3. Sử dụng ngôn ngữ rõ ràng và chuyên nghiệp
4. Cấu trúc bản tóm tắt với các điểm đánh dấu khi thích hợp
5. Bao gồm chi tiết quan trọng nhưng tránh thông tin không cần thiết

Tóm tắt (CHỈ TIẾNG VIỆT):"""
                
                summary_prompt = PromptTemplate(
                    input_variables=["text"],
                    template=summary_template
                )
                
                chain = LLMChain(llm=self.llm, prompt=summary_prompt)
                result = chain.run(text=combined_text)
                
                # Ensure response is in Vietnamese
                result = ensure_vietnamese_response(result)
                
                # Add to chat history
                if user_query:
                    self.add_to_chat_history(document_id, user_query, result)
                
                return {"result": result}
            
            elif query_type == "qa":
                if not user_query:
                    return {"result": "Vui lòng cung cấp câu hỏi cho chế độ Q&A"}
                
                # Create vector store for similarity search
                vectorstore = FAISS.from_documents(texts, self.embeddings)
                relevant_docs = vectorstore.similarity_search(user_query, k=3)
                
                relevant_text = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                qa_template = """Answer the following question in Vietnamese based on the provided context.
Provide a detailed and accurate response.
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY. DO NOT USE ANY OTHER LANGUAGE.

Hãy trả lời câu hỏi sau bằng tiếng Việt dựa trên ngữ cảnh được cung cấp.
Đưa ra câu trả lời chi tiết và chính xác.
YÊU CẦU BẮT BUỘC: CHỈ TRẢ LỜI BẰNG TIẾNG VIỆT. KHÔNG DÙNG NGÔN NGỮ KHÁC.

Ngữ cảnh:
{context}

Câu hỏi: {question}

Hướng dẫn:
1. Trả lời trực tiếp và toàn diện bằng tiếng Việt
2. Sử dụng bằng chứng từ ngữ cảnh
3. Cấu trúc câu trả lời rõ ràng
4. Nếu câu trả lời không có trong ngữ cảnh, hãy nói rõ
5. Sử dụng dấu đầu dòng cho nhiều điểm
6. Giữ ngôn ngữ chuyên nghiệp và rõ ràng

Câu trả lời (CHỈ TIẾNG VIỆT):"""
                
                qa_prompt = PromptTemplate(
                    input_variables=["context", "question"],
                    template=qa_template
                )
                
                chain = LLMChain(llm=self.llm, prompt=qa_prompt)
                result = chain.run(context=relevant_text, question=user_query)
                
                # Ensure response is in Vietnamese
                result = ensure_vietnamese_response(result)
                
                # Add to chat history
                self.add_to_chat_history(document_id, user_query, result)
                
                return {"result": result, "document_id": document_id}
            
            else:
                raise ValueError(f"Unknown query type: {query_type}")
                
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
        return {"result": "Analysis completed successfully"}

    def generate_quiz(
        self,
        file_content: bytes,
        num_questions: int = 5,
        difficulty: str = "medium",
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, Any]:
        """Generate quiz questions from a document."""
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            pages = self._load_document(temp_path, start_page, end_page)
            text_splitter = RecursiveCharacterTextSplitter()
            texts = text_splitter.split_documents(pages)
            
            # Combine all text content
            combined_text = "\n\n".join([doc.page_content for doc in texts])
            
            quiz_template = """Generate a quiz with exactly {num_questions} multiple-choice questions based on the following text.
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY. DO NOT USE ANY OTHER LANGUAGE. DO NOT USE ANY CHINESE CHARACTERS.

Hãy tạo một bài kiểm tra với đúng {num_questions} câu hỏi trắc nghiệm dựa trên văn bản sau đây.
Đối với mỗi câu hỏi, hãy cung cấp đúng 4 lựa chọn trắc nghiệm và chỉ ra câu trả lời đúng.
YÊU CẦU BẮT BUỘC: CHỈ SỬ DỤNG TIẾNG VIỆT, KHÔNG DÙNG CHỮ HÁN HOẶC NGÔN NGỮ KHÁC.

Văn bản:
{text}

Yêu cầu:
1. Tạo CHÍNH XÁC {num_questions} câu hỏi trắc nghiệm bằng tiếng Việt
2. Mỗi câu hỏi phải có 4 lựa chọn (A, B, C, D)
3. Chỉ rõ đáp án đúng cho mỗi câu hỏi
4. Độ khó: {difficulty} (dễ/trung bình/khó)
5. Tất cả nội dung phải bằng tiếng Việt
6. KHÔNG ĐƯỢC DÙNG CHỮ HÁN HOẶC BẤT KỲ NGÔN NGỮ NÀO KHÁC NGOÀI TIẾNG VIỆT

Định dạng chuẩn (phải tuân theo chính xác):
Câu 1: [Nội dung câu hỏi]
A. [Lựa chọn A]
B. [Lựa chọn B]
C. [Lựa chọn C]
D. [Lựa chọn D]
Đáp án đúng: [A/B/C/D]

Câu 2: [Nội dung câu hỏi]
A. [Lựa chọn A]
B. [Lựa chọn B]
C. [Lựa chọn C]
D. [Lựa chọn D]
Đáp án đúng: [A/B/C/D]

[Và cứ tiếp tục cho đến khi đủ {num_questions} câu hỏi]

QUAN TRỌNG: Phải đảm bảo tạo đúng {num_questions} câu hỏi, không thiếu không thừa.
BẮT BUỘC PHẢI TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT.
"""
        
            quiz_prompt = PromptTemplate(
                input_variables=["text", "num_questions", "difficulty"],
                template=quiz_template
            )
            
            # Adjust temperature based on the model's requirements
            self.llm.temperature = max(0.1, min(self.temperature, 0.7))  # Ensure temperature is in a good range
            
            # For longer outputs, we might need to make multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    chain = LLMChain(llm=self.llm, prompt=quiz_prompt)
                    result = chain.run(
                        text=combined_text[:15000],  # Limit context size to avoid token limits
                        num_questions=num_questions,
                        difficulty=difficulty
                    )
                    
                    # Verify we have the expected number of questions
                    question_count = result.count("Câu ")
                    if question_count < num_questions:
                        if attempt < max_attempts - 1:
                            continue  # Try again if we don't have enough questions
                        else:
                            # On final attempt, append a note about incomplete questions
                            result += f"\n\nChú ý: Chỉ có thể tạo được {question_count}/{num_questions} câu hỏi từ nội dung tài liệu."
                    
                    # Ensure response is in Vietnamese
                    result = ensure_vietnamese_response(result)
                    
                    # Sanitize the result before returning
                    sanitized_result = sanitize_quiz_content(result)
                    return {"result": sanitized_result}
                    
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e  # Re-raise on last attempt
                    # Otherwise try again
            
            # If all attempts failed but didn't raise an exception
            return {"result": "Không thể tạo bài kiểm tra. Vui lòng thử lại."}
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)