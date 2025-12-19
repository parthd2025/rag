# API Endpoints & Request/Response Flow

## API Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   RAG CHATBOT API                           │
│                   (FastAPI Backend)                         │
│                   Port: 8001                                │
└─────────────────────────────────────────────────────────────┘

Base URL: http://localhost:8001
```

---

## 1. Health Check Endpoint

### Endpoint: `GET /health`

**Purpose**: Monitor system status and component readiness

**Request**:
```
GET /health
```

**Response (200 OK)**:
```json
{
  "status": "ok",
  "llm_ready": true,
  "chunks": 42,
  "vector_store_initialized": true,
  "rag_engine_initialized": true
}
```

**Error Response (500)**:
```json
{
  "detail": "Health check failed"
}
```

**Flow**:
```
REQUEST → Check Vector Store → Check LLM → Check RAG Engine → RESPONSE
```

---

## 2. Configuration Endpoint

### Endpoint: `GET /config`

**Purpose**: Retrieve current system configuration

**Request**:
```
GET /config
```

**Response (200 OK)**:
```json
{
  "llm_model": "llama-3.3-70b-versatile",
  "llm_provider": "groq",
  "embedding_model": "all-MiniLM-L6-v2",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "temperature": 0.7,
  "max_tokens": 512,
  "top_k": 8
}
```

**Error Response (500)**:
```json
{
  "detail": "Failed to retrieve configuration"
}
```

---

## 3. Document Upload Endpoint

### Endpoint: `POST /upload`

**Purpose**: Upload and ingest documents into the vector store

**Request**:
```
POST /upload
Content-Type: multipart/form-data

{
  "file": <binary_file_data>
}
```

**Supported File Types**:
- `.pdf` - PDF documents
- `.docx` - Word documents
- `.txt` - Text files
- `.md` - Markdown files
- `.csv` - CSV data files
- `.xlsx`, `.xls` - Excel spreadsheets
- `.pptx` - PowerPoint presentations
- `.html`, `.htm` - HTML files
- `.xml` - XML documents

**Response (200 OK)**:
```json
{
  "filename": "document.pdf",
  "chunks_created": 15,
  "status": "success",
  "message": "Document processed and indexed successfully"
}
```

**Error Responses**:

File too large (413):
```json
{
  "detail": "File size exceeds maximum allowed size (10MB)"
}
```

Unsupported file type (400):
```json
{
  "detail": "File type not supported"
}
```

Processing error (500):
```json
{
  "detail": "Error processing document"
}
```

**Upload Flow**:
```
FILE RECEIVED
    │
    ├─→ Validate file size
    ├─→ Validate file type
    ├─→ Extract content
    ├─→ Create chunks
    ├─→ Generate embeddings
    ├─→ Store in FAISS
    │
    ▼
RESPONSE: Chunks created N
```

---

## 4. Chat Query Endpoint

### Endpoint: `POST /chat`

**Purpose**: Ask questions about uploaded documents using RAG

**Request**:
```
POST /chat
Content-Type: application/json

{
  "question": "What is the main topic of the document?",
  "top_k": 5
}
```

**Request Model**:
```python
class QueryRequest(BaseModel):
    question: str          # Min 1, Max 1000 chars
    top_k: Optional[int]  # Default 5, Range 1-20
```

**Response (200 OK)**:
```json
{
  "answer": "The main topic is Retrieval-Augmented Generation for question answering...",
  "sources": [
    {
      "chunk_id": 0,
      "document": "manual.pdf",
      "content": "RAG is a technique that combines...",
      "relevance_score": 0.95
    },
    {
      "chunk_id": 3,
      "document": "manual.pdf",
      "content": "Vector embeddings enable semantic search...",
      "relevance_score": 0.87
    }
  ]
}
```

**Error Responses**:

Empty question (422):
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "Question cannot be empty",
      "type": "value_error"
    }
  ]
}
```

No documents (404):
```json
{
  "detail": "No documents uploaded. Please upload documents first."
}
```

LLM unavailable (503):
```json
{
  "detail": "LLM service unavailable"
}
```

**Query Flow**:
```
QUESTION RECEIVED
    │
    ├─→ Validate question
    ├─→ Generate question embedding
    ├─→ Search vector store
    ├─→ Retrieve top_k chunks
    ├─→ Assemble context
    ├─→ Call LLM with context
    ├─→ Generate answer
    ├─→ Format response with sources
    │
    ▼
RESPONSE: Answer + Sources
```

---

## 5. Quiz Generation Endpoint

### Endpoint: `POST /quiz`

**Purpose**: Generate multiple-choice quiz from documents

**Request**:
```
POST /quiz
Content-Type: application/json

{
  "num_questions": 5
}
```

**Request Model**:
```python
class QuizRequest(BaseModel):
    num_questions: Optional[int]  # Default 5, Range 1-20
```

**Response (200 OK)**:
```json
{
  "questions": [
    {
      "question": "What is the primary purpose of vector embeddings?",
      "options": [
        "A: To compress file sizes",
        "B: To represent text as numerical vectors for semantic search",
        "C: To replace database indexes",
        "D: To encrypt document content"
      ],
      "correct_answer": "B",
      "source": "Getting Started Guide - Section 2"
    },
    {
      "question": "Which embedding model is used by default?",
      "options": [
        "A: BERT",
        "B: all-MiniLM-L6-v2",
        "C: RoBERTa",
        "D: GPT"
      ],
      "correct_answer": "B",
      "source": "Configuration Documentation"
    }
  ]
}
```

**Error Responses**:

No documents (404):
```json
{
  "detail": "No documents available for quiz generation"
}
```

Invalid question count (422):
```json
{
  "detail": [
    {
      "loc": ["body", "num_questions"],
      "msg": "Number of questions must be between 1 and 20",
      "type": "value_error"
    }
  ]
}
```

**Quiz Flow**:
```
REQUEST QUIZ
    │
    ├─→ Validate num_questions
    ├─→ Select random chunks
    ├─→ For each chunk:
    │   ├─→ Generate question
    │   ├─→ Create options (A-D)
    │   └─→ Mark correct answer
    ├─→ Format quiz response
    │
    ▼
RESPONSE: N Questions ready
```

---

## 6. Get Documents Endpoint

### Endpoint: `GET /documents`

**Purpose**: Retrieve statistics about uploaded documents

**Request**:
```
GET /documents
```

**Response (200 OK)**:
```json
{
  "total_chunks": 42,
  "documents": [
    {
      "name": "manual.pdf",
      "chunks": 15,
      "upload_date": "2025-12-19T10:30:00Z"
    },
    {
      "name": "guide.md",
      "chunks": 27,
      "upload_date": "2025-12-19T11:45:00Z"
    }
  ],
  "storage_info": {
    "vector_store_size": "2.3 MB",
    "embedding_dimension": 384,
    "index_type": "FAISS"
  }
}
```

**Error Response (500)**:
```json
{
  "detail": "Failed to retrieve document information"
}
```

---

## 7. Clear Data Endpoint

### Endpoint: `DELETE /clear`

**Purpose**: Clear all documents and reset the system

**Request**:
```
DELETE /clear
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "All data cleared successfully",
  "chunks_deleted": 42,
  "reset_at": "2025-12-19T12:00:00Z"
}
```

**Error Response (500)**:
```json
{
  "detail": "Failed to clear data"
}
```

**Clear Flow**:
```
CLEAR REQUEST
    │
    ├─→ Clear FAISS index
    ├─→ Remove all vectors
    ├─→ Clear chunk storage
    ├─→ Reset metadata
    ├─→ Flush database
    │
    ▼
RESPONSE: System cleared & reset
```

---

## 8. Root Endpoint

### Endpoint: `GET /`

**Purpose**: API information and welcome message

**Request**:
```
GET /
```

**Response (200 OK)**:
```json
{
  "title": "RAG Chatbot API",
  "version": "1.0.0",
  "description": "Retrieval-Augmented Generation API for document Q&A",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## Request/Response Pattern

### General Pattern

```
REQUEST
  │
  ├─→ Receive & Parse
  │
  ├─→ Validate Input
  │   └─→ [INVALID] → HTTP 400/422 Error Response
  │
  ├─→ Authorize (CORS)
  │   └─→ [DENIED] → HTTP 403 Forbidden
  │
  ├─→ Process
  │   └─→ [ERROR] → HTTP 500 Internal Server Error
  │
  ├─→ Format Response
  │
  ▼
RESPONSE (HTTP 200, 400, 403, 404, 500, 503, etc.)
```

---

## HTTP Status Codes

| Code | Meaning | Scenario |
|------|---------|----------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource not found (no documents) |
| 413 | Payload Too Large | File exceeds size limit |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error during processing |
| 503 | Service Unavailable | External service (LLM) unavailable |

---

## Error Response Format

```json
{
  "detail": "Human-readable error message",
  "error_code": "OPTIONAL_ERROR_CODE",
  "timestamp": "2025-12-19T12:00:00Z"
}
```

---

## CORS Configuration

Allowed Origins:
- `http://localhost:8501` (Streamlit Frontend)
- `http://127.0.0.1:8501`

Allowed Methods:
- `GET`
- `POST`
- `DELETE`

Allowed Headers:
- All headers (`*`)

---

## Rate Limiting & Constraints

| Parameter | Limit | Default |
|-----------|-------|---------|
| Max File Size | 10 MB | - |
| Question Length | 1-1000 chars | - |
| Top-K Results | 1-20 | 5 |
| Quiz Questions | 1-20 | 5 |
| Chunk Size | Configurable | 1000 |
| Request Timeout | 180 seconds | - |

---

## API Documentation URLs

- **Interactive Docs (Swagger UI)**: http://localhost:8001/docs
- **ReDoc (Alternative UI)**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

---

## Common Workflows

### Workflow 1: Upload and Query

```
1. POST /upload → Upload document.pdf
   Response: 15 chunks created

2. GET /health → Verify system ready
   Response: All components OK

3. POST /chat → Ask "What is...?"
   Response: Answer with sources
```

### Workflow 2: Generate Quiz

```
1. GET /documents → Check available docs
   Response: 42 chunks available

2. POST /quiz → Request 5 questions
   Response: 5 MCQ questions

3. User answers and self-evaluates
```

### Workflow 3: System Maintenance

```
1. GET /health → Check status
2. GET /config → View configuration
3. DELETE /clear → Reset system
4. POST /upload → Start fresh
```
