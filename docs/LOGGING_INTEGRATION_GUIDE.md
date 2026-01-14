# Day-Wise Logging Integration Guide

## Overview

This guide shows how to migrate existing modules to use the new **day-wise logging structure**. All logs are now centralized under `src/logs/` with automatic organization by date and component type.

### Directory Structure
```
src/logs/
├── backend/
│   ├── 2025-01-06/
│   │   ├── document_ingestion.log
│   │   ├── vector_store.log
│   │   ├── llm_queries.log
│   │   ├── api_endpoints.log
│   │   ├── rag_engine.log
│   │   ├── dataset.log
│   │   ├── opik_tracing.log
│   │   └── errors.log
│   ├── 2025-01-07/
│   │   ├── document_ingestion.log
│   │   └── ... (other logs)
│   └── current -> 2025-01-07/  (symlink for easy access)
├── frontend/
│   ├── 2025-01-06/
│   │   ├── app.log
│   │   ├── pages.log
│   │   ├── chat.log
│   │   ├── library.log
│   │   ├── upload.log
│   │   ├── settings.log
│   │   ├── api_client.log
│   │   └── errors.log
│   ├── 2025-01-07/
│   │   └── ... (other logs)
│   └── current -> 2025-01-07/  (symlink for easy access)
└── reports/
    └── daily_report_2025-01-07.json  (statistics)
```

---

## Backend Module Migration

### Before (Old Approach)
```python
import logging
from src.backend.logger_config import get_logger

# Using old unified logging
logger = get_logger(__name__)
logger.info("Processing document...")
```

### After (New Day-Wise Approach)

#### Option 1: Using Convenience Function (Recommended)
```python
from src.backend.logger_config_day_wise import get_backend_logger

# Document ingestion module
logger = get_backend_logger("document_ingestion")
logger.info("Processing document...")
logger.error("Failed to process document", exc_info=True)
```

#### Option 2: Using DayWiseLogger Directly
```python
from src.backend.logger_config_day_wise import DayWiseLogger

day_wise_logger = DayWiseLogger()
logger = day_wise_logger.get_logger(
    name="document_ingestion",
    log_type="document_ingestion",
    is_frontend=False
)
logger.info("Processing document...")
```

### Backend Log Types

| Log Type | File | Purpose |
|----------|------|---------|
| `document_ingestion` | document_ingestion.log | Document parsing, chunking, preprocessing |
| `vector_store` | vector_store.log | FAISS operations, embeddings, similarity search |
| `llm_queries` | llm_queries.log | LLM API calls, prompts, responses |
| `api_endpoints` | api_endpoints.log | FastAPI route operations, request/response |
| `rag_engine` | rag_engine.log | RAG pipeline orchestration |
| `dataset` | dataset.log | Dataset operations and management |
| `opik_tracing` | opik_tracing.log | OPIK monitoring and tracing |
| `errors` | errors.log | All ERROR/CRITICAL level logs (unified) |

---

## Frontend Module Migration

### Before (Old Approach)
```javascript
// Using console or basic logging
console.log("User uploaded file");
console.error("Upload failed");
```

### After (New Day-Wise Approach)

#### Using Python Logging (if Streamlit backend)
```python
from src.backend.logger_config_day_wise import get_frontend_logger

logger = get_frontend_logger("upload")
logger.info("File uploaded by user")
logger.error("Upload failed", exc_info=True)
```

### Frontend Log Types

| Log Type | File | Purpose |
|----------|------|---------|
| `app` | app.log | Main Streamlit app initialization |
| `pages` | pages.log | Page navigation and rendering |
| `chat` | chat.log | Chat interface interactions |
| `library` | library.log | Document library operations |
| `upload` | upload.log | File upload operations |
| `settings` | settings.log | User settings changes |
| `api_client` | api_client.log | API calls to backend |
| `errors` | errors.log | All ERROR/CRITICAL level logs (unified) |

---

## Configuration

### Environment Variables (.env)

```bash
# Base directory for all logs
BASE_LOG_DIR=src/logs

# Logging level
LOG_LEVEL=INFO

# Maximum size per log file (10MB)
LOG_MAX_BYTES=10485760

# Number of backup files to keep
LOG_BACKUP_COUNT=5

# Days to keep logs before archiving
LOG_RETENTION_DAYS=30

# Create convenient symlinks to current day
ENABLE_LOG_SYMLINKS=true
```

### Python Configuration (config.py)

```python
from src.backend.config import Settings

settings = Settings()

# Access logging settings
base_dir = settings.BASE_LOG_DIR          # "src/logs"
log_level = settings.LOG_LEVEL            # "INFO"
max_bytes = settings.LOG_MAX_BYTES        # 10485760
retention = settings.LOG_RETENTION_DAYS   # 30
use_symlinks = settings.ENABLE_LOG_SYMLINKS  # True
```

---

## Usage Examples

### Backend: Document Ingestion Module
```python
from src.backend.logger_config_day_wise import get_backend_logger

logger = get_backend_logger("document_ingestion")

def process_pdf(file_path):
    """Process a PDF file."""
    try:
        logger.info(f"Starting PDF processing: {file_path}")
        
        # Process logic
        chunks = pdf_to_chunks(file_path)
        logger.debug(f"Generated {len(chunks)} chunks")
        
        # More processing
        embeddings = create_embeddings(chunks)
        logger.info(f"Created {len(embeddings)} embeddings")
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Failed to process PDF {file_path}: {str(e)}", exc_info=True)
        raise
```

**Generated Log File**: `src/logs/backend/2025-01-07/document_ingestion.log`

### Backend: LLM Queries Module
```python
from src.backend.logger_config_day_wise import get_backend_logger

logger = get_backend_logger("llm_queries")

def generate_response(query, context):
    """Generate LLM response using Groq."""
    logger.info(f"Generating response for query: {query[:100]}...")
    logger.debug(f"Context chunks: {len(context)}")
    
    try:
        response = llm.generate(prompt=context + query)
        logger.info(f"Generated response: {len(response)} tokens")
        return response
    except Exception as e:
        logger.error(f"LLM generation failed: {str(e)}", exc_info=True)
        raise
```

**Generated Log File**: `src/logs/backend/2025-01-07/llm_queries.log`

### Backend: API Endpoints Module
```python
from fastapi import FastAPI
from src.backend.logger_config_day_wise import get_backend_logger

logger = get_backend_logger("api_endpoints")

@app.post("/api/search")
async def search(query: str):
    """Search API endpoint."""
    logger.info(f"Search request: {query}")
    
    try:
        results = perform_search(query)
        logger.info(f"Search completed: {len(results)} results")
        return {"results": results}
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        return {"error": str(e)}, 500
```

**Generated Log File**: `src/logs/backend/2025-01-07/api_endpoints.log`

### Backend: Error Aggregation
All ERROR and CRITICAL level logs are automatically aggregated:
```python
logger.error("Something went wrong")        # → errors.log
logger.critical("Critical system failure")   # → errors.log
logger.info("Normal operation")              # → document_ingestion.log (component specific)
```

**Generated Log File**: `src/logs/backend/2025-01-07/errors.log`

---

## Accessing Logs

### Using Symlinks (Easiest)

```bash
# View today's document ingestion logs
tail -f src/logs/backend/current/document_ingestion.log

# View today's errors
tail -f src/logs/backend/current/errors.log

# Search in current day's frontend logs
grep "error" src/logs/frontend/current/*.log
```

### Viewing Historical Logs

```bash
# List all backend log dates
ls -la src/logs/backend/

# View specific date
tail -f src/logs/backend/2025-01-06/llm_queries.log

# Search across all backend logs for a date
grep "pattern" src/logs/backend/2025-01-06/*.log
```

### Searching Logs

```bash
# Search in current logs
grep -r "error" src/logs/backend/current/

# Search with line numbers
grep -n "Failed" src/logs/backend/2025-01-07/api_endpoints.log

# Search case-insensitive
grep -i "timeout" src/logs/backend/current/*.log

# Use regex
grep -E "ERROR|CRITICAL" src/logs/backend/2025-01-07/errors.log
```

---

## Log Maintenance

### Automatic Daily Maintenance

The `scripts/daily_log_maintenance.py` script performs daily tasks:

1. **Update Symlinks**: Points `current/` to today's logs
2. **Archive Old Logs**: Compresses logs older than `LOG_RETENTION_DAYS` to tar.gz
3. **Generate Reports**: Creates daily statistics in `reports/`
4. **Cleanup Archives**: Removes very old compressed archives

### Setting Up Automatic Execution

#### Linux/Mac (Crontab)
```bash
# Edit crontab
crontab -e

# Add this line to run maintenance daily at 1 AM
0 1 * * * cd /path/to/RAG && python scripts/daily_log_maintenance.py
```

#### Windows (Task Scheduler)
```
Program: C:\Program Files\Python\python.exe
Arguments: C:\path\to\RAG\scripts\daily_log_maintenance.py
Schedule: Daily at 1:00 AM
```

### Manual Execution
```bash
# Run full maintenance
python scripts/daily_log_maintenance.py

# View maintenance logs
tail -f src/logs/backend/maintenance.log
```

---

## Log Statistics and Reports

### Programmatic Access
```python
from src.backend.log_manager import LogManager

manager = LogManager()

# Get statistics
stats = manager.get_log_stats()

print(f"Total Size: {stats['total_size_mb']} MB")
print(f"Total Files: {stats['total_files']}")
print(f"Error Logs: {stats['error_logs']}")
print(f"Categories: {stats['categories']}")

# Print formatted report
manager.print_log_report()
```

### Searching Logs Programmatically
```python
from src.backend.log_manager import LogManager

manager = LogManager()

# Search for specific pattern
results = manager.search_logs(
    pattern="timeout",
    category="backend",
    log_type="llm_queries"
)

for result in results:
    print(f"Found in {result['file']}: {result['matches']} matches")
```

### Daily Report JSON
Each day generates a JSON report with detailed statistics:

```json
{
  "timestamp": "2025-01-07T01:00:00",
  "total_size_mb": 245.3,
  "total_files": 89,
  "error_logs": 12,
  "categories": [
    "backend.document_ingestion",
    "backend.llm_queries",
    "frontend.chat"
  ],
  "backend": {
    "document_ingestion": {
      "size_mb": 45.2,
      "files": 8,
      "errors": 2
    },
    "llm_queries": {
      "size_mb": 123.5,
      "files": 15,
      "errors": 5
    }
  },
  "frontend": {
    "chat": {
      "size_mb": 76.6,
      "files": 66,
      "errors": 5
    }
  }
}
```

---

## Migration Checklist

- [ ] Update config.py with new logging settings (BASE_LOG_DIR, etc.)
- [ ] Update .env template with logging variables
- [ ] Create src/logs/ directory structure
- [ ] Update backend modules to use `get_backend_logger()`
- [ ] Update frontend modules to use `get_frontend_logger()`
- [ ] Test day-wise logging with sample runs
- [ ] Set up daily maintenance script in crontab/Task Scheduler
- [ ] Update developer documentation
- [ ] Train team on new logging system
- [ ] Monitor logs for first week of production

---

## Benefits

✅ **Better Organization**: Logs grouped by date and component  
✅ **Easy Archiving**: Compress old logs automatically  
✅ **Convenient Access**: Symlinks to current day logs  
✅ **Error Isolation**: All errors aggregated in errors.log  
✅ **Performance**: Smaller log files prevent slowdowns  
✅ **Compliance**: Automatic retention management  
✅ **Analytics**: Daily statistics and reports  
✅ **Searchability**: Targeted searches by date/component  

---

## Troubleshooting

### Logs Not Creating
```bash
# Check directory permissions
ls -la src/logs/

# Ensure directory exists
mkdir -p src/logs/backend src/logs/frontend
chmod 755 src/logs/
```

### Symlinks Not Working (Windows)
If symlinks don't work on Windows, disable with:
```bash
ENABLE_LOG_SYMLINKS=false
```

Then use full paths:
```bash
tail -f src/logs/backend/2025-01-07/document_ingestion.log
```

### Old Logs Not Archiving
```bash
# Check maintenance log
tail -f src/logs/backend/maintenance.log

# Manual archive
python -c "
from src.backend.log_manager import LogManager
manager = LogManager()
manager.archive_old_logs(category='backend', days=30)
print('Archive complete')
"
```

### High Disk Usage
```bash
# Get report
python -c "
from src.backend.log_manager import LogManager
LogManager().print_log_report()
"

# Reduce retention
# Set LOG_RETENTION_DAYS=14 in .env (shorter retention)
```

---

## Next Steps

1. **Implement**: Follow migration checklist above
2. **Monitor**: Check maintenance logs for first week
3. **Optimize**: Adjust LOG_RETENTION_DAYS based on disk usage
4. **Enhance**: Add Opik-based log analysis (see ENHANCED_OPIK_GUIDE.md)
5. **Dashboard**: Create Streamlit log viewer dashboard (optional)
