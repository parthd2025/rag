# Backend API Documentation

## Overview

FastAPI-based REST API for the RAG chatbot system. Provides document management and question-answering capabilities.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API server and LLM engine are ready.

**Response:**
```json
{
  "status": "ok",
  "vector_store_ready": true,
  "llm_ready": true,
  "total_chunks": 1250
}
```

**Status Codes:**
- `200`: Server is healthy
- `500`: Components not initialized

---

### 2. Upload Documents

**POST** `/upload`

Upload and process documents. Extracts text, creates embeddings, and stores in vector database.

**Parameters:**
- `files` (multipart form-data, required): List of document files
  - Supported formats: PDF, DOCX, TXT, MD
  - Max per file: 100MB (default)

**Example:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "files=@report.pdf" \
  -F "files=@notes.docx"
```

**Response:**
```json
{
  "status": "completed",
  "results": [
    {
      "filename": "report.pdf",
      "status": "success",
      "chunks_created": 42,
      "document_name": "report"
    },
    {
      "filename": "notes.docx",
      "status": "success",
      "chunks_created": 18,
      "document_name": "notes"
    }
  ],
  "total_chunks_in_store": 60
}
```

**Status Codes:**
- `200`: Upload completed
- `400`: No files provided
- `500`: Processing error

---

### 3. Chat / Query

**POST** `/chat`

Submit a question and get an answer augmented with retrieved context.

**Request Body:**
```json
{
  "question": "What is the main topic?",
  "top_k": 5
}
```

**Parameters:**
- `question` (string, required): User's question
- `top_k` (integer, optional): Number of context chunks to retrieve (default: 5, max: 20)

**Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is artificial intelligence?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "Based on the documents, artificial intelligence is the simulation of human intelligence...",
  "context": "[Document 1]\nArtificial intelligence is a branch of computer science...\n\n[Document 2]\nAI systems learn from data...",
  "sources": [
    {
      "chunk": "Artificial intelligence is a branch of computer science that aims to create...",
      "similarity": 0.89
    },
    {
      "chunk": "Machine learning is a subset of artificial intelligence...",
      "similarity": 0.85
    }
  ]
}
```

**Status Codes:**
- `200`: Answer generated successfully
- `400`: No documents in vector store
- `500`: Generation error

---

### 4. List Documents

**GET** `/documents`

Get a list of all loaded documents and their chunk counts.

**Response:**
```json
{
  "documents": {
    "report": 42,
    "notes": 18,
    "manual": 35
  },
  "total_chunks": 95
}
```

---

### 5. Clear Documents

**DELETE** `/clear`

Remove all documents from the vector store. Requires confirmation.

**Request Body:**
```json
{
  "confirm": true
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/clear \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

**Response:**
```json
{
  "status": "success",
  "message": "All documents cleared from vector store"
}
```

**Status Codes:**
- `200`: Documents cleared
- `400`: Confirmation not provided
- `500`: Clear operation failed

---

### 6. Get Statistics

**GET** `/stats`

Get system statistics and configuration.

**Response:**
```json
{
  "vector_store": {
    "total_chunks": 95,
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "index_type": "FAISS-FlatL2"
  },
  "llm_ready": true,
  "retrieval_top_k": 5,
  "temperature": 0.7
}
```

---

### 7. Root / API Info

**GET** `/`

Get basic API information and available endpoints.

**Response:**
```json
{
  "name": "RAG Chatbot API",
  "version": "1.0.0",
  "endpoints": {
    "health": "GET /health",
    "upload": "POST /upload",
    "chat": "POST /chat",
    "documents": "GET /documents",
    "clear": "DELETE /clear",
    "stats": "GET /stats"
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Question answered successfully |
| 400 | Bad Request | Missing required parameter, no docs in store |
| 500 | Server Error | Model not loaded, processing failed |

---

## CORS Configuration

The API includes CORS middleware allowing requests from any origin:

```python
CORSMiddleware(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production**, restrict to specific origins:
```python
allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
```

---

## Authentication

**Current:** None (suitable for local/trusted networks)

**For production**, implement:
- JWT tokens
- API keys
- OAuth 2.0
- Basic authentication

---

## Rate Limiting

**Current:** Unlimited (suitable for local use)

**For production**, add:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## Async Operations

All endpoints are asynchronous. Long-running operations (document processing, LLM generation) are handled efficiently without blocking the server.

For very large batches, consider:
- Pagination for `/documents`
- Chunked uploads for large files
- Background task queues (Celery)

---

## Integration Examples

### Python Requests Library

```python
import requests

API_URL = "http://localhost:8000"

# Upload documents
with open("document.pdf", "rb") as f:
    files = {"files": f}
    response = requests.post(f"{API_URL}/upload", files=files)
    print(response.json())

# Query
response = requests.post(
    f"{API_URL}/chat",
    json={"question": "What is the summary?", "top_k": 5}
)
print(response.json()["answer"])
```

### JavaScript Fetch

```javascript
const API_URL = "http://localhost:8000";

async function queryRAG(question) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: 5 })
  });
  const data = await response.json();
  return data.answer;
}
```

### cURL

```bash
# Get health status
curl http://localhost:8000/health

# Upload file
curl -X POST http://localhost:8000/upload -F "files=@doc.pdf"

# Ask question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about...", "top_k": 5}'
```

---

## Development

### Running with Hot Reload

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Create test file: tests/test_api.py
pytest tests/ -v
```

---

## Performance Tuning

### Parameters in Backend

Edit `backend/main.py`:

```python
# Reduce context length for faster inference
rag_engine.set_top_k(3)  # Retrieve fewer chunks

# Reduce LLM temperature for deterministic answers
rag_engine.set_temperature(0.3)

# Increase API timeout for long-running queries
uvicorn.run(app, timeout_keep_alive=120)
```

### Hardware Considerations

- **CPU-only**: 4-8 cores, 8+ GB RAM
- **With GPU**: NVIDIA CUDA (set `n_gpu_layers > 0` in LLM config)

---

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
CMD ["python", "backend/main.py"]
```

### Systemd Service

```ini
[Unit]
Description=RAG Chatbot API
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/rag-chatbot
ExecStart=/usr/bin/python3 backend/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Support

For issues or questions:
1. Check the main [SETUP.md](SETUP.md) guide
2. Review troubleshooting section
3. Check API logs for detailed error messages
