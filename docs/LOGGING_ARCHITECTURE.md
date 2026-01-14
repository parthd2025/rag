# Logging Architecture Diagram

## Current vs. Proposed

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT STATE (Problem)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  All Modules → Unified Logger → logs/rag_system.log             │
│                                                                   │
│  ├─ Document Service                                             │
│  ├─ Vector Store                                                 │
│  ├─ LLM Engine          ─┐                                       │
│  ├─ API Endpoints        │                                       │
│  ├─ RAG Engine           ├─→ rag_system.log (50-100MB)           │
│  ├─ Dataset Service      │                                       │
│  ├─ Frontend             │                                       │
│  └─ Observability       ─┘                                       │
│                                                                   │
│  ❌ Mixed logs - hard to find issues                             │
│  ❌ Single file grows large                                      │
│  ❌ Difficult to monitor specific components                     │
│  ❌ Can't track performance per module                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│               PROPOSED STATE (Solution)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Document Service      ──→ document_ingestion.log                │
│  Vector Store          ──→ vector_store.log                      │
│  LLM Engine            ──→ llm_queries.log                       │
│  API Endpoints         ──→ api_endpoints.log       ┌─────────┐   │
│  RAG Engine            ──→ rag_engine.log          │ LogManager│   │
│  Dataset Service       ──→ dataset_service.log     │(Central) │   │
│  Observability         ──→ opik_tracing.log        └─────────┘   │
│  Frontend              ──→ streamlit_app.log                      │
│  ALL ERROR Logs        ──→ errors.log                             │
│  Debug (Dev Only)      ──→ debug.log                              │
│                                                                   │
│  ✅ Component-specific logs                                      │
│  ✅ Smaller individual files (easier to manage)                   │
│  ✅ Easy to monitor specific areas                                │
│  ✅ Performance metrics per module                                │
│  ✅ Centralized error aggregation                                 │
│  ✅ Trace IDs for distributed tracing                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
logs/
│
├── rag_system.log
│   └─ PURPOSE: Main application backup log
│   └─ LEVEL: INFO+
│   └─ SIZE: ~10-20MB (rotated at 10MB)
│
├── components/
│   │
│   ├── document_ingestion.log
│   │   └─ Handles: PDF parsing, chunking, embedding
│   │   └─ Performance: chunk rate, parse time
│   │
│   ├── vector_store.log
│   │   └─ Handles: FAISS indexing, vector search
│   │   └─ Performance: search latency, index size
│   │
│   ├── llm_queries.log
│   │   └─ Handles: LLM API calls, token counting
│   │   └─ Performance: latency, tokens, cost tracking
│   │
│   ├── api_endpoints.log
│   │   └─ Handles: FastAPI HTTP requests/responses
│   │   └─ Performance: endpoint latency, status codes
│   │
│   ├── rag_engine.log
│   │   └─ Handles: End-to-end RAG pipeline
│   │   └─ Performance: pipeline latency, step breakdown
│   │
│   ├── dataset_service.log
│   │   └─ Handles: Dataset management, test cases
│   │   └─ Performance: dataset operations
│   │
│   └── opik_tracing.log
│       └─ Handles: Observability, trace creation
│       └─ Performance: tracing overhead
│
├── frontend/
│   │
│   └── streamlit_app.log
│       └─ Handles: UI interactions, page rendering
│       └─ Performance: render time, user actions
│
├── errors.log
│   └─ PURPOSE: Unified ERROR and CRITICAL logs
│   └─ LEVEL: ERROR+ only
│   └─ SOURCES: All modules + custom error handler
│   └─ SIZE: ~5MB (rotated at 5MB, keep 10 backups)
│
└── debug/
    │
    └── debug.log
        └─ PURPOSE: Development/testing only
        └─ LEVEL: DEBUG+
        └─ SOURCES: All modules when DEBUG_MODE=true
        └─ SIZE: ~10MB (rotated at 10MB)
```

---

## Flow Diagram: How Logs Work

```
┌──────────────────────────────────────────────────────────────────┐
│                     Your Application Code                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Module Code:                                                      │
│  ┌────────────────────────────────────────────────────────┐       │
│  │ from ..logger_config_enhanced import LoggerManager     │       │
│  │ logger = LoggerManager.get_logger(__name__,            │       │
│  │                                   "document_ingestion")│       │
│  │                                                         │       │
│  │ logger.info("Processing file...")                      │       │
│  └────────────────────────────────────────────────────────┘       │
│              │                                                      │
│              ▼                                                      │
├──────────────────────────────────────────────────────────────────┤
│                     LoggerManager (Central Hub)                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  _get_logger(name, "document_ingestion")                          │
│       │                                                             │
│       ├─→ Check if logger exists in cache                         │
│       │   (if yes, return cached logger)                          │
│       │                                                             │
│       └─→ Create new logger with:                                 │
│           ├─ Console Handler (INFO+ to stdout)                    │
│           ├─ File Handler → components/document_ingestion.log     │
│           ├─ Error Handler → errors.log (ERROR+ only)             │
│           └─ Formatter with trace ID                              │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
              │                                                       │
              ▼                                                       │
┌──────────────────────────────────────────────────────────────────┐
│                      Log Output Destination                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  logs/components/document_ingestion.log                           │
│  ├─ 2024-01-14 10:05:23 | a1b2c3d4 | INFO | Processing file...  │
│  ├─ 2024-01-14 10:05:25 | a1b2c3d4 | INFO | Embedding done      │
│  ├─ 2024-01-14 10:05:26 | a1b2c3d4 | INFO | Index updated       │
│  └─ [file rotates at 10MB, keeps 5 backups]                      │
│                                                                    │
│  logs/errors.log                                                   │
│  ├─ 2024-01-14 10:06:10 | x7y8z9a0 | ERROR | Failed to parse PDF │
│  └─ [file rotates at 5MB, keeps 10 backups]                      │
│                                                                    │
│  logs/rag_system.log (backup, all levels)                         │
│  └─ [everything goes here too, for backup]                       │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Trace Flow Example

### Scenario: User asks a question

```
REQUEST START
│
├─ [API Layer]
│  └─ logger.info("Chat endpoint | Query: 'What is ML?'")
│     → logs/components/api_endpoints.log
│     └─ Trace ID: a1b2c3d4
│
├─ [RAG Engine]
│  ├─ logger.info("RAG pipeline started")
│  │  → logs/components/rag_engine.log
│  │
│  ├─ [Vector Store]
│  │  └─ logger.info("Searching vector store | Query dimension: 384")
│  │     → logs/components/vector_store.log
│  │     └─ Trace ID: a1b2c3d4 (same)
│  │
│  └─ [LLM Engine]
│     ├─ logger.info("LLM Query | Model: Groq | Tokens: ~100")
│     │  → logs/components/llm_queries.log
│     │  └─ Trace ID: a1b2c3d4 (same)
│     │
│     └─ logger.info("LLM Response | Tokens: 250 | Cost: $0.0042")
│        → logs/components/llm_queries.log
│        └─ Trace ID: a1b2c3d4 (same)
│
└─ [API Response]
   └─ logger.info("Chat endpoint success | Time: 2.5s")
      → logs/components/api_endpoints.log
      └─ Trace ID: a1b2c3d4 (same)

RETRIEVE FULL TRACE:
$ grep "a1b2c3d4" logs/components/*.log

OUTPUT:
=== api_endpoints.log ===
Chat endpoint | Query: 'What is ML?' | Trace: a1b2c3d4

=== rag_engine.log ===
RAG pipeline started | Trace: a1b2c3d4

=== vector_store.log ===
Searching vector store | Trace: a1b2c3d4

=== llm_queries.log ===
LLM Query | Model: Groq | Trace: a1b2c3d4
LLM Response | Tokens: 250 | Cost: $0.0042 | Trace: a1b2c3d4

=== api_endpoints.log ===
Chat endpoint success | Time: 2.5s | Trace: a1b2c3d4

Now you can see the ENTIRE journey across all components!
```

---

## Performance Monitoring Dashboard (Concept)

```
┌────────────────────────────────────────────────────────────────┐
│                  RAG SYSTEM HEALTH DASHBOARD                    │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  API Endpoints (last 1 hour)                                   │
│  ├─ Requests: 1,234                                            │
│  ├─ Avg latency: 2.5s                                          │
│  ├─ Error rate: 1.2%                                           │
│  └─ P95 latency: 5.2s                                          │
│                                                                  │
│  Document Ingestion (last 1 hour)                              │
│  ├─ Files processed: 45                                        │
│  ├─ Avg parse time: 1.2s                                       │
│  ├─ Failed: 2                                                  │
│  └─ Total chunks created: 12,340                               │
│                                                                  │
│  Vector Store (last 1 hour)                                    │
│  ├─ Searches: 1,234                                            │
│  ├─ Avg search latency: 45ms                                   │
│  ├─ Vectors in index: 450,000                                  │
│  └─ Index size: 2.3GB                                          │
│                                                                  │
│  LLM Queries (last 1 hour)                                     │
│  ├─ Queries: 300                                               │
│  ├─ Avg latency: 1.8s                                          │
│  ├─ Total cost: $12.45                                         │
│  ├─ Input tokens: 150,000                                      │
│  └─ Output tokens: 45,000                                      │
│                                                                  │
│  Errors (last 1 hour)                                          │
│  ├─ Total errors: 15                                           │
│  ├─ By component:                                              │
│  │  ├─ Document ingestion: 2                                   │
│  │  ├─ Vector store: 1                                         │
│  │  ├─ LLM queries: 12                                         │
│  │  └─ API endpoints: 0                                        │
│  └─ Most common error: "Rate limit exceeded"                   │
│                                                                  │
└────────────────────────────────────────────────────────────────┘

These metrics come from parsing the component-specific logs!
```

---

## Migration Timeline

```
DAY 1: Preparation (1-2 hours)
├─ Create log directories
├─ Deploy logger_config_enhanced.py
├─ Update config.py
└─ Test basic logging

DAY 2: High-Impact Modules (2-3 hours)
├─ Migrate document_service.py
├─ Migrate llm_engine.py
├─ Test both modules
└─ Update documentation

DAY 3: More Components (2-3 hours)
├─ Migrate vector_store.py
├─ Migrate api endpoints
└─ Add trace ID support

DAY 4: Remaining & Optimization (1-2 hours)
├─ Migrate frontend.app.py
├─ Migrate dataset_service.py
├─ Set up monitoring
└─ Archive old logs

RESULT: Professional modular logging system ✅
```

---

## Benefits Summary

```
BEFORE (Unified Logging)          AFTER (Modular Logging)
═══════════════════════════════   ═══════════════════════════════

Problem:                          Solution:
• 100MB+ single file              • 10-20MB per component
• Takes 10s to search             • Search in <1 second
• Hard to isolate issues          • Easy to find problems
• No performance insights         • Track metrics per module
• Mixed log levels                • Clean separation

Examples:

BEFORE (Hard):
$ grep -i "error\|fail" logs/rag_system.log | head -50
[Gets everything mixed together]

AFTER (Easy):
$ tail -20 logs/errors.log
[Only errors, instantly clear]

BEFORE (Slow):
$ grep "embedding\|token\|cost" logs/rag_system.log
[Takes 5-10 seconds, mixed with other logs]

AFTER (Fast):
$ tail -20 logs/components/llm_queries.log | grep cost
[Instant results, clean data]

BEFORE (Blind):
$ tail logs/rag_system.log
[Can't tell where the issue is]

AFTER (Informed):
$ cat logs/components/document_ingestion.log
[Know exactly which component is acting up]
```

---

## Implementation Checklist

```
SETUP
☐ Read LOGGING_BEST_PRACTICES.md
☐ Create log directories (mkdir -p logs/components logs/frontend)
☐ Copy logger_config_enhanced.py
☐ Update config.py

PHASE 1: CRITICAL MODULES (2-3 hours)
☐ Document service → document_ingestion.log
☐ LLM engine → llm_queries.log
☐ Vector store → vector_store.log
☐ Test each module individually

PHASE 2: API & SERVICES (2-3 hours)
☐ API endpoints → api_endpoints.log
☐ Chat service → api_endpoints.log
☐ Dataset service → dataset_service.log
☐ Add trace ID support

PHASE 3: REMAINING (1-2 hours)
☐ Frontend → streamlit_app.log
☐ RAG engine → rag_engine.log
☐ Observability → opik_tracing.log
☐ Test end-to-end

PHASE 4: OPTIMIZATION (1 hour)
☐ Set up log monitoring
☐ Archive old logs
☐ Document learnings
☐ Update team documentation

MAINTENANCE
☐ Weekly log review
☐ Monitor disk usage
☐ Archive old logs monthly
☐ Adjust rotation settings if needed
```

---

## Quick Command Reference

```bash
# Watch documents being processed
tail -f logs/components/document_ingestion.log

# Monitor LLM costs in real-time
tail -f logs/components/llm_queries.log | grep cost

# Check for errors
tail -50 logs/errors.log

# Trace a single request (replace a1b2c3d4 with actual trace ID)
grep "a1b2c3d4" logs/components/*.log

# Find slow operations
grep "Time: [5-9]" logs/components/llm_queries.log

# Monitor everything
tail -f logs/components/*.log logs/errors.log 2>/dev/null
```

---

This architecture transforms your logging from a debugging nightmare to a professional observability system! 🚀
