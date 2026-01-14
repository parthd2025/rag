# Logging Quick Reference

## 🎯 Module Categories

Use these when creating a logger:

| Module | Purpose | Log File |
|--------|---------|----------|
| `document_ingestion` | Upload, parse, chunk documents | `components/document_ingestion.log` |
| `vector_store` | FAISS indexing & retrieval | `components/vector_store.log` |
| `llm_queries` | LLM API calls & responses | `components/llm_queries.log` |
| `api_endpoints` | FastAPI HTTP endpoints | `components/api_endpoints.log` |
| `rag_engine` | RAG pipeline operations | `components/rag_engine.log` |
| `dataset` | Dataset management | `components/dataset_service.log` |
| `opik_tracing` | Observability & tracing | `components/opik_tracing.log` |
| `frontend` | Streamlit UI interactions | `frontend/streamlit_app.log` |
| `error` | All ERROR+ logs | `errors.log` |
| `debug` | Development debug logs | `debug/debug.log` |
| `general` | General application | `rag_system.log` |

---

## 📝 Code Patterns

### Create a Logger
```python
from ..logger_config_enhanced import LoggerManager

# For new code (recommended)
logger = LoggerManager.get_logger(__name__, "module_name")

# For quick access to common modules
from ..logger_config_enhanced import (
    get_document_logger,      # document_ingestion
    get_vector_store_logger,  # vector_store
    get_llm_logger,          # llm_queries
    get_api_logger,          # api_endpoints
    get_frontend_logger,     # frontend
)
```

### Log Information
```python
# Simple
logger.info("Something happened")

# With context
logger.info(f"Processing | File: {filename} | Size: {size}MB")

# With multiple fields
logger.info(
    f"Operation | "
    f"Module: document | "
    f"Status: success | "
    f"Time: 2.5s | "
    f"Count: 42"
)
```

### Log Warnings
```python
logger.warning(f"Unexpected condition | Value: {value} | Expected: {expected}")
```

### Log Errors
```python
# With traceback (shows full error)
logger.error("Operation failed", exc_info=True)

# With context
logger.error(f"Failed to process | File: {file} | Error: {e}", exc_info=True)
```

### Log with Timing
```python
import time

start = time.time()
# do work...
elapsed = time.time() - start

logger.info(f"Operation completed | Time: {elapsed:.2f}s | Speed: {count/elapsed:.1f}/sec")
```

---

## 🔍 Monitoring Commands

### Watch Logs in Real-Time
```bash
# Single component
tail -f logs/components/llm_queries.log

# Multiple components
tail -f logs/components/*.log logs/errors.log

# Specific pattern
tail -f logs/components/llm_queries.log | grep "completed"
```

### Search Historical Logs
```bash
# Find errors
grep ERROR logs/components/document_ingestion.log

# Find specific operation
grep "upload" logs/components/document_ingestion.log

# Count occurrences
grep -c "ERROR" logs/errors.log

# Show last 50 lines
tail -50 logs/errors.log

# Show lines around match (context)
grep -C 3 "failed" logs/components/llm_queries.log
```

### Analyze Logs
```bash
# Show all warnings
grep WARNING logs/components/*.log

# Find slow operations
grep "Time: [5-9]" logs/components/llm_queries.log

# Get unique errors
grep ERROR logs/errors.log | sort | uniq

# Count by level
for level in INFO WARNING ERROR; do
  echo "$level: $(grep -c $level logs/components/llm_queries.log)"
done
```

### Advanced Queries
```bash
# Find trace ID
grep "a1b2c3d4" logs/components/*.log

# Operations taking > 5 seconds
awk '/Time: [0-9]*\.[0-9]*s/ && $NF+0 > 5' logs/components/*.log

# Monitor in real-time with colors
tail -f logs/errors.log | grep --color=auto "ERROR\|WARNING\|$"

# Stream to file
tail -f logs/components/llm_queries.log >> analysis.log &
```

---

## ⚡ Common Scenarios

### Scenario 1: Debug Document Upload Issue
```bash
# 1. Check what went wrong
tail -50 logs/components/document_ingestion.log

# 2. Search for specific error
grep "PDF" logs/components/document_ingestion.log | grep ERROR

# 3. See full context
grep -B5 -A5 "failed" logs/components/document_ingestion.log

# 4. Check vector storage
tail -20 logs/components/vector_store.log
```

### Scenario 2: Monitor LLM Costs
```bash
# Watch costs in real-time
tail -f logs/components/llm_queries.log | grep "cost\|Cost"

# Calculate daily costs
grep "estimated cost" logs/components/llm_queries.log | awk -F'$' '{print $2}' | awk '{s+=$1} END {print s}'

# Find expensive queries
grep "Estimated cost" logs/components/llm_queries.log | sort -t'$' -k2 -n | tail -10
```

### Scenario 3: Trace User Request
```bash
# Get trace ID from current request
TRACE_ID="a1b2c3d4"

# Follow request through all components
echo "=== API Request ==="
grep $TRACE_ID logs/components/api_endpoints.log

echo "=== Document Retrieval ==="
grep $TRACE_ID logs/components/vector_store.log

echo "=== LLM Processing ==="
grep $TRACE_ID logs/components/llm_queries.log

echo "=== Full flow ==="
grep $TRACE_ID logs/components/*.log
```

### Scenario 4: Production Error Alert
```bash
# Check recent errors
tail -100 logs/errors.log

# Find error rate
echo "Errors per minute:"
tail -1000 logs/errors.log | awk '{print $1}' | uniq -c

# Most common errors
grep ERROR logs/errors.log | grep -oE '"([^"]*)"' | sort | uniq -c | sort -rn | head -10
```

---

## 🏗️ Directory Structure

Your logs directory after setup:
```
logs/
├── rag_system.log              # Main backup log (all levels)
├── errors.log                  # Unified error log (ERROR+ only)
│
├── components/                 # Component-specific logs
│   ├── document_ingestion.log
│   ├── vector_store.log
│   ├── llm_queries.log
│   ├── api_endpoints.log
│   ├── rag_engine.log
│   ├── dataset_service.log
│   └── opik_tracing.log
│
├── frontend/                   # Frontend logs
│   └── streamlit_app.log
│
└── debug/                      # Development logs
    └── debug.log               # DEBUG level (dev only)
```

---

## ✅ Checklist for Module Migration

When migrating a module to use new logging:

- [ ] Import `LoggerManager` (not old `logger`)
- [ ] Choose correct module name from table above
- [ ] Create logger: `logger = LoggerManager.get_logger(__name__, "module_name")`
- [ ] Add structured context to log messages
- [ ] Include timing for performance-critical operations
- [ ] Use `exc_info=True` for error logging
- [ ] Remove hardcoded log file paths
- [ ] Test: verify logs appear in correct file
- [ ] Test: check error level logs go to `errors.log`
- [ ] Update any config/docs that reference logging

---

## 🔧 Configuration

### In `config.py`
```python
# Logging Configuration
LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
LOG_FILE: str = Field("logs/rag_system.log", env="LOG_FILE")
LOG_MAX_BYTES: int = Field(10 * 1024 * 1024, env="LOG_MAX_BYTES")  # 10MB
LOG_BACKUP_COUNT: int = Field(5, env="LOG_BACKUP_COUNT")  # Keep 5 rotated files

# Component Logging
ENABLE_COMPONENT_LOGS: bool = Field(True, env="ENABLE_COMPONENT_LOGS")
DEBUG_MODE: bool = Field(False, env="DEBUG_MODE")  # Creates debug logs
```

### In `.env`
```env
LOG_LEVEL=INFO              # INFO, DEBUG, WARNING, ERROR, CRITICAL
LOG_FILE=logs/rag_system.log
LOG_MAX_BYTES=10485760      # 10MB per file
LOG_BACKUP_COUNT=5          # Keep 5 old files

ENABLE_COMPONENT_LOGS=true
DEBUG_MODE=false
```

---

## 📊 Log Levels Explained

| Level | When to Use | Example |
|-------|------------|---------|
| `DEBUG` | Detailed troubleshooting | Variable values, function entry/exit |
| `INFO` | Important events | "Process started", "Success" |
| `WARNING` | Unexpected but recoverable | "Config not found, using default" |
| `ERROR` | Error but app continues | "Failed to upload file, trying again" |
| `CRITICAL` | Error and app may stop | "Database connection failed" |

---

## 🎯 Best Practices

### ✅ Do
```python
# Good: Structured context
logger.info(f"Document processed | File: {filename} | Chunks: {chunk_count} | Time: {elapsed:.2f}s")

# Good: Include IDs for tracking
logger.info(f"Query executed | Query ID: {query_id} | User: {user_id}")

# Good: Use exc_info for errors
logger.error("Failed to save index", exc_info=True)

# Good: Timing for performance
logger.info(f"Embedding generated | Time: {elapsed*1000:.0f}ms")
```

### ❌ Don't
```python
# Bad: No context
logger.info("Done")

# Bad: Too verbose
logger.info(f"a={1}, b={2}, c={3}, d={4}, e={5}")

# Bad: Unclear variables
logger.info(f"Operation on {x} resulted in {y}")

# Bad: Logging without module prefix
logger.info("Error occurred")  # Which module?
```

---

## 🚀 Getting Started (5 Minutes)

1. **Create directories**
   ```bash
   mkdir -p logs/components logs/frontend logs/debug
   ```

2. **Start using in one module**
   ```python
   from ..logger_config_enhanced import LoggerManager
   logger = LoggerManager.get_logger(__name__, "llm_queries")
   logger.info("LLM call started")
   ```

3. **Watch logs**
   ```bash
   tail -f logs/components/llm_queries.log
   ```

4. **Done!** You're now using modular logging 🎉

---

## 📚 Learn More

- **Full Guide**: Read `LOGGING_BEST_PRACTICES.md`
- **Examples**: Read `LOGGING_MIGRATION_EXAMPLES.md`
- **Setup**: Run `python scripts/setup_enhanced_logging.py`
- **Official Docs**: https://docs.python.org/3/library/logging.html

---

## 💡 Pro Tips

1. **Use grep for quick search**
   ```bash
   grep "pattern" logs/components/*.log
   ```

2. **Color-code output**
   ```bash
   grep --color=auto "ERROR\|WARNING\|$" logs/components/*.log
   ```

3. **Watch multiple logs**
   ```bash
   tail -f logs/components/*.log | grep -E "ERROR|WARNING"
   ```

4. **Archive old logs**
   ```bash
   tar czf logs_backup_$(date +%Y%m%d).tar.gz logs/
   ```

5. **Set log level at runtime**
   ```python
   import logging
   logging.getLogger().setLevel(logging.DEBUG)  # More verbose
   ```

---

**Happy Logging! 📝**
