"""
FAISS-based vector store for RAG system with improved error handling and type hints.
"""

import os
import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer

from logger_config import logger
from functools import lru_cache


# Cache embedding model to avoid reloading
@lru_cache(maxsize=1)
def _get_embedding_model(model_name: str):
    """Get cached embedding model instance."""
    return SentenceTransformer(model_name)


class FAISSVectorStore:
    """FAISS vector store for semantic search with persistence."""
    
    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        index_path: str = "data/embeddings/faiss.index",
        metadata_path: str = "data/embeddings/metadata.json"
    ):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_model_name: Name of the embedding model
            index_path: Path to save/load FAISS index
            metadata_path: Path to save/load metadata
        """
        self.embedding_model_name = embedding_model_name
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        
        # Ensure parent directories exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load embedding model (cached)
        try:
            logger.info(f"Loading embedding model: {embedding_model_name}")
            self.embedding_model = _get_embedding_model(embedding_model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded: dimension={self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}", exc_info=True)
            raise
        
        self.index: Optional[faiss.Index] = None
        self.chunks: List[str] = []
        self._load_or_create_index()
    
    def _load_or_create_index(self) -> None:
        """Load existing index or create new one."""
        if self.index_path.exists():
            try:
                logger.info(f"Loading existing index from {self.index_path}")
                self.index = faiss.read_index(str(self.index_path))
                
                # Verify index dimension matches embedding dimension
                if self.index.d != self.embedding_dim:
                    logger.warning(
                        f"Index dimension ({self.index.d}) doesn't match embedding dimension "
                        f"({self.embedding_dim}). Creating new index."
                    )
                    self.index = faiss.IndexFlatL2(self.embedding_dim)
                    self.chunks = []
                else:
                    # Load metadata
                    if self.metadata_path.exists():
                        try:
                            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                self.chunks = data.get('chunks', [])
                            
                            # Verify chunk count matches index
                            if len(self.chunks) != self.index.ntotal:
                                logger.warning(
                                    f"Chunk count ({len(self.chunks)}) doesn't match index size "
                                    f"({self.index.ntotal}). Resetting chunks."
                                )
                                self.chunks = []
                            else:
                                logger.info(f"Loaded index with {len(self.chunks)} chunks")
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing metadata JSON: {e}")
                            self.chunks = []
                        except Exception as e:
                            logger.error(f"Error loading metadata: {e}", exc_info=True)
                            self.chunks = []
                    else:
                        logger.warning("Metadata file not found, starting with empty chunks")
                        self.chunks = []
            except Exception as e:
                logger.error(f"Error loading index: {e}. Creating new index.", exc_info=True)
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.chunks = []
        else:
            logger.info("No existing index found, creating new one")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.chunks = []
    
    def add_chunks(self, chunks: List[str], document_name: str = "unknown") -> None:
        """
        Add chunks with embeddings to index.
        
        Args:
            chunks: List of text chunks to add
            document_name: Name of the source document
        """
        if not chunks:
            logger.warning("No chunks provided to add")
            return
        
        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embedding_model.encode(
                chunks,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32
            )
            embeddings = np.array(embeddings, dtype=np.float32)
            
            # Validate embeddings shape
            if embeddings.shape[1] != self.embedding_dim:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                    f"got {embeddings.shape[1]}"
                )
            
            # Add to index
            self.index.add(embeddings)
            self.chunks.extend(chunks)
            
            logger.info(f"Added {len(chunks)} chunks from '{document_name}' (total: {len(self.chunks)})")
            self._save_index()
        except Exception as e:
            logger.error(f"Error adding chunks: {e}", exc_info=True)
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar chunks.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        if not self.chunks:
            logger.debug("No chunks available for search")
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        try:
            # Generate query embedding
            query_emb = self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            ).astype(np.float32)
            
            # Search
            k = min(top_k, len(self.chunks))
            distances, indices = self.index.search(query_emb, k)
            
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                # Validate index
                if 0 <= idx < len(self.chunks):
                    # Convert L2 distance to similarity (1 / (1 + distance))
                    # This gives a similarity score between 0 and 1
                    similarity = float(1.0 / (1.0 + dist))
                    results.append((self.chunks[int(idx)], similarity))
                else:
                    logger.warning(f"Invalid index {idx} returned from search")
            
            logger.debug(f"Search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}", exc_info=True)
            return []
    
    def clear(self) -> None:
        """Clear vector store and reset index."""
        try:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.chunks = []
            self._save_index()
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}", exc_info=True)
            raise
    
    def _save_index(self) -> None:
        """Save index and metadata to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump({'chunks': self.chunks}, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved index ({self.index.ntotal} vectors) and metadata")
        except Exception as e:
            logger.error(f"Error saving index: {e}", exc_info=True)
            raise
    
    def get_statistics(self) -> dict:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.embedding_dim,
            "model": self.embedding_model_name,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path)
        }
