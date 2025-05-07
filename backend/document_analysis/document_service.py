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

    def analyze_multiple_documents(
        self,
        file_contents: List[bytes],
        filenames: List[str],
        query_type: str = "summary",
        user_query: Optional[str] = None,
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, Any]:
        """
        Analyze multiple documents and combine their results with proper references.
        
        Args:
            file_contents: List of document byte contents
            filenames: List of document filenames for reference
            query_type: Type of analysis to perform ('summary' or 'qa')
            user_query: User query for Q&A analysis
            start_page: First page to include
            end_page: Last page to include (-1 for all pages)
            
        Returns:
            Dictionary with analysis results
        """
        import hashlib
        import os
        import tempfile
        
        # Generate a combined document ID for chat history
        combined_hash = hashlib.md5(b"".join(file_contents)).hexdigest()
        
        # Process each document individually
        documents = []
        temp_paths = []
        
        try:
            # Step 1: Process each document to extract text and metadata
            for i, (content, filename) in enumerate(zip(file_contents, filenames)):
                # Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(content)
                    temp_path = temp_file.name
                    temp_paths.append(temp_path)
                
                try:
                    # Generate a hash ID for this specific document
                    doc_hash = hashlib.md5(content).hexdigest()[:10]
                    doc_id = f"doc_{i+1}_{doc_hash}"
                    
                    # Extract text content
                    pages = self._load_document(temp_path, start_page, end_page)
                    
                    if not pages:
                        documents.append({
                            "id": doc_id,
                            "filename": filename,
                            "status": "error",
                            "error": "No content could be extracted",
                            "content": ""
                        })
                        continue
                    
                    # Split into chunks for processing
                    text_splitter = RecursiveCharacterTextSplitter()
                    doc_chunks = text_splitter.split_documents(pages)
                    
                    # Add document metadata to each chunk
                    for chunk in doc_chunks:
                        chunk.metadata["doc_id"] = doc_id
                        chunk.metadata["doc_index"] = i+1
                        chunk.metadata["filename"] = filename
                    
                    # Combine all text content for this document
                    doc_text = "\n\n".join([chunk.page_content for chunk in doc_chunks])
                    
                    # Add to documents collection
                    documents.append({
                        "id": doc_id,
                        "filename": filename,
                        "status": "processed",
                        "chunks": doc_chunks,
                        "content": doc_text,
                        "page_count": len(pages)
                    })
                    
                except Exception as e:
                    documents.append({
                        "id": f"doc_{i+1}",
                        "filename": filename,
                        "status": "error",
                        "error": str(e),
                        "content": ""
                    })
            
            # Step 2: Process the query based on the documents
            if query_type == "summary":
                return self._generate_multi_document_summary(documents, combined_hash)
            elif query_type == "qa":
                if not user_query:
                    return {"result": "Vui lòng cung cấp câu hỏi cho chế độ Q&A"}
                return self._answer_question_from_documents(documents, user_query, combined_hash)
            else:
                raise ValueError(f"Unknown query type: {query_type}")
                
        finally:
            # Clean up temp files
            for temp_path in temp_paths:
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    def _generate_multi_document_summary(self, documents: List[Dict[str, Any]], combined_hash: str) -> Dict[str, Any]:
        """Generate summaries for multiple documents with proper citations."""
        # If no valid documents were processed
        valid_docs = [doc for doc in documents if doc["status"] == "processed"]
        if not valid_docs:
            return {"result": "Không thể trích xuất nội dung từ bất kỳ tài liệu nào."}
        
        if len(valid_docs) == 1:
            # If only one valid document, use regular summary
            doc = valid_docs[0]
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
            
            prompt = PromptTemplate(
                input_variables=["text"],
                template=summary_template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(text=doc["content"])
            result = ensure_vietnamese_response(result)
            
            return {"result": result, "document_id": combined_hash}
        
        # For multiple documents, create a combined summary with citations
        multi_doc_template = """Analyze and summarize multiple documents in Vietnamese.
Each document is provided with its own identifier for citation.
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY. DO NOT USE ANY OTHER LANGUAGE.

Hãy phân tích và tóm tắt nhiều tài liệu sau đây bằng tiếng Việt.
Mỗi tài liệu có mã định danh riêng để trích dẫn.
YÊU CẦU BẮT BUỘC: CHỈ TRẢ LỜI BẰNG TIẾNG VIỆT. KHÔNG DÙNG NGÔN NGỮ KHÁC.

Tài liệu:
{documents}

Yêu cầu:
1. Cung cấp bản tóm tắt tổng hợp bằng tiếng Việt
2. Làm nổi bật điểm chung và khác biệt giữa các tài liệu
3. Trích dẫn rõ ràng khi đề cập đến thông tin cụ thể (sử dụng mã định danh tài liệu)
4. Tạo phần tóm tắt riêng cho mỗi tài liệu
5. Kết luận bằng đánh giá tổng hợp các tài liệu

Tóm tắt (CHỈ TIẾNG VIỆT):"""
        
        # Format the document information for the prompt
        document_texts = []
        for doc in valid_docs:
            file_info = f"[{doc['id']}] {doc['filename']}"
            # Take first 1000 characters of each document to avoid token limits
            doc_preview = doc["content"][:1000] + "..." if len(doc["content"]) > 1000 else doc["content"]
            document_texts.append(f"{file_info}\n\n{doc_preview}\n\n---")
        
        formatted_docs = "\n\n".join(document_texts)
        
        prompt = PromptTemplate(
            input_variables=["documents"],
            template=multi_doc_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(documents=formatted_docs)
        result = ensure_vietnamese_response(result)
        
        return {
            "result": result, 
            "document_id": combined_hash,
            "document_count": len(valid_docs),
            "documents": [{"id": doc["id"], "filename": doc["filename"]} for doc in valid_docs]
        }
    
    def _answer_question_from_documents(self, documents: List[Dict[str, Any]], user_query: str, combined_hash: str) -> Dict[str, Any]:
        """Answer a question based on multiple documents with proper citations."""
        # If no valid documents were processed
        valid_docs = [doc for doc in documents if doc["status"] == "processed"]
        if not valid_docs:
            return {"result": "Không thể trích xuất nội dung từ bất kỳ tài liệu nào."}
        
        # Create vector store from all document chunks
        all_chunks = []
        for doc in valid_docs:
            all_chunks.extend(doc["chunks"])
        
        # If we have a single document, use regular QA with vectorstore
        if len(valid_docs) == 1:
            vectorstore = FAISS.from_documents(all_chunks, self.embeddings)
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
            
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=qa_template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(context=relevant_text, question=user_query)
            result = ensure_vietnamese_response(result)
            
            # Add to chat history
            self.add_to_chat_history(combined_hash, user_query, result)
            
            return {"result": result, "document_id": combined_hash}
        
        # For multiple documents, use retrieval with citations
        vectorstore = FAISS.from_documents(all_chunks, self.embeddings)
        relevant_docs = vectorstore.similarity_search(user_query, k=5)
        
        # Group relevant chunks by document for citation
        cited_chunks = []
        for chunk in relevant_docs:
            doc_id = chunk.metadata.get("doc_id", "unknown")
            filename = chunk.metadata.get("filename", "unknown")
            cited_chunks.append(f"[{doc_id}] {filename}:\n{chunk.page_content}\n---")
        
        relevant_text = "\n\n".join(cited_chunks)
        
        multi_doc_qa_template = """Answer the question in Vietnamese based on these document excerpts with citations.
IMPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY. DO NOT USE ANY OTHER LANGUAGE.

Hãy trả lời câu hỏi sau bằng tiếng Việt dựa trên các đoạn trích từ nhiều tài liệu.
YÊU CẦU BẮT BUỘC: CHỈ TRẢ LỜI BẰNG TIẾNG VIỆT. KHÔNG DÙNG NGÔN NGỮ KHÁC.

Các đoạn trích từ tài liệu:
{context}

Câu hỏi: {question}

Hướng dẫn:
1. Trả lời bằng tiếng Việt và LUÔN trích dẫn nguồn cụ thể (sử dụng mã định danh trong ngoặc vuông)
2. Với mỗi thông tin quan trọng, hãy đính kèm mã định danh nguồn trong ngoặc vuông, ví dụ: [doc_1_abc123]
3. So sánh thông tin từ các tài liệu khác nhau nếu có
4. Chỉ rõ khi các tài liệu có thông tin mâu thuẫn
5. Nếu không tìm thấy câu trả lời trong ngữ cảnh, hãy nêu rõ
6. Đảm bảo câu trả lời cụ thể và thông tin chính xác
7. Sử dụng trích dẫn theo định dạng: [mã_tài_liệu]
8. BẮT BUỘC SỬ DỤNG TRÍCH DẪN cho mọi phần thông tin cụ thể, không bỏ qua bất kỳ trích dẫn nào

Câu trả lời (CHỈ TIẾNG VIỆT VÀ BẮT BUỘC CÓ TRÍCH DẪN):"""
        
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=multi_doc_qa_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(context=relevant_text, question=user_query)
        result = ensure_vietnamese_response(result)
        
        # Add to chat history
        self.add_to_chat_history(combined_hash, user_query, result)
        
        return {
            "result": result, 
            "document_id": combined_hash,
            "document_count": len(valid_docs),
            "documents": [{"id": doc["id"], "filename": doc["filename"]} for doc in valid_docs]
        }