"""
Enhanced logging configuration for RAG system with module-specific logs.

This module provides:
- Modular logging by component (document_ingestion, vector_store, llm_queries, etc.)
- Trace ID support for distributed tracing
- Structured error logging
- Backward compatibility with existing setup_logger()
"""

import logging
import sys
import contextvars
import uuid
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict

from .config import settings


# Context variable for trace ID (used for distributed tracing)
_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id', default='')


class LogContext:
    """Manage logging context for distributed tracing across modules."""
    
    @staticmethod
    def get_trace_id() -> str:
        """Get current trace ID or generate new one."""
        trace_id = _trace_id.get()
        if not trace_id:
            trace_id = str(uuid.uuid4())[:8]
            _trace_id.set(trace_id)
        return trace_id
    
    @staticmethod
    def set_trace_id(trace_id: str) -> None:
        """Set trace ID for current context."""
        _trace_id.set(trace_id)
    
    @staticmethod
    def clear_trace_id() -> None:
        """Clear trace ID."""
        _trace_id.set('')


class TraceIDFormatter(logging.Formatter):
    """Logging formatter that includes trace ID for distributed tracing."""
    
    def format(self, record):
        trace_id = LogContext.get_trace_id()
        record.trace_id = trace_id if trace_id else 'N/A'
        return super().format(record)


class LoggerManager:
    """
    Centralized logger management with module-specific logs.
    
    Example usage:
        # In document_service.py
        logger = LoggerManager.get_logger(__name__, "document_ingestion")
        logger.info("Processing document...")
        
        # In llm_engine.py
        logger = LoggerManager.get_logger(__name__, "llm_queries")
        logger.info("Calling LLM API...")
        
        # In vector_store.py
        logger = LoggerManager.get_logger(__name__, "vector_store")
        logger.info("Adding to index...")
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    _formatters: Dict[str, str] = {
        "verbose": '%(asctime)s | %(trace_id)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        "standard": '%(asctime)s | %(trace_id)s | %(levelname)-8s | %(name)s | %(message)s',
        "simple": '%(levelname)-8s | %(name)s | %(message)s',
    }
    
    _module_paths: Dict[str, str] = {
        "document_ingestion": "components/document_ingestion.log",
        "vector_store": "components/vector_store.log",
        "llm_queries": "components/llm_queries.log",
        "api_endpoints": "components/api_endpoints.log",
        "opik_tracing": "components/opik_tracing.log",
        "rag_engine": "components/rag_engine.log",
        "frontend": "frontend/streamlit_app.log",
        "dataset": "components/dataset_service.log",
        "error": "errors.log",
        "debug": "debug/debug.log",
        "general": "rag_system.log",
    }
    
    @classmethod
    def get_logger(cls, name: str, module: str = "general") -> logging.Logger:
        """
        Get or create a logger for a specific module.
        
        Args:
            name: Logger name (typically __name__)
            module: Module category - one of:
                - document_ingestion: Document processing, chunking
                - vector_store: FAISS indexing and retrieval
                - llm_queries: LLM API calls and responses
                - api_endpoints: FastAPI endpoints
                - opik_tracing: Observability events
                - rag_engine: RAG pipeline operations
                - frontend: Streamlit frontend
                - dataset: Dataset management
                - error: Unified error log
                - debug: Development debug logs
                - general: General application logs (default)
        
        Returns:
            Configured logger instance
        """
        logger_key = f"{module}:{name}"
        
        if logger_key not in cls._loggers:
            logger = cls._setup_module_logger(name, module)
            cls._loggers[logger_key] = logger
        
        return cls._loggers[logger_key]
    
    @classmethod
    def _setup_module_logger(cls, name: str, module: str) -> logging.Logger:
        """Set up logger with module-specific file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        logger.propagate = False
        
        # Determine formatter style
        formatter_style = 'verbose' if settings.LOG_LEVEL.upper() == 'DEBUG' else 'standard'
        formatter_string = cls._formatters[formatter_style]
        formatter = TraceIDFormatter(
            formatter_string,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (INFO+ only for cleaner output)
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
        
        # Add error handler for all ERROR+ logs to go to errors.log
        if module != "error":  # Avoid recursion
            error_handler = cls._get_error_handler()
            logger.addHandler(error_handler)
        
        return logger
    
    @classmethod
    def _get_log_file_path(cls, module: str) -> str:
        """Get module-specific log file path."""
        base_logs_dir = Path(settings.LOG_FILE).parent
        
        # Get module-specific path or default
        relative_path = cls._module_paths.get(module, "rag_system.log")
        log_file = base_logs_dir / relative_path
        
        # Create parent directories if they don't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        return str(log_file)
    
    @classmethod
    def _get_error_handler(cls):
        """Get a handler that captures ERROR+ logs to errors.log."""
        error_log_file = cls._get_log_file_path("error")
        
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB - smaller to keep frequently accessed
            backupCount=10,  # More backups for error logs
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        formatter = TraceIDFormatter(
            '%(asctime)s | %(trace_id)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(formatter)
        error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)
        
        return error_handler
    
    @classmethod
    def list_available_modules(cls) -> Dict[str, str]:
        """List all available module categories and their log files."""
        return cls._module_paths.copy()


def setup_logger(name: str = "rag_system", log_file: Optional[str] = None) -> logging.Logger:
    """
    Legacy setup_logger function for backward compatibility.
    
    New code should use LoggerManager.get_logger() instead:
        logger = LoggerManager.get_logger(__name__, "module_name")
    """
    if log_file:
        # If custom log file specified, use it
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        logger.handlers.clear()
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
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
    else:
        # Use LoggerManager with general module
        return LoggerManager.get_logger(name, "general")


# Create default logger for backward compatibility
logger = LoggerManager.get_logger("rag_system", "general")


# Convenience functions for quick access to common module loggers
def get_document_logger():
    """Get logger for document ingestion."""
    return LoggerManager.get_logger("document_service", "document_ingestion")


def get_vector_store_logger():
    """Get logger for vector store operations."""
    return LoggerManager.get_logger("vector_store", "vector_store")


def get_llm_logger():
    """Get logger for LLM operations."""
    return LoggerManager.get_logger("llm_engine", "llm_queries")


def get_api_logger():
    """Get logger for API endpoints."""
    return LoggerManager.get_logger("api", "api_endpoints")


def get_frontend_logger():
    """Get logger for frontend."""
    return LoggerManager.get_logger("frontend", "frontend")
