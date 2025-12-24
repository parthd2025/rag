# RAG System - Process Flows

## 1. Document Upload & Ingestion Process

```
┌─────────────────────────────────────────────────────────────────┐
│                     DOCUMENT UPLOAD FLOW                        │
└─────────────────────────────────────────────────────────────────┘

USER
  │
  ├─→ Select File (PDF/DOCX/TXT/MD/CSV/XLSX/PPTX/HTML)
  │
  ├─→ POST /upload
  │
  ▼
┌─────────────────┐
│ VALIDATION      │
├─────────────────┤
│ • File size     │  (Max 10MB)
│ • File type     │  (Allowed extensions)
│ • Not empty     │
└────────┬────────┘
         │
         ├─→ [FAIL] → Return HTTP 400 Error
         │
         ├─→ [SUCCESS]
         │
         ▼
┌─────────────────────────────┐
│ DOCUMENT PROCESSING         │
├─────────────────────────────┤
│ 1. Parse File Content       │
│    • PDF → Extract text     │
│    • DOCX → Extract text    │
│    • TXT → Read file        │
│    • MD → Parse markdown    │
│    • CSV/XLSX → Convert     │
│                             │
│ 2. Clean Text              │
│    • Remove metadata        │
│    • Normalize whitespace   │
│    • Handle encoding        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ TEXT CHUNKING               │
├─────────────────────────────┤
│ Chunk Size: 1000 chars      │
│ Overlap: 200 chars          │
│                             │
│ Split document into         │
│ overlapping chunks for      │
│ semantic search             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ EMBEDDING GENERATION        │
├─────────────────────────────┤
│ Model: all-MiniLM-L6-v2     │
│                             │
│ Convert each chunk to       │
│ 384-dimensional vector      │
│ representation              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ VECTOR STORE (FAISS)        │
├─────────────────────────────┤
│ • Index chunks              │
│ • Store embeddings          │
│ • Save to chroma_db/        │
│ • Persist on disk           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ SUCCESS RESPONSE            │
├─────────────────────────────┤
│ • File uploaded ✓           │
│ • Chunks created: N         │
│ • Status: Ready for Q&A     │
└─────────────────────────────┘
```

---

## 2. Chat Query & RAG Retrieval Process

```
┌─────────────────────────────────────────────────────────────────┐
│                   CHAT QUERY & RAG FLOW                         │
└─────────────────────────────────────────────────────────────────┘

USER INPUT
  │
  ├─→ Ask Question
  │
  ├─→ POST /chat with QueryRequest
  │   {
  │     "question": "What is...?",
  │     "top_k": 5
  │   }
  │
  ▼
┌─────────────────────────────┐
│ QUERY VALIDATION            │
├─────────────────────────────┤
│ • Question not empty        │
│ • Length 1-1000 chars       │
│ • top_k between 1-20        │
└────────┬────────────────────┘
         │
         ├─→ [FAIL] → HTTP 400 Error
         │
         ├─→ [SUCCESS]
         │
         ▼
┌─────────────────────────────┐
│ EMBEDDING GENERATION        │
├─────────────────────────────┤
│ Convert question to         │
│ 384-dimensional vector      │
│ using same model as docs    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ VECTOR SEARCH (RETRIEVAL)   │
├─────────────────────────────┤
│ Search FAISS index for      │
│ semantically similar chunks │
│                             │
│ Return top_k (default: 5)   │
│ most relevant chunks        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ CONTEXT ASSEMBLY            │
├─────────────────────────────┤
│ Combine top chunks into     │
│ context window with:        │
│ • Source document info      │
│ • Relevance scores          │
│ • Chunk metadata            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ LLM GENERATION              │
├─────────────────────────────┤
│ Provider: Groq              │
│ Model: llama-3.3-70b        │
│ Temperature: 0.7            │
│ Max tokens: 512             │
│                             │
│ Prompt:                     │
│ "Context: [chunks]          │
│  Question: [user_question]  │
│  Answer:"                   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ RESPONSE FORMATTING         │
├─────────────────────────────┤
│ • Generated answer          │
│ • Source citations          │
│ • Confidence score          │
│ • Retrieved chunks summary  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ SEND RESPONSE               │
├─────────────────────────────┤
│ QueryResponse {             │
│   "answer": "...",          │
│   "sources": [...]          │
│ }                           │
└─────────────────────────────┘
```

---

## 3. Quiz Generation Process

```
┌─────────────────────────────────────────────────────────────────┐
│                  QUIZ GENERATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

USER
  │
  ├─→ Request Quiz
  │
  ├─→ POST /quiz with QuizRequest
  │   {
  │     "num_questions": 5
  │   }
  │
  ▼
┌─────────────────────────────┐
│ VALIDATION                  │
├─────────────────────────────┤
│ • num_questions: 1-20       │
│ • Documents exist           │
└────────┬────────────────────┘
         │
         ├─→ [FAIL] → HTTP 400/404 Error
         │
         ├─→ [SUCCESS]
         │
         ▼
┌─────────────────────────────┐
│ CHUNK SELECTION             │
├─────────────────────────────┤
│ Randomly select diverse     │
│ chunks from vector store    │
│ to generate questions from  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ QUESTION GENERATION         │
├─────────────────────────────┤
│ For each chunk:             │
│ • Generate question         │
│ • Create multiple choice    │
│   (A, B, C, D options)      │
│ • Mark correct answer       │
│                             │
│ LLM Model: llama-3.3-70b    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ RESPONSE FORMATTING         │
├─────────────────────────────┤
│ QuizResponse {              │
│   "questions": [            │
│     {                        │
│       "question": "...",     │
│       "options": [...],      │
│       "correct": "A",        │
│       "source": "..."        │
│     }                        │
│   ]                          │
│ }                            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ SEND QUIZ                   │
├─────────────────────────────┤
│ Return N questions ready    │
│ for user to answer          │
└─────────────────────────────┘
```

---

## 4. System Health & Status Check Process

```
┌─────────────────────────────────────────────────────────────────┐
│              HEALTH CHECK & STATUS FLOW                         │
└─────────────────────────────────────────────────────────────────┘

USER / MONITORING SYSTEM
  │
  ├─→ GET /health
  │
  ▼
┌─────────────────────────────┐
│ CHECK COMPONENT STATUS      │
├─────────────────────────────┤
│ 1. Vector Store             │
│    • Is initialized?        │
│    • Chunk count loaded     │
│                             │
│ 2. LLM Engine               │
│    • Is API key valid?      │
│    • Can connect to API?    │
│                             │
│ 3. RAG Engine               │
│    • Is ready?              │
│    • Dependencies OK?       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ AGGREGATE STATUS            │
├─────────────────────────────┤
│ {                            │
│   "status": "ok",            │
│   "llm_ready": true/false,   │
│   "chunks": N,               │
│   "vector_store_init": ...,  │
│   "rag_engine_init": ...     │
│ }                            │
└─────────────────────────────┘
```

---

## 5. Data Management Process

```
┌─────────────────────────────────────────────────────────────────┐
│            DATA MANAGEMENT & CLEANUP FLOW                       │
└─────────────────────────────────────────────────────────────────┘

OPERATIONS:

A) GET DOCUMENTS
   │
   ├─→ GET /documents
   │
   ▼
   ┌──────────────────────────┐
   │ Retrieve Document Stats  │
   ├──────────────────────────┤
   │ • Total chunks           │
   │ • Document count         │
   │ • Storage usage          │
   │ • Last update time       │
   └──────────────────────────┘


B) CLEAR ALL DATA
   │
   ├─→ DELETE /clear
   │
   ▼
   ┌──────────────────────────┐
   │ Confirmation Required    │
   ├──────────────────────────┤
   │ Are you sure? [Y/N]      │
   └────────┬─────────────────┘
            │
            ├─→ [NO] → Abort
            │
            ├─→ [YES]
            │
            ▼
   ┌──────────────────────────┐
   │ DELETE PROCESS           │
   ├──────────────────────────┤
   │ • Clear FAISS index      │
   │ • Remove all vectors     │
   │ • Clear chunk storage    │
   │ • Delete embeddings      │
   │ • Flush chroma_db/       │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ SUCCESS RESPONSE         │
   ├──────────────────────────┤
   │ • All data cleared ✓     │
   │ • System reset           │
   │ • Ready for new upload   │
   └──────────────────────────┘
```

---

## 6. System Initialization Process

```
┌─────────────────────────────────────────────────────────────────┐
│              SYSTEM STARTUP FLOW                                │
└─────────────────────────────────────────────────────────────────┘

SERVER START
  │
  ├─→ FastAPI Application Launch
  │
  ▼
┌─────────────────────────────┐
│ STEP 1: Load Configuration  │
├─────────────────────────────┤
│ • Read .env file            │
│ • Load API keys             │
│ • Set parameters            │
│ • Validate settings         │
└────────┬────────────────────┘
         │
         ├─→ [FAIL] → Log ERROR, continue
         │
         ├─→ [SUCCESS]
         │
         ▼
┌─────────────────────────────┐
│ STEP 2: Initialize Logging  │
├─────────────────────────────┤
│ • Setup logger              │
│ • Create log files          │
│ • Set log level             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ STEP 3: Load Vector Store   │
├─────────────────────────────┤
│ • Load existing FAISS index │
│ • Load ChromaDB             │
│ • Load stored embeddings    │
│ • Initialize vector store   │
└────────┬────────────────────┘
         │
         ├─→ [FAIL] → Log WARNING
         │
         ├─→ [SUCCESS]
         │
         ▼
┌─────────────────────────────┐
│ STEP 4: Initialize LLM      │
├─────────────────────────────┤
│ • Connect to Groq API       │
│ • Validate API key          │
│ • Load LLM model            │
│ • Test connectivity         │
└────────┬────────────────────┘
         │
         ├─→ [FAIL] → Log WARNING
         │
         ├─→ [SUCCESS]
         │
         ▼
┌─────────────────────────────┐
│ STEP 5: Initialize RAG      │
├─────────────────────────────┤
│ • Combine components        │
│ • Configure RAG engine      │
│ • Set retrieval params      │
│ • Ready for queries         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ STARTUP COMPLETE            │
├─────────────────────────────┤
│ ✓ Configuration loaded      │
│ ✓ Logging initialized       │
│ ✓ Vector store ready        │
│ ✓ LLM connected             │
│ ✓ RAG engine active         │
│                             │
│ Server ready on :8001       │
└─────────────────────────────┘
```

---

## 7. Error Handling & Recovery Process

```
┌─────────────────────────────────────────────────────────────────┐
│         ERROR HANDLING & RECOVERY FLOW                          │
└─────────────────────────────────────────────────────────────────┘

ERROR OCCURS
  │
  ├─→ Exception Caught
  │
  ▼
┌─────────────────────────────┐
│ ERROR CLASSIFICATION        │
├─────────────────────────────┤
│ Type of Error:              │
│ • Validation Error (400)    │
│ • Not Found (404)           │
│ • Server Error (500)        │
│ • Timeout Error (504)       │
└────────┬────────────────────┘
         │
         ├─→ HTTP 400 (Bad Request)
         │   └─→ Return validation message
         │
         ├─→ HTTP 404 (Not Found)
         │   └─→ Return not found message
         │
         ├─→ HTTP 500 (Server Error)
         │   └─→ Log full error details
         │   └─→ Return generic error
         │
         ├─→ HTTP 504 (Timeout)
         │   └─→ Log timeout
         │   └─→ Suggest retry
         │
         ▼
┌─────────────────────────────┐
│ LOG ERROR DETAILS           │
├─────────────────────────────┤
│ • Timestamp                 │
│ • Error type & message      │
│ • Stack trace               │
│ • Request context           │
│ • Recovery action taken     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ RECOVERY ATTEMPT            │
├─────────────────────────────┤
│ • Reset on critical error?  │
│ • Retry with backoff?       │
│ • Return cached response?   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ SEND ERROR RESPONSE         │
├─────────────────────────────┤
│ {                            │
│   "error": "...",            │
│   "detail": "...",           │
│   "status": HTTP_CODE        │
│ }                            │
└─────────────────────────────┘
```

---

## 8. Data Flow Summary

```
┌──────────────────────────────────────────────────────────────────┐
│              COMPLETE SYSTEM DATA FLOW                           │
└──────────────────────────────────────────────────────────────────┘

                    USER INTERACTION
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    UPLOAD            QUERY/CHAT         QUIZ/STATUS
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐   ┌────────────┐
    │  Document  │    │  Question  │   │  Request   │
    │  Ingest    │    │  Retrieval │   │  Handler   │
    └────┬───────┘    └────┬───────┘   └────┬───────┘
         │                 │                 │
         ▼                 ▼                 ▼
    ┌──────────────────────────────────────────┐
    │           VECTOR STORE (FAISS)           │
    │  • Embeddings                            │
    │  • Chunks                                │
    │  • Metadata                              │
    └──────────────────────────────────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    STORAGE         RETRIEVAL          STATISTICS
    ┌──────┐        ┌──────────┐       ┌──────────┐
    │Saved │        │Top-k     │       │Document  │
    │  &   │        │Similar   │       │Count &   │
    │Index │        │Chunks    │       │Stats     │
    └──┬───┘        └────┬─────┘       └──────────┘
       │                 │
       │                 ▼
       │            ┌──────────────┐
       │            │  LLM ENGINE  │
       │            │  (Groq API)  │
       │            └────┬─────────┘
       │                 │
       │                 ▼
       │            ┌──────────────┐
       │            │RESPONSE GEN. │
       │            └────┬─────────┘
       │                 │
       └─────────┬───────┘
                 │
                 ▼
         ┌──────────────────┐
         │ SEND TO CLIENT   │
         │ (JSON Response)  │
         └──────────────────┘
```

---

## 9. Configuration & Environment Process

```
┌─────────────────────────────────────────────────────────────────┐
│         CONFIGURATION MANAGEMENT FLOW                           │
└─────────────────────────────────────────────────────────────────┘

APPLICATION START
  │
  ├─→ Check .env file
  │
  ▼
┌─────────────────────────────┐
│ ENVIRONMENT VARIABLES       │
├─────────────────────────────┤
│ API CONFIGURATION:          │
│ • API_HOST (default: 0.0.0.0)
│ • API_PORT (default: 8001)  │
│ • FRONTEND_PORT (default: 8501)
│                             │
│ LLM CONFIGURATION:          │
│ • LLM_PROVIDER (groq)       │
│ • LLM_MODEL (llama-3.3)     │
│ • GROQ_API_KEY              │
│                             │
│ RAG CONFIGURATION:          │
│ • EMBEDDING_MODEL           │
│ • CHUNK_SIZE (default: 1000)│
│ • CHUNK_OVERLAP (default: 200)
│ • TOP_K (default: 8)        │
│ • TEMPERATURE (default: 0.7)│
│ • MAX_TOKENS (default: 512) │
│                             │
│ STORAGE CONFIGURATION:      │
│ • MAX_FILE_SIZE (10MB)      │
│ • ALLOWED_EXTENSIONS        │
│ • VECTORSTORE_PATH          │
└─────────────────────────────┘
```

---

## Summary

The RAG system consists of 9 major processes:

1. **Upload & Ingestion** - Document parsing, chunking, embedding
2. **Query & Retrieval** - Question embedding and similarity search
3. **Quiz Generation** - Automated question creation from documents
4. **Health Checks** - System status monitoring
5. **Data Management** - Document statistics and cleanup
6. **System Init** - Startup configuration and component loading
7. **Error Handling** - Exception management and recovery
8. **Data Flow** - Complete information pipeline
9. **Configuration** - Environment and setting management

All processes are logged, monitored, and error-handled for production reliability.
