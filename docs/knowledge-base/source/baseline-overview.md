---
source_doc: baseline-overview
version: 1.0.0
owner: platform-team
tags:
  - overview
  - onboarding
---

# RAG Chatbot - Simple & Fast

A simple, production-ready RAG (Retrieval-Augmented Generation) chatbot. 100% offline, no API costs.

## Features

✅ Upload PDFs, DOCX, TXT, Markdown  
✅ Semantic search with FAISS  
✅ Local LLM (Mistral, Phi-3, Qwen)  
✅ Web UI (Streamlit)  
✅ REST API (FastAPI)  
✅ Zero cloud dependencies  

## Quick Start (3 commands)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start backend
cd backend && python main.py

# 3. Start frontend (new terminal)
cd frontend && streamlit run app.py
```

Open **http://localhost:8501** 🎉

## Setup

### Prerequisites
- Python 3.10+
- 4GB RAM (8GB recommended)
- 10GB disk space (for LLM model)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download a Model (Optional)
Download a GGUF model:
- **Mistral-7B**: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
- **Phi-3-Mini**: https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF

Save to `models/` directory

Example:
```
models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Step 3: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

### Step 4: Use the App
1. Go to http://localhost:8501
2. Upload documents
3. Ask questions

## Architecture

```
Frontend (Streamlit)
    ↓ REST API
Backend (FastAPI)
    ├ Document Processing
    ├ FAISS Vector Database
    └ Local LLM Engine
```

## How It Works

1. **Upload Document** → Extract text → Create chunks
2. **Generate Embeddings** → Store in FAISS
3. **Ask Question** → Search similar chunks
4. **Build Prompt** → Send to LLM → Get answer

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if running |
| `/upload` | POST | Upload documents |
| `/chat` | POST | Ask questions |
| `/documents` | GET | List docs |
| `/clear` | DELETE | Clear all |

### Example: Ask a Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "top_k": 5}'
```

## Configuration

### Change Model
Edit `backend/main.py`:
```python
llm_engine = get_llm_engine(use_llama_cpp=True)
# Set model_path in LocalLLMEngine
```

### Change Embedding Model
Edit `backend/vectorstore.py`:
```python
embedding_model_name="all-MiniLM-L6-v2"  # Change here
```

### Chunk Size
Edit `backend/ingest.py`:
```python
DocumentIngestor(chunk_size=1000, chunk_overlap=200)
```

## Troubleshooting

### "Cannot connect to API"
- Check backend is running: `python backend/main.py`
- Check http://localhost:8000/health returns 200

### "Model not loaded"
- Download a GGUF model to `models/` directory
- Check model filename matches code

### Slow responses
- First response loads LLM (slow)
- CPU-only is naturally slow (10-30s)
- Use GPU if available (10x faster)

### Port already in use
- Backend uses 8000, frontend uses 8501
- Change in code if needed

## Performance

**CPU (4-core, 8GB RAM):**
- Embedding: 2-3 seconds
- Search: 100ms
- LLM generation: 10-30 seconds

**With GPU (NVIDIA CUDA):**
- LLM generation: 2-5 seconds (10x faster)

## Files

```
backend/
  ├ main.py          FastAPI server
  ├ vectorstore.py   FAISS database
  ├ llm_loader.py    LLM engine
  ├ ingest.py        Document processing
  ├ rag_engine.py    RAG logic
  └ requirements.txt  Dependencies

frontend/
  └ app.py           Streamlit UI

data/
  ├ embeddings/      FAISS index
  └ documents/       Upload cache

models/
  └ (GGUF models go here)
```

## Technologies

- **FastAPI** - Web server
- **Streamlit** - Web UI
- **FAISS** - Vector search
- **Sentence Transformers** - Embeddings
- **llama-cpp-python** - Local LLM
- **PyPDF2** - PDF extraction
- **python-docx** - DOCX extraction

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend/main.py"]
```

Run:
```bash
docker build -t rag-chatbot .
docker run -p 8000:8000 rag-chatbot
```

## License

MIT - Free to use and modify

## Support

- **Issues?** Check troubleshooting section
- **Questions?** See inline code comments
- **Models?** Visit https://huggingface.co

---

**Ready to go? Run:** `pip install -r requirements.txt && cd backend && python main.py`

