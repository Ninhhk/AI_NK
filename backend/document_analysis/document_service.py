import os
from typing import Optional, Union, Dict, List, Any
from pathlib import Path
import tempfile
import re
import unicodedata

from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from .config import OLLAMA_CONFIG

def is_chinese(char: str) -> bool:
    """Check if a character is Chinese."""
    try:
        return 'CJK' in unicodedata.name(char)
    except ValueError:
        return False

def contains_chinese(text: str) -> bool:
    """Check if text contains any Chinese characters."""
    return any(is_chinese(char) for char in text)

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

    def analyze_document(
        self,
        file_content: bytes,
        query_type: str = "summary",
        user_query: Optional[str] = None,
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, str]:
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
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY.

Hãy phân tích và tóm tắt văn bản sau bằng tiếng Việt.
Tập trung vào các điểm chính và ý tưởng chính.

Văn bản cần phân tích:
{text}

Yêu cầu:
1. Cung cấp bản tóm tắt toàn diện
2. Làm nổi bật các điểm chính và phát hiện quan trọng
3. Sử dụng ngôn ngữ rõ ràng và chuyên nghiệp
4. Cấu trúc bản tóm tắt với các điểm đánh dấu khi thích hợp
5. Bao gồm chi tiết quan trọng nhưng tránh thông tin không cần thiết

Tóm tắt:"""
                
                summary_prompt = PromptTemplate(
                    input_variables=["text"],
                    template=summary_template
                )
                
                chain = LLMChain(llm=self.llm, prompt=summary_prompt)
                result = chain.run(text=combined_text)
                return {"result": result}
            
            elif query_type == "qa":
                if not user_query:
                    return {"result": "Please provide a question for QA mode"}
                
                # Create vector store for similarity search
                vectorstore = FAISS.from_documents(texts, self.embeddings)
                relevant_docs = vectorstore.similarity_search(user_query, k=3)
                
                relevant_text = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                qa_template = """Answer the following question in Vietnamese based on the provided context.
Provide a detailed and accurate response.
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY.
Context:
{context}

Question: {question}

Guidelines:
1. Answer directly and comprehensively
2. Use evidence from the context
3. Structure the answer clearly
4. If the answer isn't in the context, say so
5. Use bullet points for multiple points
6. Keep the language professional and clear

Answer:"""
                
                qa_prompt = PromptTemplate(
                    input_variables=["context", "question"],
                    template=qa_template
                )
                
                chain = LLMChain(llm=self.llm, prompt=qa_prompt)
                result = chain.run(context=relevant_text, question=user_query)
                return {"result": result}
            
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
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY. DO NOT USE ANY CHINESE CHARACTERS.

Hãy tạo một bài kiểm tra với đúng {num_questions} câu hỏi trắc nghiệm dựa trên văn bản sau đây.
Đối với mỗi câu hỏi, hãy cung cấp đúng 4 lựa chọn trắc nghiệm và chỉ ra câu trả lời đúng.
QUAN TRỌNG: CHỈ SỬ DỤNG TIẾNG VIỆT, KHÔNG DÙNG CHỮ HÁN.

Văn bản:
{text}

Yêu cầu:
1. Tạo CHÍNH XÁC {num_questions} câu hỏi trắc nghiệm
2. Mỗi câu hỏi phải có 4 lựa chọn (A, B, C, D)
3. Chỉ rõ đáp án đúng cho mỗi câu hỏi
4. Độ khó: {difficulty} (dễ/trung bình/khó)
5. Tất cả nội dung phải bằng tiếng Việt
6. KHÔNG ĐƯỢC DÙNG CHỮ HÁN

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