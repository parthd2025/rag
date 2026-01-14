"""
Day-Wise Logger Configuration

Organizes logs by:
1. Component (backend/frontend)
2. Date (YYYY-MM-DD folders)
3. Type (document_ingestion, llm_queries, errors, etc.)

All logs centralized in: src/logs/
"""

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
    
    # Backend log file mapping
    BACKEND_LOG_TYPES = {
        "document_ingestion": "document_ingestion.log",
        "vector_store": "vector_store.log",
        "llm_queries": "llm_queries.log",
        "api_endpoints": "api_endpoints.log",
        "rag_engine": "rag_engine.log",
        "dataset": "dataset_service.log",
        "opik_tracing": "opik_tracing.log",
        "general": "general.log",
        "error": "errors.log",
    }
    
    # Frontend log file mapping
    FRONTEND_LOG_TYPES = {
        "app": "app.log",
        "pages": "pages.log",
        "chat": "chat.log",
        "library": "library.log",
        "upload": "upload.log",
        "settings": "settings.log",
        "api_client": "api_client.log",
        "general": "general.log",
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
            log_type: Type of logging
            is_frontend: True for frontend, False for backend
            
        Returns:
            Configured logger instance
            
        Examples:
            # Backend
            logger = DayWiseLogger.get_logger(__name__, "document_ingestion", False)
            
            # Frontend
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
        
        # Console handler (INFO+ only)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Day-wise file handler
        log_file = cls._get_log_file_path(log_type, is_frontend)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error handler (ERROR+ to errors.log)
        if log_type != "error":
            error_handler = cls._get_error_handler(is_frontend)
            logger.addHandler(error_handler)
        
        return logger
    
    @classmethod
    def _get_log_file_path(cls, log_type: str, is_frontend: bool) -> str:
        """Get day-wise log file path."""
        # Get base path: src/logs/
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        
        # Determine category
        category = "frontend" if is_frontend else "backend"
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Build directory
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
            backupCount=10,
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
        """Create symlinks from 'current' to today's logs."""
        base_logs_dir = Path(settings.BASE_LOG_DIR)
        category = "frontend" if is_frontend else "backend"
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_dir = base_logs_dir / category / today
        current_dir = base_logs_dir / category / "current"
        
        if today_dir.exists() and not current_dir.exists():
            try:
                # Try creating symlink
                current_dir.symlink_to(today_dir)
            except (OSError, NotImplementedError):
                # Fallback: create directory on Windows
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
