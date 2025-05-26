# Retrieval Augmented Generation (RAG) for Quiz Creation

## Overview
This document explains the implementation of Retrieval Augmented Generation (RAG) in our document analysis and quiz generation system. RAG combines information retrieval with generative AI to create more contextually aware and relevant outputs.

## Implementation
Our system implements RAG in multiple components:

### 1. Document Processing
- Documents are split into chunks using `RecursiveCharacterTextSplitter` with optimized chunk sizes (1000) and overlaps (200)
- Each chunk maintains metadata about its source document, including filename and document ID

### 2. Vector Storage
- Document chunks are embedded using `HuggingFaceEmbeddings` with the "sentence-transformers/all-MiniLM-L6-v2" model
- Embeddings are stored in a FAISS vector store for efficient similarity search

### 3. Retrieval Strategy
Both single and multi-document quiz generation implement:
- Topic-based retrieval using key prompts like:
  - "What are the main topics covered in this document?"
  - "What are the key concepts in this document?"
  - "What are the most important facts in this document?"
- Relevance-based chunk selection with configurable k parameters
- Source tracking in multi-document contexts

### 4. Generation with Context
- Two-part context provision to the LLM:
  - Document overview (truncated to prevent token overflow)
  - Specific relevant chunks retrieved for topic understanding
- Dynamic prompt templates that include both contexts
- Source references in multi-document contexts

## Key Components

### Single Document Quiz Generation
```python
# Create vector store for better retrieval
vectorstore = FAISS.from_documents(texts, self.embeddings)

# Retrieve relevant chunks for quiz generation using key topic prompts
topic_prompts = [
    "What are the main topics covered in this document?",
    "What are the key concepts in this document?"
    # ...additional prompts
]

relevant_chunks = []
for prompt in topic_prompts:
    results = vectorstore.similarity_search(prompt, k=2)
    relevant_chunks.extend([doc.page_content for doc in results])
```

### Multi-Document Quiz Generation
```python
# Create a vector store from all document chunks with source tracking
vectorstore = FAISS.from_documents(all_chunks, self.embeddings)

# Retrieve relevant chunks across documents
topic_prompts = [
    "What are the main topics covered in these documents?",
    "What are the similarities and differences between these documents?"
    # ...additional prompts
]

relevant_chunks = []
for prompt in topic_prompts:
    results = vectorstore.similarity_search(prompt, k=3)
    for doc in results:
        source = doc.metadata.get("source", "unknown")
        relevant_chunks.append(f"From {source}:\n{doc.page_content}")
```

## Benefits
- **Improved Relevance**: Questions focus on the most important content
- **Better Context Understanding**: The system can identify key concepts across the document(s)
- **Cross-Document Connections**: In multi-document mode, the system can generate questions that span document relationships
- **Source Tracking**: Questions can be traced back to their source documents

## Technical Considerations
- Context length limitations are handled through truncation (5000 chars for overview, 10000 for relevant chunks)
- Temperature is adjusted to a reasonable range (max 0.7) to ensure coherent outputs
- Vietnamese language requirements are enforced through system prompts
