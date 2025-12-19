# Data Architecture & Processing Pipeline

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   USER LAYER     │
│   (Streamlit UI) │  Port: 8501
└────────┬─────────┘
         │ HTTP/REST
         │
┌────────▼──────────────────────────────────────┐
│        API LAYER (FastAPI)                    │  Port: 8001
│  ┌──────────────────────────────────────┐    │
│  │ • Routing                             │    │
│  │ • Request Validation                  │    │
│  │ • Error Handling                      │    │
│  │ • CORS Middleware                     │    │
│  └──────────────────────────────────────┘    │
└────────┬──────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────┐
│      BUSINESS LOGIC LAYER                     │
│  ┌──────────────┐   ┌──────────────┐          │
│  │ RAG Engine   │   │ LLM Engine   │          │
│  │ • Retrieval  │   │ • Generation │          │
│  │ • Ranking    │   │ • Streaming  │          │
│  └──────┬───────┘   └──────┬───────┘          │
│         │                  │                  │
│  ┌──────▼──────────────────▼────┐             │
│  │   Document Processor         │             │
│  │  • Parsing (PDF, DOCX, etc)  │             │
│  │  • Chunking                  │             │
│  │  • Embedding Generation      │             │
│  └──────┬───────────────────────┘             │
└────────┼──────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────┐
│      DATA STORAGE LAYER                       │
│  ┌──────────────┐   ┌──────────────────────┐ │
│  │  FAISS Index │   │  ChromaDB Metadata   │ │
│  │  • Vectors   │   │  • Chunk Info        │ │
│  │  • Embeddings│   │  • Doc References    │ │
│  └──────────────┘   └──────────────────────┘ │
│  ┌──────────────────────────────────────┐    │
│  │  File System                         │    │
│  │  • chroma_db/ (Vector Store)         │    │
│  │  • backend/data/ (Documents)         │    │
│  │  • logs/ (System Logs)               │    │
│  └──────────────────────────────────────┘    │
└───────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────┐
│    EXTERNAL SERVICES                          │
│  ┌──────────────────────────────────────┐    │
│  │ Groq API (LLM)                        │    │
│  │ • llama-3.3-70b-versatile             │    │
│  │ • Query Response Generation           │    │
│  │ • Quiz Creation                       │    │
│  └──────────────────────────────────────┘    │
│  ┌──────────────────────────────────────┐    │
│  │ HuggingFace (Embeddings)              │    │
│  │ • all-MiniLM-L6-v2                    │    │
│  │ • Document Embedding                 │    │
│  │ • Query Embedding                     │    │
│  └──────────────────────────────────────┘    │
└───────────────────────────────────────────────┘
```

---

## Data Processing Pipeline

### Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│           DOCUMENT TO ANSWER PIPELINE                       │
└─────────────────────────────────────────────────────────────┘

DOCUMENT INGESTION PHASE:
═════════════════════════

1. INPUT
   ┌──────────────────────────┐
   │ • PDF/DOCX/TXT/MD/etc    │
   │ • CSV/XLSX/PPTX/HTML     │
   │ • File size: < 10MB      │
   └──────────────────────────┘
         │
         ▼
2. PARSING
   ┌──────────────────────────┐
   │ Extract raw text from:   │
   │ • PDF → PyPDF2/pdfplumber│
   │ • DOCX → python-docx     │
   │ • TXT → plain read       │
   │ • CSV → pandas           │
   │ • HTML → BeautifulSoup   │
   └──────────────────────────┘
         │
         ▼
3. TEXT CLEANING
   ┌──────────────────────────┐
   │ • Remove metadata        │
   │ • Normalize whitespace   │
   │ • Fix encoding issues    │
   │ • Remove invalid chars   │
   └──────────────────────────┘
         │
         ▼
4. CHUNKING
   ┌──────────────────────────┐
   │ Chunk Size: 1000 chars   │
   │ Overlap: 200 chars       │
   │                          │
   │ Process:                 │
   │ Text → [Chunk1, Chunk2,  │
   │         Chunk3, ...]     │
   │                          │
   │ Each chunk = Semantic    │
   │ unit for embedding       │
   └──────────────────────────┘
         │
         ▼
5. EMBEDDING GENERATION
   ┌──────────────────────────┐
   │ Model: all-MiniLM-L6-v2  │
   │ Dimensions: 384          │
   │                          │
   │ Chunk → 384-dim Vector   │
   │ Each chunk is converted  │
   │ to numerical representation
   └──────────────────────────┘
         │
         ▼
6. STORAGE
   ┌──────────────────────────┐
   │ Store in Vector DB:      │
   │ • FAISS Index            │
   │ • ChromaDB Metadata      │
   │ • Chunk Content          │
   │ • Source References      │
   └──────────────────────────┘


QUERY RESOLUTION PHASE:
══════════════════════

1. USER QUESTION
   ┌──────────────────────────┐
   │ "What is the meaning of..?"
   │ Max: 1000 characters     │
   └──────────────────────────┘
         │
         ▼
2. QUESTION EMBEDDING
   ┌──────────────────────────┐
   │ Question → 384-dim Vector│
   │ (same model as docs)     │
   │ Ensures semantic match   │
   └──────────────────────────┘
         │
         ▼
3. VECTOR SEARCH
   ┌──────────────────────────┐
   │ FAISS Similarity Search  │
   │ • L2 distance            │
   │ • Cosine similarity      │
   │ • Top K selection        │
   │ • Default K: 5           │
   │ • Max K: 20              │
   └──────────────────────────┘
         │
         ▼
4. CHUNK RETRIEVAL
   ┌──────────────────────────┐
   │ Retrieved Top-K Chunks:  │
   │ • Chunk 1 (score: 0.95)  │
   │ • Chunk 3 (score: 0.87)  │
   │ • Chunk 5 (score: 0.82)  │
   │ • Chunk 2 (score: 0.79)  │
   │ • Chunk 7 (score: 0.75)  │
   └──────────────────────────┘
         │
         ▼
5. CONTEXT ASSEMBLY
   ┌──────────────────────────┐
   │ Combine chunks into:     │
   │                          │
   │ "Context:                │
   │  [Chunk1 content]        │
   │  [Chunk3 content]        │
   │  [Chunk5 content]        │
   │  [Chunk2 content]        │
   │  [Chunk7 content]        │
   │                          │
   │  Question:               │
   │  [User question]"        │
   └──────────────────────────┘
         │
         ▼
6. LLM GENERATION
   ┌──────────────────────────┐
   │ Groq API (llama-3.3-70b) │
   │                          │
   │ Input: Context + Question│
   │ Params:                  │
   │ • temp: 0.7              │
   │ • max_tokens: 512        │
   │ • top_p: 0.95            │
   │                          │
   │ Output: Generated Answer │
   └──────────────────────────┘
         │
         ▼
7. RESPONSE FORMATTING
   ┌──────────────────────────┐
   │ Format final response:   │
   │ {                        │
   │   "answer": "...",       │
   │   "sources": [           │
   │     {                    │
   │       "chunk": "...",    │
   │       "score": 0.95,     │
   │       "doc": "file.pdf"  │
   │     }                    │
   │   ]                      │
   │ }                        │
   └──────────────────────────┘
         │
         ▼
8. RESPONSE DELIVERY
   ┌──────────────────────────┐
   │ Send to client (JSON)    │
   │ Streamed or chunked      │
   │ Timeout: 180 seconds     │
   └──────────────────────────┘
```

---

## Data Storage Architecture

### Directory Structure

```
d:\RAG\
│
├── chroma_db/                    ← Vector Store (FAISS)
│   ├── chroma.sqlite3            ← Database
│   └── [uuid]/                   ← Collection data
│
├── backend/
│   ├── data/
│   │   ├── documents/            ← Ingested documents
│   │   └── embeddings/           ← Cached embeddings
│   ├── logs/                     ← Runtime logs
│   └── services/
│
├── logs/                         ← Centralized logs
│   ├── frontend_logs/            ← UI logs
│   └── backend_logs/             ← API/RAG logs
│
├── config/                       ← Configuration files
├── data/
│   ├── documents/                ← User uploads
│   └── embeddings/               ← Embedding cache
│
└── models/                       ← Model configs
```

---

## Data Models

### Chunk Data Model

```
Chunk {
  id: int                          ← Unique identifier
  content: str                     ← Text content (≤1000 chars)
  source_document: str             ← Original file name
  page_number: int                 ← Page in source (if applicable)
  chunk_index: int                 ← Position in document
  embedding: float[384]            ← Vector representation
  metadata: {
    created_at: timestamp
    last_updated: timestamp
    relevance_score: float
    document_hash: str
  }
}
```

### Query Request Model

```
QueryRequest {
  question: str                    ← 1-1000 chars
  top_k: int (optional)           ← 1-20, default 5
  filters: dict (optional)         ← Metadata filters
  stream: bool (optional)         ← Stream response?
}
```

### Query Response Model

```
QueryResponse {
  answer: str                      ← Generated response
  sources: [
    {
      chunk_id: int
      document: str
      content: str
      relevance_score: float       ← 0-1 similarity score
      page: int
    }
  ]
  metadata: {
    processing_time_ms: int
    chunks_searched: int
    chunks_used: int
    model_used: str
  }
}
```

### Quiz Question Model

```
QuizQuestion {
  id: int
  question: str
  options: [str, str, str, str]   ← A, B, C, D
  correct_answer: str              ← "A", "B", "C", or "D"
  source_chunk_id: int
  source_document: str
  difficulty: str                  ← "easy", "medium", "hard"
  topic: str                       ← Extracted topic
}
```

---

## Embedding & Vectorization

### Embedding Process

```
TEXT CHUNK (1000 chars max)
        │
        ▼
┌──────────────────────────────┐
│ Tokenization                 │
│ • Split into tokens          │
│ • WordPiece tokenization     │
│ • Max length: 512 tokens     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Model: all-MiniLM-L6-v2      │
│ • 22M parameters             │
│ • 6 transformer layers       │
│ • 384 output dimensions      │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Embedding Vector (384-dim)   │
│ [0.23, -0.15, 0.89, ...]    │
│ Normalized (L2)              │
└──────────────────────────────┘
```

### Vector Search Algorithm

```
┌────────────────────────────────────┐
│ FAISS (Facebook AI Similarity)     │
│                                    │
│ Algorithm: IndexFlatL2            │
│ • Exact nearest neighbor search   │
│ • L2 (Euclidean) distance         │
│ • Low latency (<100ms)            │
│ • Suitable for up to 1M vectors  │
└────────────────────────────────────┘

SEARCH PROCESS:
1. Query embedding (384-dim)
2. Calculate distance to all vectors
3. Sort by distance
4. Return top_k closest matches
5. Retrieve metadata & content
```

---

## Performance Characteristics

### Latency Profile

```
Operation          | Typical Time | Max Time | Bottleneck
─────────────────────────────────────────────────────────
File Upload        | 2-5s        | 30s     | Network/Parsing
Embedding Gen      | 0.5-2s      | 5s      | Model Inference
Vector Search      | 50-200ms    | 500ms   | Index size
LLM Generation     | 2-5s        | 20s     | API latency
Total Q&A          | 5-10s       | 30s     | Multiple factors
```

### Storage Requirements

```
Resource          | Per Document | Notes
────────────────────────────────────────────
Document         | 0.5-5 MB     | Original file
Chunks (text)    | 0.1-0.5 MB   | 10 chunks average
Embeddings       | 1.5-6 MB     | 384-dim vectors
Metadata         | 50-200 KB    | Document info
Total per doc    | 2-12 MB      | Rough estimate
```

---

## Data Flow Sequence Diagrams

### Query Processing Sequence

```
USER    FRONTEND    API      RAG ENGINE   VECTOR STORE   LLM
│         │         │          │             │            │
├────────>│ POST /chat
│         ├────────>│ Validate
│         │<────────┤ 200 OK
│         │         ├────────>│ Embed Question
│         │         │<────────┤ Vector
│         │         ├────────────────────>│ Search
│         │         │<────────────────────┤ Top-K
│         │         ├────────>│ Assemble Context
│         │         │         ├─────────────────────>│
│         │         │         │                      │ Generate
│         │         │         │<─────────────────────┤
│         │         │<────────┤ Answer + Metadata
│         │<────────┤ Response
│<────────┤ Display
```

---

## Caching Strategy

```
Layer           | What's Cached        | TTL     | Strategy
──────────────────────────────────────────────────────────
Document Cache  | Parsed docs          | Session | LRU
Embedding Cache | Generated vectors    | Persist | Disk
Vector Index    | FAISS index          | Persist | Disk
Query Cache     | Frequent questions   | 1 hour  | LRU (optional)
Model Cache     | LLM responses        | None    | State-based
```

---

## Error Handling Data Flow

```
ERROR OCCURS
    │
    ├─→ Capture Error
    │
    ├─→ Log Details
    │   ├─→ logs/backend_logs/
    │   ├─→ Timestamp
    │   ├─→ Stack trace
    │   └─→ Context
    │
    ├─→ Classify Error
    │   ├─→ Validation (400)
    │   ├─→ Not Found (404)
    │   ├─→ Server (500)
    │   └─→ Service (503)
    │
    ├─→ Recovery Action
    │   ├─→ Retry?
    │   ├─→ Fallback?
    │   └─→ Cleanup?
    │
    ▼
RESPONSE: Error message to client
```
