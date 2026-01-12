"""
__init__ file for backend package.
"""
import sys
from pathlib import Path

# Add src directory to Python path for proper 'backend.xxx' imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from .vectorstore import FAISSVectorStore
from .llm_loader import GroqLLMEngine, get_llm_engine
from .ingest import DocumentIngestor
from .rag_engine import RAGEngine

__all__ = [
    "FAISSVectorStore",
    "GroqLLMEngine", 
    "get_llm_engine",
    "DocumentIngestor",
    "RAGEngine"
]
