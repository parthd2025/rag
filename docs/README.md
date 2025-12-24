# RAG Chatbot System

A production-ready Retrieval-Augmented Generation (RAG) system with FastAPI backend and Streamlit frontend.

## Features

- **Document Processing**: Supports PDF, DOCX, TXT, and Markdown files
- **Vector Search**: FAISS-based semantic search with persistent storage
- **LLM Integration**: Groq API for fast inference
- **Web Interface**: Streamlit frontend for easy interaction
- **REST API**: FastAPI backend with comprehensive error handling
- **Production Ready**: Logging, error handling, validation, and testing

## Documentation Structure

- **knowledge-base/**: Canonical sources that power retrieval. Each file is versioned alongside a manifest describing provenance and ingestion metadata.
- **architecture/**: System and data flow diagrams plus operational narratives for the overall platform.
- **frontend/**: Streamlit UX guides, implementation notes, and rollout history.
- **guides/**: Reserved for step-by-step runbooks or how-to content (add as needed).

When adding new knowledge sources for document-specific Q&A, place the authored or curated material in knowledge-base/source and register it in knowledge-base/manifest.yaml. Derived artifacts such as FAISS indexes continue to live under data/embeddings and stay out of git.

## Architecture

```
┌─────────────┐
│  Frontend   │  Streamlit UI
│  (Streamlit)│
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│   Backend   │  FastAPI REST API
│  (FastAPI)  │
└──────┬──────┘
       │
┌──────▼──────────┐
│  RAG Engine    │
├────────────────┤
│ Vector Store   │  FAISS
│ Document Proc  │  PDF/DOCX/TXT/MD
│ LLM Engine     │  Groq
└────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
API_URL=http://localhost:8001
```

Get a free Groq API key at: https://console.groq.com/keys

### 3. Start Backend

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8001`

### 4. Start Frontend

In a new terminal:

```bash
cd frontend
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

## Configuration

All configuration is managed through environment variables or `.env` file:

- `GROQ_API_KEY`: Groq API key (required)
- `API_HOST`: Backend host (default: 0.0.0.0)
- `API_PORT`: Backend port (default: 8001)
- `EMBEDDING_MODEL`: Embedding model name (default: all-MiniLM-L6-v2)
- `LLM_MODEL`: LLM model name (default: llama-3.3-70b-versatile)
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Chunk overlap (default: 200)
- `MAX_FILE_SIZE`: Max upload size in bytes (default: 10MB)
- `LOG_LEVEL`: Logging level (default: INFO)

See `backend/config.py` for all available options.

## API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload documents
- `POST /chat` - Ask questions
- `GET /documents` - Get document statistics
- `DELETE /clear` - Clear all documents

## Testing

Run tests with pytest:

```bash
pip install -r requirements-dev.txt
pytest
```

## Project Structure

```
RAG/
├── backend/           # FastAPI backend
│   ├── main.py       # API server
│   ├── config.py     # Configuration
│   ├── ingest.py     # Document processing
│   ├── vectorstore.py # FAISS vector store
│   ├── rag_engine.py  # RAG orchestration
│   └── llm_loader.py  # LLM integration
├── frontend/          # Streamlit frontend
│   └── app.py        # UI application
├── tests/            # Test suite
├── requirements.txt  # Dependencies
└── .env             # Environment variables
```

## Improvements Made

✅ Unified configuration management
✅ Comprehensive logging system
✅ Proper error handling (no bare except)
✅ Input validation and security (CORS, file validation)
✅ Type hints throughout
✅ Performance optimizations (caching)
✅ Test infrastructure
✅ Consolidated dependencies
✅ Improved frontend error handling
✅ Resource management and graceful shutdown
✅ Removed duplicate code

## License

MIT

