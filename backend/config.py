"""
Unified configuration management for RAG system.
"""
import os
from pathlib import Path
from typing import Optional, List, Set
from pydantic import Field, validator

# Support both Pydantic v1 and v2
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    GROQ_API_KEY: Optional[str] = Field(None, env="GROQ_API_KEY")
    
    # Server Configuration
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    FRONTEND_PORT: int = Field(8501, env="FRONTEND_PORT")
    API_URL: str = Field("http://localhost:8000", env="API_URL")
    
    # Model Configuration
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_MODE: str = Field("neural", env="EMBEDDING_MODE")  # "neural" or "tfidf"
    LLM_MODEL: str = Field("llama-3.3-70b-versatile", env="LLM_MODEL")
    LLM_PROVIDER: str = Field("groq", env="LLM_PROVIDER")
    
    # RAG Configuration - Optimized for better quality
    TOP_K: int = Field(12, env="TOP_K")  # Increased for maximum coverage
    TEMPERATURE: float = Field(0.3, env="TEMPERATURE")  # Lower for more consistent answers
    MAX_TOKENS: int = Field(1000, env="MAX_TOKENS")  # Increased for detailed answers
    CONTEXT_WINDOW_SIZE: int = Field(4000, env="CONTEXT_WINDOW_SIZE")  # Larger context window
    
    # Chunking Configuration - Optimized for specific term retrieval
    CHUNK_SIZE: int = Field(800, env="CHUNK_SIZE")  # Smaller chunks for precision
    CHUNK_OVERLAP: int = Field(100, env="CHUNK_OVERLAP")  # Increased overlap for context preservation
    CHUNKING_LEVEL: int = Field(3, env="CHUNKING_LEVEL")  # Best practice level
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB default
    ALLOWED_EXTENSIONS: Set[str] = Field(
        default_factory=lambda: {
            ".pdf", ".docx", ".txt", ".md",
            ".csv", ".xlsx", ".xls",
            ".pptx",
            ".html", ".htm", ".xml",
            ".png", ".jpg", ".jpeg"
        },
        env="ALLOWED_EXTENSIONS",
    )
    ENABLE_OCR: bool = Field(False, env="ENABLE_OCR")  # Only enable for scanned/image documents
    
    # Vector Store Configuration
    INDEX_PATH: str = Field("data/embeddings/faiss.index", env="INDEX_PATH")
    METADATA_PATH: str = Field("data/embeddings/metadata.json", env="METADATA_PATH")
    KNOWLEDGE_MANIFEST_PATH: str = Field("docs/knowledge-base/manifest.yaml", env="KNOWLEDGE_MANIFEST_PATH")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:8501", "http://127.0.0.1:8501"],
        env="CORS_ORIGINS",
    )
    PRODUCTION: bool = Field(False, env="PRODUCTION")
    
    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/rag_system.log", env="LOG_FILE")
    LOG_MAX_BYTES: int = Field(10 * 1024 * 1024, env="LOG_MAX_BYTES")  # 10MB
    LOG_BACKUP_COUNT: int = Field(5, env="LOG_BACKUP_COUNT")
    MAX_SUGGESTED_QUESTIONS: int = Field(8, env="MAX_SUGGESTED_QUESTIONS")
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_extensions(cls, v):
        """Parse ALLOWED_EXTENSIONS from env into a set."""
        if isinstance(v, str):
            return {ext.strip() for ext in v.split(",") if ext.strip()}
        if isinstance(v, (list, set, tuple)):
            return {str(ext).strip() for ext in v if str(ext).strip()}
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from env into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, (list, set, tuple)):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return v

    @validator("CHUNKING_LEVEL", pre=True, always=True)
    def clamp_chunking_level(cls, v):
        """Ensure chunking level stays within 1-10."""
        try:
            level = int(v)
        except (TypeError, ValueError):
            return 5
        return max(1, min(10, level))

    @validator("CONTEXT_WINDOW_SIZE", pre=True, always=True)
    def clamp_context_window(cls, v):
        """Ensure context window size remains in a sane range."""
        try:
            size = int(v)
        except (TypeError, ValueError):
            return 2048
        return max(256, min(size, 8192))

    @validator("MAX_SUGGESTED_QUESTIONS", pre=True, always=True)
    def clamp_question_count(cls, v):
        """Ensure suggested question count is positive and reasonable."""
        try:
            count = int(v)
        except (TypeError, ValueError):
            return 8
        return max(1, min(count, 20))
    
    @property
    def allowed_extensions_set(self) -> Set[str]:
        """Get allowed extensions as a set."""
        return self.ALLOWED_EXTENSIONS
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return self.CORS_ORIGINS
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env without validation errors


# Global settings instance
settings = Settings()

