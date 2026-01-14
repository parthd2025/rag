# Day-Wise Logging - Quick Reference Card

## TL;DR - Copy-Paste Templates

### Backend Module
```python
from src.backend.logger_config_day_wise import get_backend_logger

# Available types: document_ingestion, vector_store, llm_queries, api_endpoints, rag_engine, dataset, opik_tracing
logger = get_backend_logger("document_ingestion")

logger.info("Starting processing")
logger.debug(f"Debug info: {data}")
logger.warning("This might fail")
logger.error("Failed to process", exc_info=True)
```

**Result**: Log file at `src/logs/backend/YYYY-MM-DD/document_ingestion.log`

---

### Frontend Module (Streamlit)
```python
from src.backend.logger_config_day_wise import get_frontend_logger

# Available types: app, pages, chat, library, upload, settings, api_client
logger = get_frontend_logger("chat")

logger.info("User sent message")
logger.error("API call failed", exc_info=True)
```

**Result**: Log file at `src/logs/frontend/YYYY-MM-DD/chat.log`

---

## Backend Log Types Cheat Sheet

| Type | File | Import | Use When |
|------|------|--------|----------|
| Document Ingestion | `document_ingestion.log` | `get_backend_logger("document_ingestion")` | Processing PDFs, DOCs, chunking |
| Vector Store | `vector_store.log` | `get_backend_logger("vector_store")` | FAISS operations, embeddings |
| LLM Queries | `llm_queries.log` | `get_backend_logger("llm_queries")` | Groq/LLM API calls |
| API Endpoints | `api_endpoints.log` | `get_backend_logger("api_endpoints")` | FastAPI routes, requests |
| RAG Engine | `rag_engine.log` | `get_backend_logger("rag_engine")` | RAG pipeline orchestration |
| Dataset | `dataset.log` | `get_backend_logger("dataset")` | Dataset operations |
| Opik Tracing | `opik_tracing.log` | `get_backend_logger("opik_tracing")` | Opik monitoring/tracing |

---

## Frontend Log Types Cheat Sheet

| Type | File | Import | Use When |
|------|------|--------|----------|
| App | `app.log` | `get_frontend_logger("app")` | Main Streamlit app events |
| Pages | `pages.log` | `get_frontend_logger("pages")` | Page navigation, rendering |
| Chat | `chat.log` | `get_frontend_logger("chat")` | Chat interface interactions |
| Library | `library.log` | `get_frontend_logger("library")` | Document library operations |
| Upload | `upload.log` | `get_frontend_logger("upload")` | File upload operations |
| Settings | `settings.log` | `get_frontend_logger("settings")` | User settings changes |
| API Client | `api_client.log` | `get_frontend_logger("api_client")` | Backend API calls |

---

## Viewing Logs

### Current Day Logs (Easiest)
```bash
# Tail document ingestion logs in real-time
tail -f src/logs/backend/current/document_ingestion.log

# Tail frontend chat logs
tail -f src/logs/frontend/current/chat.log

# View errors
tail -f src/logs/backend/current/errors.log
```

### Specific Date
```bash
# View yesterday's logs
tail src/logs/backend/2025-01-06/llm_queries.log

# Search in specific date
grep "error" src/logs/backend/2025-01-07/*.log
```

### Search Patterns
```bash
# Find all errors (current day)
grep -i "error" src/logs/backend/current/*.log

# Find timeout errors (specific file)
grep "timeout" src/logs/backend/current/api_endpoints.log

# Find with line numbers
grep -n "Failed" src/logs/backend/2025-01-07/document_ingestion.log

# Case-insensitive search
grep -i "warning" src/logs/backend/current/*.log
```

---

## Directory Structure at a Glance

```
src/logs/
├── backend/
│   ├── 2025-01-05/          ← Previous days
│   ├── 2025-01-06/
│   │   ├── document_ingestion.log
│   │   ├── vector_store.log
│   │   ├── llm_queries.log
│   │   ├── api_endpoints.log
│   │   ├── errors.log        ← All ERROR/CRITICAL
│   │   └── ...
│   ├── 2025-01-07/          ← Today's logs
│   ├── current/             ← Symlink to 2025-01-07/
│   └── maintenance.log      ← Daily maintenance runs
├── frontend/
│   ├── 2025-01-06/
│   ├── 2025-01-07/          ← Today
│   └── current/             ← Symlink to today
└── reports/
    └── daily_report_2025-01-07.json
```

---

## Logging Best Practices

### ✅ DO:
- Use appropriate log levels: DEBUG < INFO < WARNING < ERROR < CRITICAL
- Include context in error logs: `logger.error(f"Failed: {err}", exc_info=True)`
- Use debug for detailed tracing: `logger.debug(f"Variable: {value}")`
- Log start/end of major operations: `logger.info("Starting document processing")`

### ❌ DON'T:
- Log sensitive data (passwords, API keys)
- Use `print()` instead of logger
- Log too frequently in loops (causes file bloat)
- Ignore exceptions - use `exc_info=True` for stack traces

---

## Configuration (.env)

```bash
BASE_LOG_DIR=src/logs           # Where all logs go
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_MAX_BYTES=10485760          # 10MB file rotation
LOG_BACKUP_COUNT=5              # Keep 5 backups
LOG_RETENTION_DAYS=30           # Archive after 30 days
ENABLE_LOG_SYMLINKS=true        # Create symlinks to current/
```

---

## Maintenance

### Automatic (Daily at 1 AM)
Script `scripts/daily_log_maintenance.py` automatically:
- ✓ Updates symlinks to current day
- ✓ Archives logs older than 30 days
- ✓ Generates daily reports
- ✓ Cleans up old archives

### Manual Operations
```python
from src.backend.log_manager import LogManager

manager = LogManager()

# View statistics
manager.print_log_report()

# Search logs
results = manager.search_logs("timeout", category="backend")

# Get stats programmatically
stats = manager.get_log_stats()
print(f"Total: {stats['total_size_mb']} MB, {stats['total_files']} files")
```

---

## Common Scenarios

### Scenario 1: Debug Document Processing
```python
from src.backend.logger_config_day_wise import get_backend_logger

logger = get_backend_logger("document_ingestion")

def process_doc(path):
    logger.info(f"Processing: {path}")
    try:
        chunks = extract_chunks(path)
        logger.debug(f"Chunks: {len(chunks)}")
        return chunks
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        raise
```

Then view: `tail -f src/logs/backend/current/document_ingestion.log`

---

### Scenario 2: Monitor API Performance
```python
from src.backend.logger_config_day_wise import get_backend_logger
import time

logger = get_backend_logger("api_endpoints")

@app.post("/search")
async def search(query: str):
    start = time.time()
    logger.info(f"Search: {query}")
    
    try:
        results = search_engine.search(query)
        elapsed = time.time() - start
        logger.info(f"Search completed: {len(results)} results in {elapsed:.2f}s")
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise
```

Then search: `grep "completed" src/logs/backend/current/api_endpoints.log`

---

### Scenario 3: Find All Errors Across Components
```bash
# All errors today
grep -h "ERROR\|CRITICAL" src/logs/backend/current/*.log | sort

# Errors in specific date
grep -h "ERROR\|CRITICAL" src/logs/backend/2025-01-06/*.log

# Errors by component
grep "ERROR" src/logs/backend/2025-01-07/document_ingestion.log
grep "ERROR" src/logs/backend/2025-01-07/llm_queries.log
```

Or use unified errors log:
```bash
cat src/logs/backend/current/errors.log
tail -f src/logs/backend/current/errors.log
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Logs not appearing | Check `LOG_LEVEL=INFO` in .env, ensure logger initialized |
| Symlink not working (Windows) | Set `ENABLE_LOG_SYMLINKS=false`, use full paths |
| Files too large | Reduce `LOG_RETENTION_DAYS` or increase `LOG_MAX_BYTES` |
| Disk filling up | Check archived logs in `src/logs/backend/2025-*/` directories |
| Performance slow | Archive very old logs manually or reduce `LOG_BACKUP_COUNT` |

---

## One-Liners for Common Tasks

```bash
# Watch errors in real-time
tail -f src/logs/backend/current/errors.log

# Count errors today
wc -l src/logs/backend/current/errors.log

# List all log files
ls -la src/logs/backend/current/

# Search all backends today
grep "pattern" src/logs/backend/current/*.log

# Compare sizes
du -sh src/logs/backend/current/*.log

# Archive manually
python -c "from src.backend.log_manager import LogManager; LogManager().archive_old_logs('backend', 30)"

# Get daily report
python -c "from src.backend.log_manager import LogManager; LogManager().print_log_report()"
```

---

## Links & Documentation

- Full Guide: [LOGGING_INTEGRATION_GUIDE.md](LOGGING_INTEGRATION_GUIDE.md)
- Architecture: [LOGGING_DAY_WISE_STRUCTURE.md](LOGGING_DAY_WISE_STRUCTURE.md)
- Best Practices: [LOGGING_BEST_PRACTICES.md](LOGGING_BEST_PRACTICES.md)
- Index: [LOGGING_INDEX.md](LOGGING_INDEX.md)

---

*Last Updated: 2025-01-07 | For latest info see docs/LOGGING_* files*
