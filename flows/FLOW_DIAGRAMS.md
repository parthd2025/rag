# Visual Flow Diagrams

## 📊 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   main.py    │  ← Entry Point (CLI)
                    │ main() - L9  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  RAGSystem   │  ← Main Orchestrator
                    │ __init__ L27 │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│PDF Processor │  │Vector Store  │  │Embedding &  │
│extract L8    │  │__init__ L16  │  │embedder L39  │
│chunk L30     │  │add_doc L33   │  │model L49     │
│              │  │search L67    │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔄 Loading a PDF - Detailed Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PDF LOADING PROCESS                               │
└─────────────────────────────────────────────────────────────────────┘

User Command:
python main.py load document.pdf
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Parse Command & Initialize                              │
├─────────────────────────────────────────────────────────────────┤
│  main.main() - line 9                                           │
│    └─→ Parse arguments (line 33)                                │
│    └─→ Create RAGSystem (line 41)                               │
│                                                                 │
│  RAGSystem.__init__() - rag_system.py:27                        │
│    • Load Sentence Transformer (line 39)                      │
│    • Connect to Google Gemini API (line 47-49)                  │
│    • Initialize VectorStore (line 50)                           │
│      └─→ VectorStore.__init__() - vector_store.py:16            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Extract Text from PDF                                   │
├─────────────────────────────────────────────────────────────────┤
│  main.main() calls rag.load_pdf() - main.py:49                  │
│    └─→ RAGSystem.load_pdf() - rag_system.py:52                  │
│        └─→ extract_text_from_pdf() - pdf_processor.py:8         │
│                                                                 │
│  Function: extract_text_from_pdf(pdf_path)                     │
│  File: pdf_processor.py, Line: 8                                │
│                                                                 │
│  PDF File                                                       │
│    │                                                            │
│    ├─→ Page 1: "Introduction to machine learning..."           │
│    ├─→ Page 2: "Neural networks are..."                       │
│    ├─→ Page 3: "Deep learning uses..."                        │
│    └─→ ...                                                      │
│                                                                 │
│  Result: "Introduction to machine learning... Neural networks   │
│           are... Deep learning uses..."                        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Chunk Text                                              │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.load_pdf() calls chunk_text() - rag_system.py:67     │
│    └─→ chunk_text() - pdf_processor.py:30                       │
│                                                                 │
│  Function: chunk_text(text, chunk_size=1000, overlap=200)      │
│  File: pdf_processor.py, Line: 30                              │
│                                                                 │
│  Input:  "Very long text..." (10,000 characters)               │
│                                                                 │
│  Process:                                                       │
│    Chunk 1: [0:1000]     "Introduction to machine..."          │
│    Chunk 2: [800:1800]   "...machine learning. Neural..."      │
│    Chunk 3: [1600:2600]  "...Neural networks are..."           │
│    ...                                                          │
│                                                                 │
│  Result: ["Chunk 1...", "Chunk 2...", "Chunk 3...", ...]       │
│          (~10 chunks for 10k chars)                            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Generate Embeddings                                     │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.load_pdf() - rag_system.py:72                       │
│    └─→ self.embedder.encode(chunks)                            │
│                                                                 │
│  Function: embedder.encode()                                    │
│  Location: rag_system.py, Line: 72                              │
│  (Sentence Transformer library method)                         │
│                                                                 │
│  Input:  ["Chunk 1...", "Chunk 2...", ...]                     │
│                                                                 │
│  Process:                                                       │
│    Chunk 1 → [0.23, -0.45, 0.67, ..., 0.12]  (384 numbers)    │
│    Chunk 2 → [0.25, -0.43, 0.65, ..., 0.11]  (384 numbers)    │
│    Chunk 3 → [0.28, -0.41, 0.63, ..., 0.15]  (384 numbers)    │
│    ...                                                          │
│                                                                 │
│  Result: [[0.23, -0.45, ...], [0.25, -0.43, ...], ...]         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Store in Vector Database                               │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.load_pdf() calls vector_store.add_document()        │
│    └─→ rag_system.py:78                                         │
│        └─→ VectorStore.add_document() - vector_store.py:33     │
│                                                                 │
│  Function: VectorStore.add_document(chunks, embeddings, doc)   │
│  File: vector_store.py, Line: 33                               │
│                                                                 │
│  ChromaDB Collection:                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ID              │ Embedding      │ Text        │ Metadata│  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ doc_chunk_0    │ [0.23, -0.45..]│ "Chunk 1..." │ doc.pdf │  │
│  │ doc_chunk_1    │ [0.25, -0.43..]│ "Chunk 2..." │ doc.pdf │  │
│  │ doc_chunk_2    │ [0.28, -0.41..]│ "Chunk 3..." │ doc.pdf │  │
│  │ ...            │ ...            │ ...         │ ...     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Saved to: chroma_db/ folder (persistent)                       │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
✅ PDF Successfully Loaded!
```

---

## 🔍 Querying - Detailed Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    QUERY PROCESS                                    │
└─────────────────────────────────────────────────────────────────────┘

User Command:
python main.py query "What is machine learning?"
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Parse Command & Check Documents                        │
├─────────────────────────────────────────────────────────────────┤
│  main.main() - line 9                                          │
│    └─→ Parse arguments (line 33)                               │
│    └─→ Create RAGSystem (line 41)                              │
│    └─→ Call rag.query() - main.py:56                           │
│        └─→ RAGSystem.query() - rag_system.py:81                │
│            └─→ Check if documents loaded (line 92)            │
│                └─→ vector_store.get_chunk_count() - vector_store.py:135
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Convert Question to Embedding                           │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.query() - rag_system.py:96                          │
│    └─→ self.embedder.encode(question)                           │
│                                                                 │
│  Function: embedder.encode()                                   │
│  Location: rag_system.py, Line: 96                             │
│  (Sentence Transformer library method)                         │
│                                                                 │
│  Input:  "What is machine learning?"                            │
│                                                                 │
│  Process:                                                       │
│    Question → [0.25, -0.43, 0.65, ..., 0.12]                   │
│              (384 numbers representing the question)            │
│                                                                 │
│  Result: query_vector = [0.25, -0.43, 0.65, ..., 0.12]         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Search for Similar Chunks                               │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.query() calls vector_store.search() - rag_system.py:99
│    └─→ VectorStore.search() - vector_store.py:67              │
│                                                                 │
│  Function: VectorStore.search(query_embedding, top_k=3)        │
│  File: vector_store.py, Line: 67                               │
│                                                                 │
│  Process:                                                       │
│    1. Convert embedding to list (line 79)                      │
│    2. Query ChromaDB (line 82)                                 │
│    3. Format results (line 88-97)                              │
│    4. Return top 3                                             │
│                                                                 │
│  Similarity Scores:                                             │
│    Chunk 1: "Machine learning is..." → 0.92 (92% match) ✓      │
│    Chunk 2: "ML algorithms..."      → 0.85 (85% match) ✓        │
│    Chunk 3: "AI and ML..."         → 0.82 (82% match) ✓        │
│    Chunk 4: "Python programming..." → 0.15 (15% match) ✗       │
│                                                                 │
│  Result: Top 3 chunks with highest similarity                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Build Context Prompt                                    │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.query() - rag_system.py:105                         │
│    └─→ Build context string (line 105)                         │
│    └─→ Construct prompt (line 108-116)                         │
│                                                                 │
│  Function: RAGSystem.query() (prompt building)                 │
│  File: rag_system.py, Lines: 105-116                           │
│                                                                 │
│  Context:                                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [From document.pdf]                                      │  │
│  │ Machine learning is a subset of artificial intelligence │  │
│  │ that enables systems to learn from data...              │  │
│  │                                                          │  │
│  │ [From document.pdf]                                      │  │
│  │ ML algorithms can be supervised or unsupervised...       │  │
│  │                                                          │  │
│  │ [From document.pdf]                                      │  │
│  │ AI and ML are closely related fields...                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Question: "What is machine learning?"                          │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Generate Answer with Gemini AI                          │
├─────────────────────────────────────────────────────────────────┤
│  RAGSystem.query() - rag_system.py:119                         │
│    └─→ self.model.generate_content(prompt)                     │
│                                                                 │
│  Function: model.generate_content()                            │
│  Location: rag_system.py, Line: 119                            │
│  (Google Gemini API call)                                      │
│                                                                 │
│  Input to Gemini:                                               │
│  """                                                            │
│  You are a helpful assistant...                                 │
│                                                                 │
│  Context from documents:                                        │
│  [From document.pdf]                                            │
│  Machine learning is a subset of AI...                          │
│  ...                                                            │
│                                                                 │
│  Question: What is machine learning?                            │
│  """                                                            │
│                                                                 │
│  Gemini Processing:                                             │
│    1. Reads context                                             │
│    2. Understands question                                      │
│    3. Generates answer based on context                         │
│                                                                 │
│  Output:                                                        │
│  "Machine learning is a subset of artificial intelligence       │
│   that enables systems to learn and improve from experience    │
│   without being explicitly programmed..."                       │
│                                                                 │
│  Return to main.py (line 56) → Display answer (line 59)        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
✅ Answer Returned to User
```

---

## 🔗 Component Interactions

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTION DIAGRAM                    │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   User       │
                    └──────┬───────┘
                           │ Commands
                           ▼
                    ┌──────────────┐
                    │   main.py    │
                    │ main() L9    │
                    │              │
                    │  • Parse CLI │
                    │  • Route cmds│
                    └──────┬───────┘
                           │
                           │ Creates
                           ▼
                    ┌──────────────┐
                    │  RAGSystem   │
                    │ __init__ L27 │
                    │              │
                    │  • Orchestrates│
                    │  • Manages   │
                    └───┬──────┬───┘
                        │      │
        ┌───────────────┘      └───────────────┐
        │                                      │
        ▼                                      ▼
┌──────────────┐                      ┌──────────────┐
│PDF Processor │                      │Vector Store   │
│extract L8    │                      │__init__ L16   │
│chunk L30     │                      │add_doc L33    │
│              │                      │search L67     │
│• Extract    │                      │• Add docs    │
│• Chunk      │                      │• Search      │
└──────────────┘                      │• Persist     │
                                      └──────┬───────┘
                                             │
                                             │ Uses
                                             ▼
                                      ┌──────────────┐
                                      │  ChromaDB    │
                                      │  (Database)  │
                                      └──────────────┘

                    ┌──────────────┐
                    │  RAGSystem   │
                    │ load_pdf L52 │
                    │ query L81    │
                    └───┬──────┬───┘
                        │      │
        ┌───────────────┘      └───────────────┐
        │                                      │
        ▼                                      ▼
┌──────────────┐                      ┌──────────────┐
│Sentence      │                      │Google Gemini │
│Transformer   │                      │              │
│encode L72    │                      │generate L119 │
│encode L96    │                      │              │
│              │                      │• Generate    │
│• Encode text │                      │  answers     │
│• Create      │                      │              │
│  embeddings  │                      │              │
└──────────────┘                      └──────────────┘
```

---

## 📦 Data Structures Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA TRANSFORMATION PIPELINE                     │
└─────────────────────────────────────────────────────────────────────┘

PDF File (binary)
    │
    ▼
String (text)
    "Introduction to machine learning. Neural networks..."
    │
    ▼
List[String] (chunks)
    [
      "Introduction to machine learning. Neural...",
      "...learning. Neural networks are...",
      "...networks are computational models..."
    ]
    │
    ▼
List[np.ndarray] (embeddings)
    [
      array([0.23, -0.45, 0.67, ..., 0.12]),  # 384 numbers
      array([0.25, -0.43, 0.65, ..., 0.11]),  # 384 numbers
      array([0.28, -0.41, 0.63, ..., 0.15])   # 384 numbers
    ]
    │
    ▼
ChromaDB Storage
    {
      ids: ["doc_chunk_0", "doc_chunk_1", ...],
      embeddings: [[0.23, -0.45, ...], [0.25, -0.43, ...], ...],
      documents: ["Chunk 1...", "Chunk 2...", ...],
      metadatas: [{"document_name": "doc.pdf"}, ...]
    }
    │
    ▼
Query Time:
    Question String
        │
        ▼
    Query Vector (np.ndarray)
        │
        ▼
    Search Results: List[Tuple]
        [
          ("Chunk text...", 0.92, "doc.pdf"),  # (text, score, doc)
          ("Chunk text...", 0.85, "doc.pdf"),
          ("Chunk text...", 0.82, "doc.pdf")
        ]
        │
        ▼
    Prompt String
        "Context: ...\nQuestion: ..."
        │
        ▼
    Answer String
        "Machine learning is..."
```

---

## 🎯 Similarity Search Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│              HOW SIMILARITY SEARCH WORKS                            │
└─────────────────────────────────────────────────────────────────────┘

Stored Chunks in Database:
┌──────────────────────────────────────────────────────────────────┐
│ Chunk 1: "Machine learning is a subset of AI"                   │
│ Vector: [0.23, -0.45, 0.67, ..., 0.12]                          │
├──────────────────────────────────────────────────────────────────┤
│ Chunk 2: "Python is a programming language"                     │
│ Vector: [0.89, 0.12, -0.34, ..., -0.56]                         │
├──────────────────────────────────────────────────────────────────┤
│ Chunk 3: "Deep learning uses neural networks"                   │
│ Vector: [0.28, -0.41, 0.63, ..., 0.15]                          │
└──────────────────────────────────────────────────────────────────┘

User Question:
"What is machine learning?"
Vector: [0.25, -0.43, 0.65, ..., 0.11]

Similarity Calculation:
┌──────────────────────────────────────────────────────────────────┐
│ Question vs Chunk 1:                                              │
│   Cosine Similarity = 0.92 (92% similar) ✓ TOP MATCH            │
│                                                                   │
│ Question vs Chunk 3:                                              │
│   Cosine Similarity = 0.78 (78% similar) ✓ RELEVANT             │
│                                                                   │
│ Question vs Chunk 2:                                              │
│   Cosine Similarity = 0.15 (15% similar) ✗ NOT RELEVANT         │
└──────────────────────────────────────────────────────────────────┘

Results (top_k=3):
1. Chunk 1 (score: 0.92) ← Most relevant
2. Chunk 3 (score: 0.78) ← Relevant
3. Chunk 2 (score: 0.15) ← Less relevant, but included
```

---

## 🔄 Complete End-to-End Flow

```
START
  │
  ├─→ [User] python main.py load doc.pdf
  │
  ├─→ [main.py] main() - line 9
  │     └─→ Parse command (line 33)
  │     └─→ Create RAGSystem() (line 41)
  │           └─→ RAGSystem.__init__() - rag_system.py:27
  │                 • Load Sentence Transformer (line 39)
  │                 • Connect Gemini API (line 47-49)
  │                 • VectorStore.__init__() - vector_store.py:16
  │
  ├─→ [RAGSystem] load_pdf("doc.pdf") - rag_system.py:52
  │     │
  │     ├─→ [PDF Processor] extract_text_from_pdf() - pdf_processor.py:8
  │     │     └─→ "Full text content..."
  │     │
  │     ├─→ [PDF Processor] chunk_text() - pdf_processor.py:30
  │     │     └─→ ["Chunk 1", "Chunk 2", ...]
  │     │
  │     ├─→ [Sentence Transformer] embedder.encode() - rag_system.py:72
  │     │     └─→ [[0.23, ...], [0.25, ...], ...]
  │     │
  │     └─→ [Vector Store] add_document() - vector_store.py:33
  │           └─→ Persisted to disk (ChromaDB)
  │
  └─→ ✅ PDF Loaded
        │
        ├─→ [User] python main.py query "Question?"
        │
        ├─→ [main.py] main() - line 9
        │     └─→ rag.query() - main.py:56
        │           └─→ RAGSystem.query() - rag_system.py:81
        │                 │
        │                 ├─→ [Sentence Transformer] embedder.encode() - rag_system.py:96
        │                 │     └─→ [0.25, -0.43, ...]
        │                 │
        │                 ├─→ [Vector Store] search() - vector_store.py:67
        │                 │     └─→ Top 3 chunks found
        │                 │
        │                 ├─→ [RAGSystem] Build prompt - rag_system.py:105-116
        │                 │     └─→ Context + Question
        │                 │
        │                 └─→ [Gemini API] model.generate_content() - rag_system.py:119
        │                       └─→ "Answer text..."
        │
        └─→ ✅ Answer displayed (main.py:59)
```

---

## 💾 Persistence Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE                                  │
└─────────────────────────────────────────────────────────────────────┘

Session 1:
  Load PDF → ChromaDB → Save to chroma_db/ folder
    │
    └─→ RAGSystem.load_pdf() - rag_system.py:78
        └─→ VectorStore.add_document() - vector_store.py:33
            └─→ ChromaDB saves automatically (line 60-65)
    │
    └─→ chroma_db/
        ├── chroma.sqlite3 (metadata)
        └── [collection_id]/
            ├── data_level0.bin
            ├── header.bin
            └── ...

Session 2 (Restart):
  Start RAGSystem → ChromaDB loads from chroma_db/
    │
    └─→ RAGSystem.__init__() - rag_system.py:50
        └─→ VectorStore.__init__() - vector_store.py:16
            └─→ chromadb.PersistentClient() loads existing data (line 24)
    │
    └─→ All previous documents available!
        │
        └─→ Can query immediately without reloading

Clear Command:
  python main.py clear
    │
    └─→ main.main() - main.py:75
        └─→ RAGSystem.clear() - rag_system.py:131
            └─→ VectorStore.clear() - vector_store.py:101
                └─→ Deletes collection (line 105) → chroma_db/ folder cleared
```

---

## 📋 Function Reference Table

Quick reference for all key functions with their file locations and line numbers:

| Function Name | File | Line | Purpose |
|--------------|------|------|---------|
| `main()` | main.py | 9 | CLI entry point, parses commands |
| `RAGSystem.__init__()` | rag_system.py | 27 | Initialize RAG system, load models |
| `RAGSystem.load_pdf()` | rag_system.py | 52 | Load and process PDF file |
| `RAGSystem.query()` | rag_system.py | 81 | Answer questions using RAG |
| `RAGSystem.list_documents()` | rag_system.py | 122 | List all loaded documents |
| `RAGSystem.clear()` | rag_system.py | 131 | Clear all documents |
| `extract_text_from_pdf()` | pdf_processor.py | 8 | Extract text from PDF file |
| `chunk_text()` | pdf_processor.py | 30 | Split text into chunks |
| `VectorStore.__init__()` | vector_store.py | 16 | Initialize ChromaDB |
| `VectorStore.add_document()` | vector_store.py | 33 | Store chunks and embeddings |
| `VectorStore.search()` | vector_store.py | 67 | Search for similar chunks |
| `VectorStore.clear()` | vector_store.py | 101 | Clear all stored data |
| `VectorStore.get_document_list()` | vector_store.py | 114 | Get list of document names |
| `VectorStore.get_chunk_count()` | vector_store.py | 135 | Get total chunk count |

### External Library Functions Used:

| Function/Method | Library | Used In | Line |
|----------------|---------|---------|------|
| `embedder.encode()` | Sentence Transformers | rag_system.py | 72, 96 |
| `model.generate_content()` | Google Gemini API | rag_system.py | 119 |
| `chromadb.PersistentClient()` | ChromaDB | vector_store.py | 24 |

---

*These diagrams show the complete flow of data and control through your RAG system with function names and line numbers for easy code navigation!*



## Detailed Condition Flows (File / Function / Lines / Next Step)

### 1. `backend/main.py::upload` (L168–L286)

| File            | Function | Lines     | Condition / Step                                   | If Condition TRUE (failure)                                                              | If Condition FALSE (next step)                                     |
|----------------|----------|-----------|----------------------------------------------------|------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| backend/main.py | upload  | 175–184   | `if not vector_store`                             | Log `UPLOAD STEP 1 FAILED`; raise `HTTPException(500, "Vector store not initialized")`   | Log `UPLOAD STEP 1 COMPLETE`; go to Step 2 (validate files)       |
| backend/main.py | upload  | 186–193   | `if not files`                                    | Log `UPLOAD STEP 2 FAILED`; raise `HTTPException(400, "No files provided")`              | Log `UPLOAD STEP 2 COMPLETE`; enter loop `for idx, file in files` |
| backend/main.py | upload  | 206–218   | `if not file_ext or file_ext not in allowed_extensions` | Log `UPLOAD STEP 3.{idx}.1 FAILED`; append `status="error"` result; increment `error_count` | Log `UPLOAD STEP 3.{idx}.1 COMPLETE`; go to size validation       |
| backend/main.py | upload  | 225–233   | `if file_size > settings.MAX_FILE_SIZE`           | Log `UPLOAD STEP 3.{idx}.2 FAILED`; append size `error` result; increment `error_count`  | Continue to zero-size check                                        |
| backend/main.py | upload  | 235–243   | `if file_size == 0`                               | Log `UPLOAD STEP 3.{idx}.2 FAILED`; append “File is empty”; increment `error_count`      | Log `UPLOAD STEP 3.{idx}.2 COMPLETE`; call `ingestor.process_uploaded_file` |
| backend/main.py | upload  | 251–262   | `if chunks`                                       | Log `UPLOAD STEP 3.{idx}.4`; call `vector_store.add_chunks`; append `status="ok"` result; `success_count++` | Log path; already in success branch                               |
| backend/main.py | upload  | 263–269   | `else` (no chunks)                                | Log `UPLOAD STEP 3.{idx} FAILED: No chunks extracted`; append `status="error"` result; `error_count++` | N/A                                                                |
| backend/main.py | upload  | 271–273   | `except HTTPException`                            | Log `UPLOAD STEP 3.{idx} FAILED`; re-raise `HTTPException`                               | N/A                                                                |
| backend/main.py | upload  | 274–281   | `except Exception as e`                           | Log `UPLOAD STEP 3.{idx} FAILED: Error processing file`; append `status="error"` result; `error_count++` | N/A                                                                |
| backend/main.py | upload  | 283–286   | Finalize                                          | Log `UPLOAD ... COMPLETE` with success/error counts and total chunks; return JSON        | N/A                                                                |


### 2. `backend/ingest.py::process_uploaded_file` (L540–L603)

| File             | Function              | Lines    | Condition / Step                                      | If Condition TRUE (failure)                                                         | If Condition FALSE (next step)                          |
|-----------------|-----------------------|----------|-------------------------------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------|
| backend/ingest.py | process_uploaded_file | 553–556 | `if not file_content` (STEP 1)                        | Log `STEP 1 FAILED: Empty file content provided`; return `([], "unknown")`         | Log `STEP 1 COMPLETE`; proceed to temp directory        |
| backend/ingest.py | process_uploaded_file | 560–566 | `try: temp_path.parent.mkdir(...)` (STEP 2)           | On exception: log `STEP 2 FAILED`; return `([], filename or "unknown")`            | Log `STEP 2 COMPLETE`; proceed to write temp file       |
| backend/ingest.py | process_uploaded_file | 569–576 | `try: open(temp_path, 'wb')` (STEP 3)                 | On exception: log `STEP 3 FAILED`; return `([], filename or "unknown")`            | Log `STEP 3 COMPLETE`; proceed to process document      |
| backend/ingest.py | process_uploaded_file | 579–588 | `try: load_and_process_documents([temp_path])` (STEP 4) | On exception: log `STEP 4 FAILED`; return `([], filename or "unknown")`           | If `chunks`: log `STEP 4 COMPLETE`; else log `STEP 4 FAILED`; return `(chunks, doc_name)` |
| backend/ingest.py | process_uploaded_file | 595–602 | `finally` cleanup (STEP 5)                            | If `unlink` fails: log `STEP 5 FAILED` warning; no change to returned result        | On success: log `STEP 5 COMPLETE` or debug              |


### 3. `backend/ingest.py::load_and_process_documents` (L37–L113)

| File             | Function                    | Lines  | Condition / Step                                 | If Condition TRUE (failure)                                                | If Condition FALSE (next step)                           |
|-----------------|-----------------------------|--------|--------------------------------------------------|----------------------------------------------------------------------------|----------------------------------------------------------|
| backend/ingest.py | load_and_process_documents | 49–52  | `if not file_paths` (STEP 1)                     | Log `STEP 1 FAILED: No file paths provided`; return `([], "unknown")`      | Log `STEP 1 COMPLETE`; proceed to loop over file_paths   |
| backend/ingest.py | load_and_process_documents | 61–68  | `if not os.path.exists(file_path)` (STEP 2.{idx}) | Log `STEP 2.{idx} FAILED: File not found`; `failed_count++`; `continue`   | Log `STEP 2.{idx}.1 COMPLETE`; proceed to `_extract_text` |
| backend/ingest.py | load_and_process_documents | 72–84  | `try: text = self._extract_text(...)` (STEP 2.{idx}.2) | On exception: log `STEP 2.{idx} FAILED`; `failed_count++`; `continue`    | If `text.strip()`: append text + name; else log `FAILED` and `failed_count++` |
| backend/ingest.py | load_and_process_documents | 92–95  | `if not all_text.strip()` (STEP 3)               | Log `STEP 3 FAILED: No text extracted from any files`; return `([], "unknown")` | Log `STEP 3 COMPLETE`; proceed to chunking               |
| backend/ingest.py | load_and_process_documents | 98–107 | `try: chunks = self._chunk_text(all_text)` (STEP 4) | If `not chunks`: log `STEP 4 FAILED`; return `([], "unknown")`; on exception: log and return `([], "unknown")` | Log `STEP 4 COMPLETE`; continue                          |
| backend/ingest.py | load_and_process_documents | 110–113| STEP 5 result composition                        | Log flow COMPLETE; return `(chunks, doc_name)`                               | N/A                                                      |


### 4. `backend/rag_engine.py::answer_query_with_context` (L81–202)

| File               | Function                   | Lines   | Condition / Step                                     | If Condition TRUE (failure)                                                              | If Condition FALSE (next step)                       |
|-------------------|----------------------------|---------|------------------------------------------------------|------------------------------------------------------------------------------------------|------------------------------------------------------|
| backend/rag_engine.py | answer_query_with_context | 93–100 | `if not question or not question.strip()` (RAG STEP 1) | Log `RAG STEP 1 FAILED: Empty question provided`; return `"Please provide a valid question."` | Log `RAG STEP 1 COMPLETE`; proceed to LLM validation |
| backend/rag_engine.py | answer_query_with_context | 104–110| `if not self.llm_engine.is_ready()` (STEP 2)         | Log `RAG STEP 2 FAILED: LLM engine not ready`; return `"Error: LLM service not available..."` | Log `RAG STEP 2 COMPLETE`; proceed to search         |
| backend/rag_engine.py | answer_query_with_context | 114–126| `results = self.vector_store.search(...)` (STEP 3)   | On exception: log `RAG STEP 3 FAILED`; return `"Error searching documents: ..."`        | If `not results`: log `RAG STEP 3 FAILED`; return `"No documents found..."`; else continue |
| backend/rag_engine.py | answer_query_with_context | 135–151| Build context/sources (STEP 4)                      | On exception: log `RAG STEP 4 FAILED`; return `"Error building context: ..."`           | Log `RAG STEP 4 COMPLETE`; proceed to build prompt   |
| backend/rag_engine.py | answer_query_with_context | 160–170| Build prompt (STEP 5)                               | On exception: log `RAG STEP 5 FAILED`; return `"Error building prompt: ..."` plus context/sources | Log `RAG STEP 5 COMPLETE`; proceed to generate       |
| backend/rag_engine.py | answer_query_with_context | 173–195| Generate answer (STEP 6)                            | On exception: log `RAG STEP 6 FAILED`; return `"Error processing query: ..."`           | If `answer`: log COMPLETE and return; else return `"Error: Empty response from LLM."` |


### 5. `backend/vectorstore.py::search` (L165–225)

| File                | Function | Lines   | Condition / Step                              | If Condition TRUE (failure)                                        | If Condition FALSE (next step)                         |
|--------------------|----------|---------|-----------------------------------------------|--------------------------------------------------------------------|--------------------------------------------------------|
| backend/vectorstore.py | search | 179–182 | `if not self.chunks` (SEARCH STEP 1)          | Log `SEARCH STEP 1 FAILED: No chunks available`; return `[]`       | Log `SEARCH STEP 1 COMPLETE`; proceed to query validation      |
| backend/vectorstore.py | search | 185–187 | `if not query or not query.strip()` (STEP 2)  | Log `SEARCH STEP 2 FAILED: Empty query provided`; return `[]`     | Log `SEARCH STEP 2 COMPLETE`; proceed to embedding              |
| backend/vectorstore.py | search | 190–197 | Generate query embedding (STEP 3)             | On exception (caught as `SEARCH FAILED`): return `[]`             | Log `SEARCH STEP 3 COMPLETE`; proceed to index.search          |
| backend/vectorstore.py | search | 199–203 | `self.index.search(query_emb, k)` (STEP 4)    | On exception: log `SEARCH FAILED: Error during search`; return `[]` | Log `SEARCH STEP 4 COMPLETE`; proceed to processing results     |
| backend/vectorstore.py | search | 205–221 | Process `indices`/`distances` (STEP 5)        | Invalid indices: log warnings and skip those entries; only outer exception returns `[]` | On success: log `SEARCH COMPLETE` and return results   |


### 6. `backend/vectorstore.py::add_chunks` (L113–163)

| File                | Function   | Lines   | Condition / Step                                | If Condition TRUE (failure)                                            | If Condition FALSE (next step)                         |
|--------------------|------------|---------|-------------------------------------------------|------------------------------------------------------------------------|--------------------------------------------------------|
| backend/vectorstore.py | add_chunks | 123–126 | `if not chunks` (ADD_CHUNKS STEP 1)            | Log `ADD_CHUNKS STEP 1 FAILED: No chunks provided`; `return`           | Log `ADD_CHUNKS STEP 1 COMPLETE`; proceed to embeddings             |
| backend/vectorstore.py | add_chunks | 129–139 | Generate embeddings (STEP 2)                   | On exception: outer `except` logs `ADD_CHUNKS FAILED` and **raises**   | Log `ADD_CHUNKS STEP 2 COMPLETE`; proceed to shape validation       |
| backend/vectorstore.py | add_chunks | 141–147 | `if embeddings.shape[1] != self.embedding_dim` (STEP 3) | Log `ADD_CHUNKS STEP 3 FAILED: Dimension mismatch`; raise `ValueError` | Log `ADD_CHUNKS STEP 3 COMPLETE`; proceed to adding to index        |
| backend/vectorstore.py | add_chunks | 150–154 | Add to FAISS index (STEP 4)                    | On exception: outer `except` logs and **raises**                       | Log `ADD_CHUNKS STEP 4 COMPLETE`; proceed to save index             |
| backend/vectorstore.py | add_chunks | 156–160 | `_save_index()` (STEP 5)                       | On exception: outer `except` logs and **raises**                       | Log `ADD_CHUNKS STEP 5 COMPLETE` and flow COMPLETE                  |


### 7. `backend/main.py::init_components` (L66–113)

| File            | Function        | Lines   | Condition / Step                                             | If Condition TRUE (failure)                                                          | If Condition FALSE (next step)                                   |
|----------------|-----------------|---------|--------------------------------------------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------|
| backend/main.py | init_components | 70–72  | Start init: log `"=== Starting RAG system initialization flow ==="` | N/A                                                                          | Proceed to STEP 1                                               |
| backend/main.py | init_components | 73–80  | STEP 1 – create `DocumentIngestor(...)`                      | If `DocumentIngestor.__init__` raises: caught by outer `except`, log `INIT FAILED` and **re-raise** | Log `INIT STEP 1 COMPLETE`; proceed to STEP 2                    |
| backend/main.py | init_components | 82–89  | STEP 2 – create `FAISSVectorStore(...)`                      | If `FAISSVectorStore.__init__` raises: caught, log `INIT FAILED`, **re-raise**      | Log `INIT STEP 2 COMPLETE` (chunks count); proceed to STEP 3     |
| backend/main.py | init_components | 91–97  | STEP 3 – `llm_engine = get_llm_engine(...)` + `is_ready()`   | If `get_llm_engine` raises: caught, log `INIT FAILED`, **re-raise**; if LLM not ready: log `INIT STEP 3 FAILED` but continue | If ready: log `INIT STEP 3 COMPLETE`; then go to STEP 4          |
| backend/main.py | init_components | 99–107 | STEP 4 – create `RAGEngine(...)`                             | If `RAGEngine.__init__` raises: caught, log `INIT FAILED`, **re-raise**            | Log `INIT STEP 4 COMPLETE`; log `INIT flow COMPLETE`            |
| backend/main.py | init_components | 111–113| Outer `except Exception as e`                                | Any failure in any step: log `INIT FAILED: Failed to initialize components: {e}`; **re-raise** | N/A                                                              |


### 8. `backend/main.py::chat` (L289–345)

| File            | Function | Lines   | Condition / Step                                                       | If Condition TRUE (failure)                                                                 | If Condition FALSE (next step)                                |
|----------------|----------|---------|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| backend/main.py | chat     | 292–293| Start: log `"=== Starting chat endpoint flow for query: ... ==="`     | N/A                                                                                         | Proceed to STEP 1                                             |
| backend/main.py | chat     | 295–300| STEP 1 – `if not rag_engine`                                          | Log `CHAT STEP 1 FAILED: RAG engine not initialized`; raise `HTTPException(500)`           | Log `CHAT STEP 1 COMPLETE`; proceed to STEP 2                 |
| backend/main.py | chat     | 304–309| STEP 2 – `if not llm_engine or not llm_engine.is_ready()`             | Log `CHAT STEP 2 FAILED: LLM not ready`; raise `HTTPException(503)`                        | Log `CHAT STEP 2 COMPLETE`; proceed to STEP 3                 |
| backend/main.py | chat     | 313–318| STEP 3 – `if not vector_store or not vector_store.chunks`             | Log `CHAT STEP 3 FAILED: No documents loaded`; raise `HTTPException(400)`                  | Log `CHAT STEP 3 COMPLETE` (chunks count); proceed to STEP 4  |
| backend/main.py | chat     | 323–325| STEP 4 – set top_k and call `rag_engine.answer_query_with_context()`  | If `set_top_k` or RAG call raises: handled by `except` blocks below                        | On success, `result` dict is available; proceed to answer check |
| backend/main.py | chat     | 327–336| STEP 4 answer check – `if result.get("answer")` else error            | If falsy: log `CHAT STEP 4 FAILED: Empty answer returned`; raise `HTTPException(500)`      | Log `CHAT STEP 4 COMPLETE` and `Chat flow COMPLETE`; return `QueryResponse` |
| backend/main.py | chat     | 337–339| `except HTTPException`                                                | Log `CHAT STEP 4 FAILED: HTTPException raised`; re-raise same `HTTPException`              | N/A                                                           |
| backend/main.py | chat     | 340–345| `except Exception as e`                                               | Log `CHAT STEP 4 FAILED: Error processing query: {e}`; raise `HTTPException(500)`          | N/A                                                           |