---
source_doc: baseline-overview
version: 2.0.0
owner: platform-team
tags:
  - overview
  - onboarding
  - groq
  - cloud
---

# RAG Chatbot - Cloud-Powered & Lightning Fast

A production-ready RAG (Retrieval-Augmented Generation) chatbot powered by Groq Cloud API for blazing-fast responses.

## Features

✅ Upload PDFs, DOCX, TXT, Markdown  
✅ Semantic search with FAISS  
✅ Groq Cloud API with Llama-3.3-70B (lightning fast)  
✅ Web UI (Streamlit)  
✅ REST API (FastAPI)  
✅ Zero local model requirements  
✅ Sub-second response times  

## Quick Start (4 commands)

```bash
# 1. Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start backend
cd backend && python main.py

# 4. Start frontend (new terminal)
cd frontend && streamlit run app.py
```

Open **http://localhost:8501** 🎉

## Setup

### Prerequisites
- Python 3.10+
- 2GB RAM (4GB recommended)
- Groq API Key (free tier available)
- Internet connection

### Step 1: Get Groq API Key
1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Save it securely

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Create `.env` file in project root:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Or set environment variable:
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# Windows CMD
set GROQ_API_KEY=your_groq_api_key_here

# Linux/Mac
export GROQ_API_KEY="your_groq_api_key_here"
```

### Step 4: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Backend runs on: http://localhost:8001

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```
Frontend runs on: http://localhost:8501

### Step 5: Use the App
1. Go to http://localhost:8501
2. Upload documents
3. Ask questions and get instant answers

## Architecture

```
Frontend (Streamlit)
    ↓ REST API (Port 8001)
Backend (FastAPI)
    ├ Document Processing
    ├ FAISS Vector Database
    └ Groq Cloud API (Llama-3.3-70B)
```

## How It Works

1. **Upload Document** → Extract text → Create semantic chunks
2. **Generate Embeddings** → Store in FAISS vector database
3. **Ask Question** → Search top 10 similar chunks
4. **Build Context** → Send to Groq API → Get lightning-fast answer

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if running |
| `/upload` | POST | Upload documents |
| `/chat` | POST | Ask questions |
| `/documents` | GET | List documents |
| `/clear` | DELETE | Clear all data |

### Example: Ask a Question

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "top_k": 10}'
```

### Example: Check Health

```bash
curl http://localhost:8001/health
```

## Configuration

### Model Settings
Current configuration (optimized for quality):
- **Model**: llama-3.3-70b-versatile
- **TOP_K**: 10 (retrieves top 10 relevant chunks)
- **Temperature**: 0.3 (balanced creativity/accuracy)
- **Max Tokens**: 800 (detailed responses)

### Change Groq Model
Edit `backend/config.py`:
```python
GROQ_MODEL = "llama-3.3-70b-versatile"  # or "llama-3.1-70b-versatile"
```

### Adjust Retrieval Settings
Edit `backend/rag_engine.py`:
```python
TOP_K = 10          # Number of chunks to retrieve
TEMPERATURE = 0.3   # Response creativity (0.0-2.0)
MAX_TOKENS = 800    # Response length limit
```

### Change Embedding Model
Edit `backend/vectorstore.py`:
```python
embedding_model_name = "all-MiniLM-L6-v2"  # Lightweight & fast
```

### Adjust Chunking
Edit `backend/ingest.py`:
```python
DocumentIngestor(chunk_size=1000, chunk_overlap=200)
```

## Troubleshooting

### "Cannot connect to API"
- Check backend is running: `python backend/main.py`
- Verify backend health: http://localhost:8001/health
- Ensure port 8001 is not blocked by firewall

### "Groq API Error"
- Verify GROQ_API_KEY is set correctly
- Check API key has credits remaining
- Ensure internet connection is stable
- Visit https://console.groq.com to check account status

### "Failed to retrieve context"
- Upload documents first via web interface
- Check documents were processed successfully
- Verify FAISS index was created in `data/embeddings/`

### "Port already in use"
- Backend uses port 8001, frontend uses 8501
- Kill existing processes: `netstat -ano | findstr :8001`
- Change ports in config files if needed

### Frontend won't connect to backend
- Ensure backend is running on http://localhost:8001
- Check `frontend/utils/api_client.py` has correct URL
- Verify no proxy/firewall blocking requests

## Performance

**Cloud API Performance:**
- Document upload: 1-3 seconds
- Semantic search: 50-100ms
- Groq API response: 0.5-2 seconds
- **Total response time: 1-3 seconds**

**Resource Usage:**
- RAM: ~500MB (no local models)
- CPU: Minimal (only for embeddings)
- Disk: ~50MB (no model storage)
- Network: API calls only

## Files

```
backend/
  ├ main.py          FastAPI server (port 8001)
  ├ config.py        Groq API configuration
  ├ vectorstore.py   FAISS vector database
  ├ llm_loader.py    Groq API integration
  ├ ingest.py        Document processing
  ├ rag_engine.py    RAG orchestration
  └ requirements.txt Dependencies

frontend/
  ├ app.py           Streamlit UI (port 8501)
  └ utils/
    └ api_client.py  Backend API client

data/
  ├ embeddings/      FAISS vector index
  └ documents/       Uploaded document cache

.env                 Environment variables
```

## Technologies

- **FastAPI** - High-performance web server
- **Streamlit** - Interactive web UI  
- **FAISS** - Lightning-fast vector search
- **Sentence Transformers** - Document embeddings
- **Groq API** - Ultra-fast LLM inference
- **PyPDF2** - PDF text extraction
- **python-docx** - Word document processing

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "backend/main.py"]
```

Build and run:
```bash
docker build -t rag-chatbot .
docker run -p 8001:8001 -e GROQ_API_KEY=your_key_here rag-chatbot
```

### Production Tips
- Store GROQ_API_KEY in secure secret management
- Use environment-specific configurations
- Enable HTTPS for production deployments
- Monitor API usage and costs
- Implement rate limiting for public access

## Costs & Limits

**Groq Free Tier:**
- 14,400 requests per day
- 6,000 tokens per minute
- Perfect for development and small apps

**Typical Usage:**
- Document upload: 0 tokens
- Each question: ~500-1000 tokens
- Daily cost: $0-$2 (depending on usage)

## License

MIT - Free to use and modify

## Support

- **API Issues?** Check https://console.groq.com/docs
- **Setup Problems?** Verify GROQ_API_KEY and internet connection
- **Performance?** Groq is optimized for speed - expect sub-second responses
- **Questions?** See inline code comments and API documentation

---

**Ready to go? Set your API key and run:** 
```bash
export GROQ_API_KEY="your_key_here" && pip install -r requirements.txt && cd backend && python main.py
```

