# Process Flows - Quick Reference

## 📋 Quick Navigation

| Document | Purpose | Use Case |
|----------|---------|----------|
| [SYSTEM_PROCESSES.md](SYSTEM_PROCESSES.md) | 9 major system processes | Understand workflow |
| [API_FLOWS.md](API_FLOWS.md) | API endpoints & flows | Integrate with API |
| [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) | Data pipeline & storage | System design |
| README.md (root) | Getting started | Setup & run system |

---

## 🔄 Main Process Flows

### 1️⃣ Document Upload
**File** → **Parse** → **Chunk** → **Embed** → **Store** → **Ready**

Time: 2-5 seconds | Endpoint: `POST /upload`

### 2️⃣ Chat Query
**Question** → **Embed** → **Search** → **Retrieve** → **LLM** → **Answer**

Time: 5-10 seconds | Endpoint: `POST /chat`

### 3️⃣ Quiz Generation
**Request** → **Select Chunks** → **Generate Q&A** → **Format** → **Response**

Time: 3-8 seconds | Endpoint: `POST /quiz`

### 4️⃣ System Health
**Check** → **Vector Store** → **LLM** → **RAG Engine** → **Status**

Time: <1 second | Endpoint: `GET /health`

### 5️⃣ Data Management
**Get Stats** → **Document Info** → **Storage Info** → **Response**

Time: <1 second | Endpoint: `GET /documents` | `DELETE /clear`

---

## 🚀 Quick Flow Sequences

### Upload & Query Workflow
```
1. POST /upload (document.pdf)
   ↓ 2-5 sec
   ✓ 15 chunks created

2. POST /chat (question)
   ↓ 5-10 sec
   ✓ Answer + sources

3. Repeat step 2
```

### Quiz Workflow
```
1. GET /documents (check what's loaded)
   ↓ <1 sec
   ✓ 42 chunks available

2. POST /quiz (num_questions: 5)
   ↓ 3-8 sec
   ✓ 5 quiz questions

3. User answers & self-grades
```

### System Setup Workflow
```
1. GET /health (verify system)
   ↓ <1 sec
   ✓ All components OK

2. GET /config (view settings)
   ↓ <1 sec
   ✓ Configuration loaded

3. POST /upload (add documents)
   ↓ 2-5 sec per doc
   ✓ Ready for queries
```

---

## 📊 Data Flow Summary

```
USER INPUT
    ↓
API VALIDATION
    ↓
PROCESSING
    ├─ Document: Parse → Chunk → Embed → Store
    ├─ Query: Embed → Search → Retrieve → Generate
    └─ Quiz: Select → Generate → Format
    ↓
RESPONSE OUTPUT
```

---

## ⚙️ Configuration Parameters

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| CHUNK_SIZE | 1000 | - | Document segmentation |
| CHUNK_OVERLAP | 200 | - | Context preservation |
| TOP_K | 8 | 1-20 | Retrieval breadth |
| TEMPERATURE | 0.7 | 0-1 | Response creativity |
| MAX_TOKENS | 512 | - | Response length |
| MAX_FILE_SIZE | 10MB | - | Upload limit |

---

## 🔌 API Endpoints Quick Reference

| Method | Endpoint | Purpose | Time |
|--------|----------|---------|------|
| GET | `/health` | System status | <1s |
| GET | `/config` | Configuration | <1s |
| POST | `/upload` | Add documents | 2-5s |
| POST | `/chat` | Ask questions | 5-10s |
| POST | `/quiz` | Generate quiz | 3-8s |
| GET | `/documents` | Document stats | <1s |
| DELETE | `/clear` | Reset system | 1-2s |

---

## 📁 Directory Organization

```
d:\RAG\
├── flows/              ← Process documentation
│   ├── SYSTEM_PROCESSES.md      ← 9 processes
│   ├── API_FLOWS.md             ← API details
│   ├── DATA_ARCHITECTURE.md     ← Data pipeline
│   └── INDEX.md                 ← This file
├── backend/            ← FastAPI server
├── logs/               ← Centralized logs
│   ├── backend_logs/
│   └── frontend_logs/
├── chroma_db/          ← Vector store
└── README.md           ← Main docs
```

---

## 🔍 Error Handling

| Error | HTTP | Solution |
|-------|------|----------|
| Invalid question | 400 | Validate input (1-1000 chars) |
| File too large | 413 | Use file < 10MB |
| No documents | 404 | Upload document first |
| LLM error | 503 | Check API key, retry |
| Processing error | 500 | Check logs, contact admin |

---

## 📈 Performance Insights

### Latency Breakdown (Chat Query)
- Embedding: 0.5-2s
- Vector Search: 50-200ms
- LLM Generation: 2-5s
- Total: 5-10s

### Storage Usage
- Per document: 2-12 MB
- Vector index: ~1.5-6 MB per 10 chunks
- Metadata: ~50-200 KB per document

### Throughput
- Concurrent users: Limited by LLM API
- Requests/min: ~10-20 (depends on API limits)
- Upload queue: Sequential processing

---

## 🎯 Common Workflows

### Workflow A: Single Document Q&A
```
1. Upload one PDF/document
2. Ask 5-10 questions
3. Review answers with sources
```

### Workflow B: Multi-Document Research
```
1. Upload multiple documents
2. Ask cross-document questions
3. Compare sources
4. Export answers
```

### Workflow C: Knowledge Assessment
```
1. Upload study material
2. Generate quiz (5-20 questions)
3. Take quiz
4. Review incorrect answers
```

### Workflow D: System Maintenance
```
1. Check health status
2. Monitor document count
3. Clear old data if needed
4. Restart if issues
```

---

## 🛠️ Troubleshooting

### Issue: Upload fails
- Check file size < 10MB
- Verify file format supported
- Check API connectivity

### Issue: Query slow
- Reduce top_k parameter
- Check LLM API status
- Review vector store size

### Issue: No results found
- Ensure documents uploaded
- Check question clarity
- Try different phrasing

### Issue: LLM unavailable
- Verify API key in .env
- Check internet connection
- Check Groq API status

---

## 📚 Related Documentation

- **README.md** - System overview & setup
- **backend/config.py** - Configuration details
- **backend/main.py** - API implementation
- **backend/rag_engine.py** - RAG logic

---

## 🔗 External Links

- **Groq API**: https://console.groq.com
- **HuggingFace Models**: https://huggingface.co/models
- **FAISS Docs**: https://faiss.ai/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/

---

## 📝 Version Info

- **System**: RAG Chatbot v1.0.0
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Vector DB**: FAISS + ChromaDB
- **LLM**: Groq (llama-3.3-70b)
- **Embeddings**: all-MiniLM-L6-v2

---

## ⏱️ Last Updated

December 19, 2025

---

*For detailed flows, refer to specific documents in this folder.*
