"""
Unified configuration management for RAG system.
"""
import os
from pathlib import Path
from typing import Optional
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
    GEMINI_API_KEY: Optional[str] = Field(None, env="GEMINI_API_KEY")
    
    # Server Configuration
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8001, env="API_PORT")
    FRONTEND_PORT: int = Field(8501, env="FRONTEND_PORT")
    API_URL: str = Field("http://localhost:8001", env="API_URL")
    
    # Model Configuration
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    LLM_MODEL: str = Field("llama-3.3-70b-versatile", env="LLM_MODEL")
    LLM_PROVIDER: str = Field("groq", env="LLM_PROVIDER")  # groq or gemini
    
    # RAG Configuration
    TOP_K: int = Field(5, env="TOP_K")
    TEMPERATURE: float = Field(0.7, env="TEMPERATURE")
    MAX_TOKENS: int = Field(512, env="MAX_TOKENS")
    
    # Chunking Configuration
    CHUNK_SIZE: int = Field(1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(200, env="CHUNK_OVERLAP")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB default
    ALLOWED_EXTENSIONS: str = Field(".pdf,.docx,.txt,.md", env="ALLOWED_EXTENSIONS")
    
    # Vector Store Configuration
    INDEX_PATH: str = Field("data/embeddings/faiss.index", env="INDEX_PATH")
    METADATA_PATH: str = Field("data/embeddings/metadata.json", env="METADATA_PATH")
    
    # CORS Configuration
    CORS_ORIGINS: str = Field("http://localhost:8501,http://127.0.0.1:8501", env="CORS_ORIGINS")
    PRODUCTION: bool = Field(False, env="PRODUCTION")
    
    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("rag_system.log", env="LOG_FILE")
    LOG_MAX_BYTES: int = Field(10 * 1024 * 1024, env="LOG_MAX_BYTES")  # 10MB
    LOG_BACKUP_COUNT: int = Field(5, env="LOG_BACKUP_COUNT")
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_extensions(cls, v):
        """Parse comma-separated extensions into set."""
        if isinstance(v, str):
            return set(ext.strip() for ext in v.split(",") if ext.strip())
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @property
    def allowed_extensions_set(self) -> set:
        """Get allowed extensions as a set."""
        if isinstance(self.ALLOWED_EXTENSIONS, set):
            return self.ALLOWED_EXTENSIONS
        return set(ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip())
    
    @property
    def cors_origins_list(self) -> list:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

