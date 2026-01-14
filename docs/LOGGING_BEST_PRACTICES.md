# Logging Best Practices for RAG System

## Current Issues

Your current logging setup writes everything to a **unified file** (`logs/rag_system.log`), which creates several challenges:

- 🔍 **Hard to track specific issues** (can't isolate document ingestion vs. query errors)
- 📊 **Performance monitoring difficult** (queries/embeddings mixed with other logs)
- 🐛 **Debugging complex flows** (multi-component traces are scattered)
- ⚠️ **Alert management** (can't filter critical errors by component)
- 📈 **Analysis overhead** (searching huge log file for specific issues)

---

## Recommended Architecture: Structured Logging by Module

### 1. **Separate Logs by Component/Module**

Create distinct log files for each major functional area:

```
logs/
├── rag_system.log          # Main application log (INFO level)
├── components/
│   ├── document_ingestion.log    # Document processing, chunking, embedding
│   ├── vector_store.log          # FAISS operations, indexing, retrieval
│   ├── llm_queries.log           # LLM calls, tokens, latency
│   ├── api_endpoints.log         # HTTP requests/responses
│   ├── opik_tracing.log          # Observability/tracing events
│   └── errors.log                # All ERROR and CRITICAL level logs
├── frontend/
│   └── streamlit_app.log         # Frontend interactions
└── debug/
    └── debug.log                 # DEBUG level logs (development only)
```

### 2. **Key Benefits**

| Benefit | Implementation |
|---------|-----------------|
| **Targeted Debugging** | Search `document_ingestion.log` for upload issues only |
| **Performance Tracking** | Monitor `llm_queries.log` for latency and costs |
| **Error Alerting** | Watch `errors.log` for critical issues |
| **Flow Tracing** | Use trace IDs across multiple logs to follow a request |
| **Log Rotation** | Each log rotates independently without bloating others |
| **Easy Analysis** | Smaller files load faster in tools/IDEs |

---

## Implementation Strategy

### Step 1: Enhanced Logger Configuration

```python
# src/backend/logger_config.py (UPDATED)

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict

from .config import settings


class LoggerManager:
    """Centralized logger management with module-specific logs."""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def get_logger(cls, name: str, module: str = "general") -> logging.Logger:
        """
        Get or create a logger for a specific module.
        
        Args:
            name: Logger name (typically __name__)
            module: Module category (document_ingestion, vector_store, llm_queries, etc.)
            
        Returns:
            Configured logger instance
            
        Examples:
            # In document ingestion code
            logger = LoggerManager.get_logger(__name__, "document_ingestion")
            
            # In LLM code
            logger = LoggerManager.get_logger(__name__, "llm_queries")
        """
        logger_key = f"{module}:{name}"
        
        if logger_key not in cls._loggers:
            logger = cls._setup_module_logger(name, module)
            cls._loggers[logger_key] = logger
        
        return cls._loggers[logger_key]
    
    @staticmethod
    def _setup_module_logger(name: str, module: str) -> logging.Logger:
        """Set up logger with module-specific file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        logger.handlers.clear()
        
        # Enhanced formatter with more context
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (INFO+ only)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Module-specific file handler
        log_file = cls._get_log_file_path(module)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def _get_log_file_path(module: str) -> str:
        """Get module-specific log file path."""
        base_logs_dir = Path(settings.LOG_FILE).parent
        
        module_paths = {
            "document_ingestion": base_logs_dir / "components" / "document_ingestion.log",
            "vector_store": base_logs_dir / "components" / "vector_store.log",
            "llm_queries": base_logs_dir / "components" / "llm_queries.log",
            "api_endpoints": base_logs_dir / "components" / "api_endpoints.log",
            "opik_tracing": base_logs_dir / "components" / "opik_tracing.log",
            "frontend": base_logs_dir / "frontend" / "streamlit_app.log",
            "error": base_logs_dir / "errors.log",
            "debug": base_logs_dir / "debug" / "debug.log",
        }
        
        log_file = module_paths.get(module, base_logs_dir / "rag_system.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        return str(log_file)


# Backward compatibility
def setup_logger(name: str = "rag_system", log_file: Optional[str] = None) -> logging.Logger:
    """Legacy setup_logger for backward compatibility."""
    return LoggerManager.get_logger(name, "general")


# Default logger
logger = LoggerManager.get_logger("rag_system", "general")
```

### Step 2: Update Component Usage

**Document Ingestion Service:**
```python
# src/backend/services/document_service.py

from ..logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__, "document_ingestion")

class DocumentService:
    def ingest_document(self, file_path: str):
        logger.info(f"Starting document ingestion: {file_path}")
        try:
            # Document processing logic
            logger.info(f"Successfully ingested document: {file_path}")
        except Exception as e:
            logger.error(f"Failed to ingest document: {file_path}", exc_info=True)
```

**Vector Store Operations:**
```python
# src/backend/vector_store.py

from .logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__, "vector_store")

class FAISSVectorStore:
    def add_documents(self, docs: List[Document]):
        logger.info(f"Adding {len(docs)} documents to vector store")
        start_time = time.time()
        
        try:
            # Vector store logic
            elapsed = time.time() - start_time
            logger.info(f"Added documents in {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"Failed to add documents", exc_info=True)
```

**LLM Query Tracking:**
```python
# src/backend/llm_engine.py

from .logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__, "llm_queries")

class GroqLLMEngine:
    async def generate(self, prompt: str, **kwargs):
        logger.info(f"LLM Query | Model: {self.model} | Tokens: ~{len(prompt.split())}")
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(...)
            latency = time.time() - start_time
            logger.info(
                f"LLM Response | "
                f"Latency: {latency:.2f}s | "
                f"Tokens: {response.usage.total_tokens} | "
                f"Cost: ${self._estimate_cost(response.usage):.4f}"
            )
            return response
        except Exception as e:
            logger.error(f"LLM generation failed", exc_info=True)
            raise
```

**API Endpoints:**
```python
# src/backend/main.py

from .logger_config import LoggerManager

api_logger = LoggerManager.get_logger("api_endpoints", "api_endpoints")

@app.post("/chat")
async def chat(req: QueryRequest):
    api_logger.info(f"Chat endpoint called | Query: {req.query[:50]}...")
    
    try:
        response = await enhanced_chat_service.process_query(req)
        api_logger.info(f"Chat endpoint success | Response tokens: {len(response.answer.split())}")
        return response
    except Exception as e:
        api_logger.error(f"Chat endpoint failed", exc_info=True)
        raise
```

### Step 3: Structured Logging with Context

Use trace IDs to correlate logs across modules:

```python
# src/backend/context.py (NEW FILE)

import contextvars
import uuid
from typing import Optional

# Context variable for trace ID
_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id')

class LogContext:
    """Manage logging context for distributed tracing."""
    
    @staticmethod
    def get_trace_id() -> str:
        """Get current trace ID or create new one."""
        try:
            return _trace_id.get()
        except LookupError:
            trace_id = str(uuid.uuid4())[:8]
            _trace_id.set(trace_id)
            return trace_id
    
    @staticmethod
    def set_trace_id(trace_id: str) -> None:
        """Set trace ID for current request."""
        _trace_id.set(trace_id)
    
    @staticmethod
    def clear_trace_id() -> None:
        """Clear trace ID."""
        _trace_id.set("")


# Enhanced formatter with trace ID
class TraceIDFormatter(logging.Formatter):
    """Logging formatter that includes trace ID."""
    
    def format(self, record):
        trace_id = LogContext.get_trace_id()
        record.trace_id = trace_id
        return super().format(record)
```

Then in handlers:
```python
formatter = logging.Formatter(
    '%(asctime)s | %(trace_id)s | %(levelname)-8s | %(name)s | %(message)s'
)
```

### Step 4: Error Aggregation

Create a unified error log that captures all errors:

```python
# src/backend/logger_config.py (ADDITION)

class ErrorLogHandler(logging.Handler):
    """Custom handler that routes ERROR and CRITICAL logs to error.log."""
    
    def __init__(self, log_file: str):
        super().__init__()
        self.handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10,  # Keep more backups for errors
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        self.handler.setFormatter(formatter)
    
    def emit(self, record):
        """Only log ERROR and CRITICAL."""
        if record.levelno >= logging.ERROR:
            self.handler.emit(record)
```

---

## Configuration Changes Required

### Update `config.py`:

```python
# Logging Configuration
LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
LOG_FILE: str = Field("logs/rag_system.log", env="LOG_FILE")
LOG_MAX_BYTES: int = Field(10 * 1024 * 1024, env="LOG_MAX_BYTES")  # 10MB
LOG_BACKUP_COUNT: int = Field(5, env="LOG_BACKUP_COUNT")

# Component-specific logging (new)
ENABLE_COMPONENT_LOGS: bool = Field(True, env="ENABLE_COMPONENT_LOGS")
DEBUG_MODE: bool = Field(False, env="DEBUG_MODE")  # Creates logs/debug/ logs
```

### Update `.env` template:

```env
# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/rag_system.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Component Logging
ENABLE_COMPONENT_LOGS=true
DEBUG_MODE=false
```

---

## Usage Examples by Scenario

### Scenario 1: Debugging Document Upload Issues

```bash
# Only look at document ingestion logs
tail -f logs/components/document_ingestion.log

# Search for specific errors
grep "ERROR" logs/components/document_ingestion.log | head -20

# Find logs for a specific file
grep "sample.pdf" logs/components/document_ingestion.log
```

### Scenario 2: Monitoring LLM Performance

```bash
# Check response times and costs
tail -f logs/components/llm_queries.log

# Analyze latency over time
grep "LLM Response" logs/components/llm_queries.log | awk -F'|' '{print $4}' > latency.txt
```

### Scenario 3: Tracking a Single Request

```bash
# Use trace ID (e.g., "a1b2c3d4")
grep "a1b2c3d4" logs/components/*.log

# Shows journey: API endpoint → document retrieval → LLM call
```

### Scenario 4: Critical Production Issues

```bash
# Check unified error log
tail -50 logs/errors.log

# Find specific component error
grep "vector_store\|ERROR" logs/errors.log
```

---

## Migration Path

### Phase 1: Add New Logger (Backward Compatible)
- ✅ Keep existing `setup_logger()`
- ✅ Add `LoggerManager.get_logger()`
- ✅ Update one module at a time

### Phase 2: Migrate High-Volume Modules
- Document ingestion → `document_ingestion.log`
- LLM queries → `llm_queries.log`
- Vector store → `vector_store.log`

### Phase 3: Add Trace IDs
- Implement `LogContext` in middleware
- Pass through request lifecycle
- Track distributed flows

### Phase 4: Monitor & Optimize
- Analyze log file sizes
- Adjust rotation settings
- Set up log aggregation tools (optional)

---

## Advanced: Log Aggregation & Analysis

For production deployments, consider:

### Option A: **ELK Stack (Elasticsearch, Logstash, Kibana)**
```bash
# Parse logs and send to Elasticsearch
# Create dashboards for real-time monitoring
```

### Option B: **Grafana Loki**
```bash
# Lightweight log aggregation
# Works well with Docker/Kubernetes
```

### Option C: **Datadog/New Relic**
```bash
# Cloud-based centralized logging
# Integrated alerting and analysis
```

### Option D: **Simple Log Rotation + Archiving**
```bash
# Keep it simple for now
# Archive old logs weekly
# Use grep/awk for analysis
```

---

## Quick Reference: Log File Purposes

| File | Purpose | Rotation | Debug |
|------|---------|----------|-------|
| `rag_system.log` | Main app events | 10MB/5 backups | INFO+ |
| `document_ingestion.log` | Upload, parsing, chunking | 10MB/5 backups | DEBUG |
| `vector_store.log` | FAISS indexing, retrieval | 10MB/5 backups | DEBUG |
| `llm_queries.log` | Model calls, latency, costs | 10MB/5 backups | INFO+ |
| `api_endpoints.log` | HTTP requests/responses | 10MB/5 backups | INFO+ |
| `opik_tracing.log` | Observability events | 10MB/5 backups | DEBUG |
| `errors.log` | All ERROR/CRITICAL | 5MB/10 backups | ERROR+ |
| `debug.log` | Development only | 10MB/3 backups | DEBUG |

---

## Summary

✅ **Implement modular logging** - One log per functional area  
✅ **Use trace IDs** - Track requests across components  
✅ **Separate error handling** - Unified error log for alerting  
✅ **Maintain rotation** - Prevent disk space issues  
✅ **Add structured context** - Include timestamps, function names, line numbers  
✅ **Backward compatible** - Migrate gradually  

This approach makes it **easy to find, track, and debug issues** while maintaining clean log files!
