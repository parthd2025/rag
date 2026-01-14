# Enhanced Day-Wise Logging Structure

## 📁 Proposed Structure: All Logs Under One Roof

```
src/
├── logs/                              ← CENTRAL LOG REPOSITORY
│   ├── backend/
│   │   ├── 2026-01-14/               ← DATE FOLDERS
│   │   │   ├── document_ingestion.log
│   │   │   ├── vector_store.log
│   │   │   ├── llm_queries.log
│   │   │   ├── api_endpoints.log
│   │   │   ├── rag_engine.log
│   │   │   ├── dataset_service.log
│   │   │   ├── opik_tracing.log
│   │   │   └── errors.log
│   │   ├── 2026-01-13/
│   │   │   ├── document_ingestion.log  (previous day's logs)
│   │   │   ├── ...
│   │   │   └── errors.log
│   │   └── current/                   ← SYMLINK or CONVENIENCE FOLDER
│   │       ├── document_ingestion.log → ../2026-01-14/document_ingestion.log
│   │       ├── vector_store.log       → ../2026-01-14/vector_store.log
│   │       └── errors.log             → ../2026-01-14/errors.log
│   │
│   ├── frontend/
│   │   ├── 2026-01-14/               ← DATE FOLDERS
│   │   │   ├── app.log               ← Main app logs
│   │   │   ├── pages.log             ← Page-specific logs
│   │   │   ├── chat.log              ← Chat page logs
│   │   │   ├── library.log           ← Library page logs
│   │   │   ├── upload.log            ← Upload page logs
│   │   │   ├── settings.log          ← Settings page logs
│   │   │   └── errors.log            ← Frontend errors
│   │   ├── 2026-01-13/
│   │   │   ├── app.log
│   │   │   ├── ...
│   │   │   └── errors.log
│   │   └── current/                  ← SYMLINK or CONVENIENCE FOLDER
│   │       ├── app.log               → ../2026-01-14/app.log
│   │       ├── pages.log             → ../2026-01-14/pages.log
│   │       └── errors.log            → ../2026-01-14/errors.log
│   │
│   ├── archive/                      ← OLDER LOGS (30+ days old)
│   │   ├── logs_2026-01-01_to_2026-01-10.tar.gz
│   │   └── logs_2025-12-01_to_2025-12-31.tar.gz
│   │
│   └── README.md                     ← Log directory documentation
```

---

## 🗂️ Detailed Backend Log Structure

```
src/logs/backend/
├── 2026-01-14/                       ← TODAY'S LOGS
│   ├── document_ingestion.log        ← Document processing (INFO+)
│   ├── vector_store.log              ← FAISS operations (INFO+)
│   ├── llm_queries.log               ← LLM API calls with costs
│   ├── api_endpoints.log             ← HTTP requests/responses
│   ├── rag_engine.log                ← RAG pipeline operations
│   ├── dataset_service.log           ← Dataset management
│   ├── opik_tracing.log              ← Observability events
│   └── errors.log                    ← ALL ERROR/CRITICAL logs
│
├── 2026-01-13/                       ← YESTERDAY'S LOGS
│   ├── document_ingestion.log
│   ├── vector_store.log
│   ├── ...
│   └── errors.log
│
├── 2026-01-12/                       ← 2 DAYS AGO
│   └── [Same structure]
│
└── current/ OR latest/               ← SYMLINK TO TODAY (optional)
    ├── document_ingestion.log → ../2026-01-14/document_ingestion.log
    ├── vector_store.log       → ../2026-01-14/vector_store.log
    ├── llm_queries.log        → ../2026-01-14/llm_queries.log
    ├── api_endpoints.log      → ../2026-01-14/api_endpoints.log
    ├── rag_engine.log         → ../2026-01-14/rag_engine.log
    ├── dataset_service.log    → ../2026-01-14/dataset_service.log
    ├── opik_tracing.log       → ../2026-01-14/opik_tracing.log
    └── errors.log             → ../2026-01-14/errors.log
```

---

## 🎨 Detailed Frontend Log Structure

```
src/logs/frontend/
├── 2026-01-14/                       ← TODAY'S LOGS
│   ├── app.log                       ← Main Streamlit app logs
│   ├── pages.log                     ← Page navigation logs
│   ├── chat.log                      ← Chat page interactions
│   ├── library.log                   ← Document library page
│   ├── upload.log                    ← Document upload logs
│   ├── settings.log                  ← Settings page logs
│   ├── api_client.log                ← API communication logs
│   └── errors.log                    ← ALL frontend errors
│
├── 2026-01-13/                       ← YESTERDAY'S LOGS
│   ├── app.log
│   ├── pages.log
│   ├── chat.log
│   └── ...
│
└── current/                          ← CONVENIENCE SYMLINK
    ├── app.log → ../2026-01-14/app.log
    ├── pages.log → ../2026-01-14/pages.log
    ├── chat.log → ../2026-01-14/chat.log
    └── errors.log → ../2026-01-14/errors.log
```

---

## 🔧 Enhanced Logger Configuration

```python
# src/backend/logger_config_day_wise.py

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict

from .config import settings


class DayWiseLogger:
    """Logger that creates day-wise log files in centralized location."""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    # Log type to backend log file mapping
    BACKEND_LOG_TYPES = {
        "document_ingestion": "document_ingestion.log",
        "vector_store": "vector_store.log",
        "llm_queries": "llm_queries.log",
        "api_endpoints": "api_endpoints.log",
        "rag_engine": "rag_engine.log",
        "dataset": "dataset_service.log",
        "opik_tracing": "opik_tracing.log",
        "error": "errors.log",
    }
    
    # Log type to frontend log file mapping
    FRONTEND_LOG_TYPES = {
        "app": "app.log",
        "pages": "pages.log",
        "chat": "chat.log",
        "library": "library.log",
        "upload": "upload.log",
        "settings": "settings.log",
        "api_client": "api_client.log",
        "error": "errors.log",
    }
    
    @classmethod
    def get_logger(
        cls,
        name: str,
        log_type: str = "general",
        is_frontend: bool = False
    ) -> logging.Logger:
        """
        Get or create a day-wise logger.
        
        Args:
            name: Logger name (typically __name__)
            log_type: Type of logging (document_ingestion, llm_queries, etc.)
            is_frontend: True for frontend logs, False for backend
            
        Returns:
            Configured logger instance
            
        Examples:
            # Backend logging
            logger = DayWiseLogger.get_logger(__name__, "document_ingestion", False)
            
            # Frontend logging
            logger = DayWiseLogger.get_logger(__name__, "chat", True)
        """
        logger_key = f"{'fe' if is_frontend else 'be'}:{log_type}:{name}"
        
        if logger_key not in cls._loggers:
            logger = cls._setup_logger(name, log_type, is_frontend)
            cls._loggers[logger_key] = logger
        
        return cls._loggers[logger_key]
    
    @classmethod
    def _setup_logger(
        cls,
        name: str,
        log_type: str,
        is_frontend: bool
    ) -> logging.Logger:
        """Set up day-wise logger with proper handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        logger.handlers.clear()
        logger.propagate = False
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Day-wise file handler
        log_file = cls._get_log_file_path(log_type, is_frontend)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB per file
            backupCount=5,  # Keep 5 backups
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error handler (logs ERROR+ to errors.log)
        if log_type != "error":
            error_handler = cls._get_error_handler(is_frontend)
            logger.addHandler(error_handler)
        
        return logger
    
    @classmethod
    def _get_log_file_path(cls, log_type: str, is_frontend: bool) -> str:
        """Get day-wise log file path."""
        # Get base path: src/logs/
        base_logs_dir = Path(settings.BASE_LOG_DIR)  # Will define in config.py
        
        # Determine frontend or backend
        category = "frontend" if is_frontend else "backend"
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Build path
        log_dir = base_logs_dir / category / today
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get log file name
        log_types = cls.FRONTEND_LOG_TYPES if is_frontend else cls.BACKEND_LOG_TYPES
        log_filename = log_types.get(log_type, "general.log")
        
        return str(log_dir / log_filename)
    
    @classmethod
    def _get_error_handler(cls, is_frontend: bool):
        """Get handler for ERROR+ logs."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        category = "frontend" if is_frontend else "backend"
        today = datetime.now().strftime("%Y-%m-%d")
        
        error_log_path = base_logs_dir / category / today / "errors.log"
        error_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        error_handler = RotatingFileHandler(
            str(error_log_path),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10,  # Keep 10 error log backups
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        error_handler.setFormatter(formatter)
        error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)
        
        return error_handler
    
    @classmethod
    def create_symlinks(cls, is_frontend: bool = False) -> None:
        """Create symlinks from 'current' folder to today's logs."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        category = "frontend" if is_frontend else "backend"
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_dir = base_logs_dir / category / today
        current_dir = base_logs_dir / category / "current"
        
        # Remove old symlink if exists
        if current_dir.exists() and current_dir.is_symlink():
            current_dir.unlink()
        
        # Create new symlink (or just a folder on Windows if symlinks don't work)
        if not current_dir.exists():
            try:
                # Try creating symlink
                current_dir.symlink_to(today_dir)
            except (OSError, NotImplementedError):
                # Fallback: create actual directory with copies
                current_dir.mkdir(parents=True, exist_ok=True)


# Convenience functions
def get_backend_logger(log_type: str, name: str = None):
    """Get backend logger."""
    if name is None:
        name = log_type
    return DayWiseLogger.get_logger(name, log_type, is_frontend=False)


def get_frontend_logger(log_type: str, name: str = None):
    """Get frontend logger."""
    if name is None:
        name = log_type
    return DayWiseLogger.get_logger(name, log_type, is_frontend=True)


# Create default loggers
backend_logger = get_backend_logger("general")
frontend_logger = get_frontend_logger("app")
```

---

## ⚙️ Configuration Updates

Add to `src/backend/config.py`:

```python
# Centralized Logging Configuration
BASE_LOG_DIR: str = Field("src/logs", env="BASE_LOG_DIR")
LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
LOG_MAX_BYTES: int = Field(10 * 1024 * 1024, env="LOG_MAX_BYTES")  # 10MB
LOG_BACKUP_COUNT: int = Field(5, env="LOG_BACKUP_COUNT")
ENABLE_LOG_SYMLINKS: bool = Field(True, env="ENABLE_LOG_SYMLINKS")
LOG_RETENTION_DAYS: int = Field(30, env="LOG_RETENTION_DAYS")  # Archive after 30 days
```

Add to `.env`:

```env
# Centralized Logging
BASE_LOG_DIR=src/logs
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
ENABLE_LOG_SYMLINKS=true
LOG_RETENTION_DAYS=30
```

---

## 🧹 Automatic Log Rotation & Archiving

```python
# src/backend/log_manager.py

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import tarfile

from .config import settings
from .logger_config_day_wise import DayWiseLogger


class LogManager:
    """Manage log files - cleanup, archiving, etc."""
    
    @staticmethod
    def archive_old_logs(days: int = None) -> None:
        """Archive logs older than specified days."""
        if days is None:
            days = settings.LOG_RETENTION_DAYS
        
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for category in ["backend", "frontend"]:
            category_dir = base_logs_dir / category
            
            # Find old date folders
            for date_folder in category_dir.iterdir():
                if not date_folder.is_dir() or date_folder.name in ["current", "archive"]:
                    continue
                
                try:
                    folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d")
                    
                    if folder_date < cutoff_date:
                        # Archive this folder
                        LogManager._archive_folder(date_folder, category_dir)
                except ValueError:
                    # Skip if folder name is not a date
                    continue
    
    @staticmethod
    def _archive_folder(folder_path: Path, category_dir: Path) -> None:
        """Archive a folder to tar.gz."""
        archive_dir = category_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        # Create archive name with date range
        start_date = folder_path.name
        archive_name = f"{start_date}_logs.tar.gz"
        archive_path = archive_dir / archive_name
        
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(folder_path, arcname=folder_path.name)
            
            # Remove original folder
            shutil.rmtree(folder_path)
            print(f"Archived and removed: {folder_path}")
            
        except Exception as e:
            print(f"Error archiving {folder_path}: {e}")
    
    @staticmethod
    def cleanup_symlinks() -> None:
        """Update symlinks to point to today's logs."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        
        for category in ["backend", "frontend"]:
            DayWiseLogger.create_symlinks(is_frontend=(category == "frontend"))
    
    @staticmethod
    def get_log_stats() -> dict:
        """Get statistics about log directory."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        
        stats = {
            "backend": {
                "total_size_mb": 0,
                "total_files": 0,
                "total_days": 0,
                "error_count": 0,
            },
            "frontend": {
                "total_size_mb": 0,
                "total_files": 0,
                "total_days": 0,
                "error_count": 0,
            },
        }
        
        for category in ["backend", "frontend"]:
            category_dir = base_logs_dir / category
            
            if not category_dir.exists():
                continue
            
            # Count date folders and files
            for date_folder in category_dir.iterdir():
                if not date_folder.is_dir() or date_folder.name in ["current", "archive"]:
                    continue
                
                stats[category]["total_days"] += 1
                
                for log_file in date_folder.glob("*.log"):
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    stats[category]["total_size_mb"] += size_mb
                    stats[category]["total_files"] += 1
                    
                    # Count errors in error.log
                    if log_file.name == "errors.log":
                        with open(log_file, 'r') as f:
                            stats[category]["error_count"] += sum(1 for _ in f)
        
        return stats
    
    @staticmethod
    def print_log_report() -> None:
        """Print log directory report."""
        stats = LogManager.get_log_stats()
        
        print("\n" + "=" * 70)
        print("LOG DIRECTORY REPORT")
        print("=" * 70)
        
        for category in ["backend", "frontend"]:
            cat_stats = stats[category]
            print(f"\n{category.upper()}:")
            print(f"  Total size: {cat_stats['total_size_mb']:.2f}MB")
            print(f"  Total files: {cat_stats['total_files']}")
            print(f"  Total days: {cat_stats['total_days']}")
            print(f"  Total errors: {cat_stats['error_count']}")
        
        print("\n" + "=" * 70)
```

---

## 📊 Usage Examples

### Backend Module

```python
# src/backend/services/document_service.py

from ..logger_config_day_wise import get_backend_logger

logger = get_backend_logger("document_ingestion")

class DocumentService:
    def ingest_document(self, file_path: str):
        logger.info(f"Starting ingestion | File: {file_path}")
        
        try:
            # Process document
            logger.info(f"Document processed | Chunks: 42 | Time: 2.5s")
        except Exception as e:
            logger.error(f"Failed to ingest document", exc_info=True)
            raise
```

### Frontend Module

```python
# src/frontend/pages/chat.py

from backend.logger_config_day_wise import get_frontend_logger

logger = get_frontend_logger("chat")

def render_chat_page():
    logger.info("Chat page loaded")
    
    if st.button("Send"):
        logger.info("Chat button clicked")
        # Process chat...
        logger.info("Chat response received | Length: 250 chars")
```

---

## 🚀 Daily Maintenance Tasks

Create a script to run daily:

```python
# scripts/daily_log_maintenance.py

#!/usr/bin/env python3
"""Run daily log maintenance tasks."""

from src.backend.log_manager import LogManager
from src.backend.logger_config_day_wise import DayWiseLogger

def main():
    print("Running daily log maintenance...")
    
    # Update symlinks
    print("Updating symlinks...")
    DayWiseLogger.create_symlinks(is_frontend=False)
    DayWiseLogger.create_symlinks(is_frontend=True)
    
    # Archive old logs
    print("Archiving old logs...")
    LogManager.archive_old_logs()
    
    # Print report
    print("Generating report...")
    LogManager.print_log_report()
    
    print("✅ Daily maintenance complete!")


if __name__ == "__main__":
    main()
```

Schedule with:
```bash
# Linux/Mac: crontab -e
0 2 * * * cd /path/to/RAG && python scripts/daily_log_maintenance.py

# Windows: Task Scheduler
# Run daily at 2 AM: python scripts/daily_log_maintenance.py
```

---

## 📈 Benefits of Day-Wise Structure

| Benefit | Why |
|---------|-----|
| ✅ **Easy to find** | Each day has own folder, easy to locate specific date |
| ✅ **Better organization** | Frontend/Backend separated clearly |
| ✅ **Easy archiving** | Old folders can be zipped and removed |
| ✅ **Performance** | Smaller files load faster |
| ✅ **Disk management** | Can delete old date folders easily |
| ✅ **Debugging** | Jump to specific date immediately |
| ✅ **Monitoring** | Easy to set up log watchers per day |
| ✅ **Compliance** | Can implement retention policies |

---

## 🔍 Monitoring Examples

### Today's Backend Logs
```bash
# Watch today's LLM queries
tail -f src/logs/backend/$(date +%Y-%m-%d)/llm_queries.log

# Watch today's errors
tail -f src/logs/backend/$(date +%Y-%m-%d)/errors.log

# Watch all today's backend logs
tail -f src/logs/backend/$(date +%Y-%m-%d)/*.log
```

### Frontend Logs
```bash
# Watch today's chat page
tail -f src/logs/frontend/$(date +%Y-%m-%d)/chat.log

# Watch all frontend errors
tail -f src/logs/frontend/$(date +%Y-%m-%d)/errors.log
```

### Quick Access with Symlinks
```bash
# Same as above but simpler:
tail -f src/logs/backend/current/llm_queries.log
tail -f src/logs/frontend/current/chat.log
```

### Historical Search
```bash
# Search across multiple days
grep "ERROR" src/logs/backend/2026-01-*/errors.log | head -20

# Find slow operations on specific day
grep "Time: [5-9]\." src/logs/backend/2026-01-14/llm_queries.log
```

---

## 💡 Suggestions for Further Improvements

### 1. **Hourly Log Rotation** (if daily is too coarse)
```python
# Add hourly subfolders within each day
src/logs/backend/2026-01-14/
├── 00/  (midnight to 1 AM)
│   ├── llm_queries.log
│   └── ...
├── 01/  (1 AM to 2 AM)
│   └── ...
└── 23/  (11 PM to midnight)
```

### 2. **Automatic Log Cleanup**
```python
# Delete logs older than 30 days automatically
LogManager.cleanup_old_logs(days=30, delete_not_archive=False)
```

### 3. **Real-Time Monitoring Dashboard**
```python
# Create a monitoring app
streamlit run scripts/log_monitor.py
# Shows live log metrics, errors, performance
```

### 4. **Log Aggregation Integration**
```python
# Send logs to ELK Stack, Datadog, or Loki
# Automatically index by day, component, level
```

### 5. **Error Alerting**
```python
# Send email/Slack alerts for errors
LogManager.setup_error_alerts(
    email="team@example.com",
    threshold=5  # Alert after 5 errors
)
```

### 6. **Performance Metrics Extraction**
```python
# Extract metrics from logs
metrics = LogManager.extract_metrics(
    date="2026-01-14",
    metric_type="performance"
)
# Returns: avg latency, throughput, P95 response time, etc.
```

### 7. **Log Compression**
```python
# Compress logs older than 7 days
LogManager.compress_old_logs(days=7)
# Saves 80-90% disk space
```

### 8. **Multi-Level Archiving**
```
src/logs/backend/
├── current_month/        (< 7 days - hot)
├── previous_months/      (7-30 days - warm)
└── archive/              (> 30 days - cold, compressed)
```

---

## ✅ Implementation Checklist

- [ ] Create `logger_config_day_wise.py` with DayWiseLogger class
- [ ] Update `config.py` with BASE_LOG_DIR setting
- [ ] Create `log_manager.py` with archiving/cleanup
- [ ] Update `.env` with logging configuration
- [ ] Create symlinks structure
- [ ] Test backend logging
- [ ] Test frontend logging
- [ ] Set up daily maintenance script
- [ ] Schedule daily maintenance task
- [ ] Document log access for team
- [ ] Set up monitoring dashboard (optional)
- [ ] Implement error alerting (optional)

---

## 📚 File Structure Summary

```
src/
├── logs/                          ← ALL LOGS HERE (centralized)
│   ├── backend/
│   │   ├── 2026-01-14/           ← Day folders
│   │   ├── 2026-01-13/
│   │   ├── archive/              ← Old compressed logs
│   │   └── current/              ← Symlink to today
│   │
│   └── frontend/
│       ├── 2026-01-14/           ← Day folders
│       ├── 2026-01-13/
│       ├── archive/              ← Old compressed logs
│       └── current/              ← Symlink to today
│
├── backend/
│   ├── logger_config_day_wise.py ← NEW (day-wise logging)
│   ├── log_manager.py            ← NEW (maintenance)
│   └── config.py                 ← UPDATED (BASE_LOG_DIR)
│
├── frontend/
│   └── [pages]
│       └── [use get_frontend_logger()]
│
└── scripts/
    └── daily_log_maintenance.py  ← NEW (daily tasks)
```

This structure is **clear, organized, scalable, and professional!** 🚀
