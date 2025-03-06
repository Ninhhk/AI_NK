import os
from typing import Optional, Union, Dict
from pathlib import Path
import tempfile

from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class DocumentAnalysisService:
    def __init__(
        self,
        model_name: str,
        ollama_base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.ollama_base_url = ollama_base_url
        self.llm = self._initialize_llm()
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
    def _initialize_llm(self) -> Ollama:
        return Ollama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.ollama_base_url,
        )

    def _load_document(self, file_path: Union[str, Path], start_page: int = 0, end_page: int = -1) -> list:
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        if end_page < 0:
            end_page = len(pages) + end_page + 1
        
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
MPORTANT: YOU MUST RESPOND IN VIETNAMESE LANGUAGE ONLY.
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