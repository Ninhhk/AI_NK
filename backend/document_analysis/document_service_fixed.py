import os
import logging
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
    """For debugging: Always return True to bypass Vietnamese language check."""
    return True

def ensure_vietnamese_response(response: str) -> str:
    """For debugging: Bypass Vietnamese language enforcement and return input as-is."""
    return response

def sanitize_text(text: str) -> str:
    """Remove Chinese characters and clean up text."""
    cleaned = ''.join(char for char in text if not is_chinese(char))
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\n+', '\n', cleaned)
    return cleaned.strip()

def sanitize_quiz_content(content: str) -> str:
    """Sanitize quiz content and ensure proper formatting."""
    lines = content.split('\n')
    sanitized_lines = []
    
    for line in lines:
        if not line.strip():
            sanitized_lines.append('')
            continue
            
        cleaned_line = ''.join(char for char in line if not is_chinese(char))
        cleaned_line = cleaned_line.strip()
        
        if not cleaned_line:
            continue
            
        if re.match(r'^Question\s+\d+', cleaned_line):
            sanitized_lines.extend(['', cleaned_line])
        elif re.match(r'^[A-D]\.', cleaned_line):
            sanitized_lines.append(cleaned_line)
        elif 'Correct answer:' in cleaned_line:
            sanitized_lines.extend([cleaned_line, ''])
        else:
            sanitized_lines.append(cleaned_line)
    
    result = '\n'.join(sanitized_lines)
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
        self.chat_histories = {}
        
    def _initialize_model(self) -> Ollama:
        return Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature
        )
    
    def set_model(self, model_name: str) -> None:
        """Change the model used for generation."""
        if model_name != self.model_name:
            self.model_name = model_name
            self.llm = self._initialize_model()
            logging.getLogger(__name__).info(f"Changed model to {model_name}")
    
    def get_current_model(self) -> str:
        """Get the current model name."""
        return self.model_name

    def _load_document(self, file_path: str, start_page: int = 0, end_page: int = -1) -> List[Any]:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        if end_page == -1:
            end_page = len(pages)
        
        return pages[start_page:end_page]

    def _generate_document_id(self, file_content: bytes) -> str:
        import hashlib
        return hashlib.md5(file_content).hexdigest()
    
    def get_chat_history(self, document_id: str) -> List[Dict[str, Any]]:
        if not CHAT_HISTORY_ENABLED:
            return []
            
        return self.chat_histories.get(document_id, [])
        
    def add_to_chat_history(
        self, 
        document_id: str, 
        user_query: str, 
        system_response: str
    ) -> None:
        if not CHAT_HISTORY_ENABLED:
            return
            
        if document_id not in self.chat_histories:
            self.chat_histories[document_id] = []
            
        chat_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "user_query": user_query,
            "system_response": system_response
        }
        
        self.chat_histories[document_id].append(chat_entry)
        
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
        document_id = self._generate_document_id(file_content)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            pages = self._load_document(temp_path, start_page, end_page)
            text_splitter = RecursiveCharacterTextSplitter()
            texts = text_splitter.split_documents(pages)
            
            combined_text = "\n\n".join([doc.page_content for doc in texts])
            
            if query_type == "summary":
                summary_template = """Analyze and summarize the following text. 
Focus on key points and main ideas.

Text to analyze:
{text}

Requirements:
1. Provide a comprehensive summary
2. Highlight key points and important findings
3. Use clear and professional language
4. Structure the summary with bullet points when appropriate
5. Include important details but avoid unnecessary information

Summary:"""
                
                summary_prompt = PromptTemplate(
                    input_variables=["text"],
                    template=summary_template
                )
                
                chain = LLMChain(llm=self.llm, prompt=summary_prompt)
                result = chain.invoke({"text": combined_text})["text"]
                
                if user_query:
                    self.add_to_chat_history(document_id, user_query, result)
                
                return {"result": result}
            
            elif query_type == "qa":
                if not user_query:
                    return {"result": "Please provide a question for Q&A mode."}
                
                vectorstore = FAISS.from_documents(texts, self.embeddings)
                relevant_docs = vectorstore.similarity_search(user_query, k=3)
                
                relevant_text = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                qa_template = """Answer the following question based on the provided context.
Provide a detailed and accurate response.

Context:
{context}

Question: {question}

Guidelines:
1. Answer directly and comprehensively
2. Use evidence from the context
3. Structure your answer clearly
4. If the answer is not in the context, say so clearly
5. Use bullet points for multiple items
6. Keep language professional and clear

Answer:"""
                
                qa_prompt = PromptTemplate(
                    input_variables=["context", "question"],
                    template=qa_template
                )
                
                chain = LLMChain(llm=self.llm, prompt=qa_prompt)
                result = chain.invoke({"context": relevant_text, "question": user_query})["text"]
                
                self.add_to_chat_history(document_id, user_query, result)
                
                return {"result": result, "document_id": document_id}
            
            else:
                raise ValueError(f"Unknown query type: {query_type}")
                
        finally:
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
        """Generate quiz questions from a single document."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            pages = self._load_document(temp_path, start_page, end_page)
            text_splitter = RecursiveCharacterTextSplitter()
            texts = text_splitter.split_documents(pages)
            
            combined_text = "\n\n".join([doc.page_content for doc in texts])
            
            quiz_template = """Generate exactly {num_questions} multiple-choice questions based on the following text.

Text:
{text}

Requirements:
1. Create exactly {num_questions} questions.
2. Each question must have 4 options (A, B, C, D).
3. Indicate the correct answer for each question.
4. Difficulty: {difficulty}

Format strictly:
Question 1: [question text]
A. [option A]
B. [option B]
C. [option C]
D. [option D]
Correct answer: [A/B/C/D]

Continue in this format until Question {num_questions}."""
        
            quiz_prompt = PromptTemplate(
                input_variables=["text", "num_questions", "difficulty"],
                template=quiz_template
            )
            
            self.llm.temperature = max(0.1, min(self.temperature, 0.7))
            
            chain = LLMChain(llm=self.llm, prompt=quiz_prompt)
            result = chain.invoke({
                "text": combined_text[:15000],
                "num_questions": num_questions,
                "difficulty": difficulty
            })["text"]
            
            sanitized_result = sanitize_quiz_content(result)
            return {"result": sanitized_result}
        
        finally:
            os.unlink(temp_path)

    def generate_quiz_multiple(
        self,
        file_contents: List[bytes],
        filenames: List[str],
        num_questions: int = 5,
        difficulty: str = "medium",
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, Any]:
        """Generate a quiz from multiple documents."""
        import tempfile, os
        docs_text = []
        for content, filename in zip(file_contents, filenames):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
                tf.write(content)
                temp_path = tf.name
            try:
                pages = self._load_document(temp_path, start_page, end_page)
                splitter = RecursiveCharacterTextSplitter()
                chunks = splitter.split_documents(pages)
                combined = "\n\n".join([doc.page_content for doc in chunks])
                docs_text.append(f"### Document: {filename}\n{combined}")
            finally:
                os.unlink(temp_path)
        all_text = "\n\n---\n\n".join(docs_text)
        
        quiz_template = """Generate exactly {num_questions} multiple-choice questions based on the following documents and their content.

{all_text}

Requirements:
1. Create exactly {num_questions} questions.
2. Each question must have 4 options (A, B, C, D).
3. Indicate the correct answer for each question.
4. Difficulty: {difficulty}

Format strictly:
Question 1: [question text]
A. [option A]
B. [option B]
C. [option C]
D. [option D]
Correct answer: [A/B/C/D]

Continue in this format until Question {num_questions}."""
        
        quiz_prompt = PromptTemplate(
            input_variables=["all_text", "num_questions", "difficulty"],
            template=quiz_template
        )
        
        self.llm.temperature = max(0.1, min(self.temperature, 0.7))
        chain = LLMChain(llm=self.llm, prompt=quiz_prompt)
        result = chain.invoke({"all_text": all_text, "num_questions": num_questions, "difficulty": difficulty})["text"]
        sanitized = sanitize_quiz_content(result)
        return {"result": sanitized}

    def analyze_multiple_documents(
        self,
        file_contents: List[bytes],
        filenames: List[str],
        query_type: str = "summary",
        user_query: Optional[str] = None,
        start_page: int = 0,
        end_page: int = -1,
    ) -> Dict[str, Any]:
        import hashlib
        import os
        import tempfile
        
        combined_hash = hashlib.md5(b"".join(file_contents)).hexdigest()
        
        documents = []
        temp_paths = []
        
        try:
            for i, (content, filename) in enumerate(zip(file_contents, filenames)):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(content)
                    temp_path = temp_file.name
                    temp_paths.append(temp_path)
                
                try:
                    doc_hash = hashlib.md5(content).hexdigest()[:10]
                    doc_id = f"doc_{i+1}_{doc_hash}"
                    
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
                    
                    text_splitter = RecursiveCharacterTextSplitter()
                    doc_chunks = text_splitter.split_documents(pages)
                    
                    for chunk in doc_chunks:
                        chunk.metadata["doc_id"] = doc_id
                        chunk.metadata["doc_index"] = i+1
                        chunk.metadata["filename"] = filename
                    
                    doc_text = "\n\n".join([chunk.page_content for chunk in doc_chunks])
                    
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
            
            if query_type == "summary":
                return self._generate_multi_document_summary(documents, combined_hash)
            elif query_type == "qa":
                if not user_query:
                    return {"result": "Please provide a question for Q&A mode."}
                return self._answer_question_from_documents(documents, user_query, combined_hash)
            else:
                raise ValueError(f"Unknown query type: {query_type}")
                
        finally:
            for temp_path in temp_paths:
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    def _generate_multi_document_summary(self, documents: List[Dict[str, Any]], combined_hash: str) -> Dict[str, Any]:
        valid_docs = [doc for doc in documents if doc["status"] == "processed"]
        if not valid_docs:
            return {"result": "No content could be extracted from any document."}
        
        if len(valid_docs) == 1:
            doc = valid_docs[0]
            summary_template = """Analyze and summarize the following text. 
Focus on key points and main ideas.

Text to analyze:
{text}

Requirements:
1. Provide a comprehensive summary
2. Highlight key points and important findings
3. Use clear and professional language
4. Structure the summary with bullet points when appropriate
5. Include important details but avoid unnecessary information

Summary:"""
            
            prompt = PromptTemplate(
                input_variables=["text"],
                template=summary_template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke({"text": doc["content"]})["text"]
            
            return {"result": result, "document_id": combined_hash}
        
        multi_doc_template = """Analyze and summarize multiple documents.
Each document is provided with its own identifier for citation.

Documents:
{documents}

Requirements:
1. Provide a combined summary
2. Highlight commonalities and differences between the documents
3. Clearly cite specific information (use document identifiers)
4. Create individual summaries for each document
5. Conclude with an overall evaluation of the documents

Summary:"""
        
        document_texts = []
        for doc in valid_docs:
            file_info = f"[{doc['id']}] {doc['filename']}"
            doc_preview = doc["content"][:1000] + "..." if len(doc["content"]) > 1000 else doc["content"]
            document_texts.append(f"{file_info}\n\n{doc_preview}\n\n---")
        
        formatted_docs = "\n\n".join(document_texts)
        
        prompt = PromptTemplate(
            input_variables=["documents"],
            template=multi_doc_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({"documents": formatted_docs})["text"]
        
        return {
            "result": result, 
            "document_id": combined_hash,
            "document_count": len(valid_docs),
            "documents": [{"id": doc["id"], "filename": doc["filename"]} for doc in valid_docs]
        }
    
    def _answer_question_from_documents(self, documents: List[Dict[str, Any]], user_query: str, combined_hash: str) -> Dict[str, Any]:
        valid_docs = [doc for doc in documents if doc["status"] == "processed"]
        if not valid_docs:
            return {"result": "No content could be extracted from any document."}
        
        all_chunks = []
        for doc in valid_docs:
            all_chunks.extend(doc["chunks"])
        
        if len(valid_docs) == 1:
            vectorstore = FAISS.from_documents(all_chunks, self.embeddings)
            relevant_docs = vectorstore.similarity_search(user_query, k=3)
            relevant_text = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            qa_template = """Answer the following question based on the provided context.
Provide a detailed and accurate response.

Context:
{context}

Question: {question}

Guidelines:
1. Answer directly and comprehensively
2. Use evidence from the context
3. Structure your answer clearly
4. If the answer is not in the context, say so clearly
5. Use bullet points for multiple items
6. Keep language professional and clear

Answer:"""
            
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=qa_template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke({"context": relevant_text, "question": user_query})["text"]
            
            self.add_to_chat_history(combined_hash, user_query, result)
            
            return {"result": result, "document_id": combined_hash}
        
        vectorstore = FAISS.from_documents(all_chunks, self.embeddings)
        relevant_docs = vectorstore.similarity_search(user_query, k=5)
        
        cited_chunks = []
        for chunk in relevant_docs:
            doc_id = chunk.metadata.get("doc_id", "unknown")
            filename = chunk.metadata.get("filename", "unknown")
            cited_chunks.append(f"[{doc_id}] {filename}:\n{chunk.page_content}\n---")
        
        relevant_text = "\n\n".join(cited_chunks)
        
        multi_doc_qa_template = """Answer the question based on these document excerpts with citations.

Document excerpts:
{context}

Question: {question}

Guidelines:
1. Answer and ALWAYS cite specific sources (use identifiers in square brackets)
2. For each important information, attach the source identifier in square brackets, e.g., [doc_1_abc123]
3. Structure the answer clearly
4. If the answer is not found in the documents, state so clearly
5. Ensure comprehensive answers, combining information from all relevant sources

Answer:"""
        
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=multi_doc_qa_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({"context": relevant_text, "question": user_query})["text"]
        
        self.add_to_chat_history(combined_hash, user_query, result)
        
        document_references = "\n".join([f"[{doc['id']}]: {doc['filename']}" for doc in valid_docs])
        
        return {
            "result": result,
            "document_id": combined_hash,
            "document_count": len(valid_docs),
            "documents": [{"id": doc["id"], "filename": doc["filename"]} for doc in valid_docs]
        }
