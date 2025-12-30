"""
FAISS-based vector store for RAG system with TF-IDF local embeddings.
"""

import os
import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .logger_config import logger
from functools import lru_cache


# Local embedding using TF-IDF (no downloads needed)
@lru_cache(maxsize=1)
def _get_embedding_model(model_name: str):
    """Get cached TF-IDF vectorizer for local embeddings."""
    return TfidfVectorizer(
        max_features=1000,  # Reasonable feature count
        stop_words='english',
        ngram_range=(1, 2),  # Include bigrams
        min_df=1,
        max_df=0.95
    )


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
        
        # Load local embedding model (no downloads)
        try:
            logger.info(f"Initializing local TF-IDF embeddings (model: {embedding_model_name})")
            self.embedding_model = _get_embedding_model(embedding_model_name)
            self.embedding_dim = None  # Will be set after first fitting
            self._is_fitted = False  # Track if vectorizer is fitted
            logger.info(f"Local embedding model ready: dimension will be determined after first fit")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
        
        self.index: Optional[faiss.Index] = None
        self.chunks: List[str] = []
        self.metadata: List[dict] = []  # Store metadata for each chunk: {source_doc, chunk_index, timestamp}
        self._load_or_create_index()

    def reload_from_disk(self) -> int:
        """Reload FAISS index and metadata from disk."""
        logger.info("=== Starting reload vector store flow ===")
        try:
            self.index = None
            self.chunks = []
            self.metadata = []
            self._load_or_create_index()
            logger.info(f"=== Reload flow COMPLETE: {len(self.chunks)} chunk(s) loaded ===")
            return len(self.chunks)
        except Exception as e:
            logger.error(f"RELOAD FAILED: {e}", exc_info=True)
            raise

    def get_document_stats(self, manifest_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Aggregate per-document statistics with optional manifest enrichment."""

        stats: Dict[str, Dict[str, Any]] = {}

        def _normalize_timestamp(value: Optional[Any]) -> Optional[str]:
            if value is None:
                return None
            if isinstance(value, str):
                return value
            if isinstance(value, datetime):
                ts = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
                return ts.isoformat()
            return str(value)

        for meta in self.metadata:
            doc_key = meta.get("source_doc") or "unknown"
            entry = stats.setdefault(doc_key, {
                "source_doc": doc_key,
                "name": doc_key,
                "chunks": 0,
                "last_chunk_at": None,
                "preview": None,
            })

            entry["chunks"] += 1

            timestamp = meta.get("timestamp")
            if timestamp:
                ts_norm = _normalize_timestamp(timestamp)
                if ts_norm and (entry["last_chunk_at"] is None or ts_norm > entry["last_chunk_at"]):
                    entry["last_chunk_at"] = ts_norm

            if entry["preview"] is None and meta.get("preview"):
                entry["preview"] = meta.get("preview")

        manifest_entries: Dict[str, Dict[str, Any]] = {}
        if manifest_path:
            manifest_file = Path(manifest_path)
            if manifest_file.exists():
                try:
                    import yaml  # type: ignore

                    with open(manifest_file, "r", encoding="utf-8") as fh:
                        manifest_data = yaml.safe_load(fh) or {}

                    for doc in manifest_data.get("documents", []):
                        ingestion_info = doc.get("ingestion", {}) or {}
                        key = ingestion_info.get("source_doc") or doc.get("id")
                        filename = doc.get("filename")
                        if not key and filename:
                            key = Path(filename).stem
                        if key:
                            manifest_entries[key] = doc
                except ImportError:
                    logger.warning("PyYAML not installed. Skipping manifest enrichment.")
                except Exception as exc:
                    logger.warning(f"Error parsing manifest {manifest_path}: {exc}")

        for key, entry in stats.items():
            manifest_doc = manifest_entries.get(key)
            if manifest_doc:
                display_name = manifest_doc.get("title") or manifest_doc.get("filename") or entry["name"]
                entry["name"] = display_name
                entry["title"] = manifest_doc.get("title")
                entry["version"] = manifest_doc.get("version")
                entry["owner"] = manifest_doc.get("owner")
                entry["tags"] = manifest_doc.get("tags") or []
                ingestion_info = manifest_doc.get("ingestion", {}) or {}
                entry["ingested_at"] = ingestion_info.get("last_ingested") or entry.get("last_chunk_at")
                entry["source_doc"] = ingestion_info.get("source_doc") or entry["source_doc"]
            else:
                entry.setdefault("tags", [])
                entry.setdefault("ingested_at", entry.get("last_chunk_at"))

        for key, manifest_doc in manifest_entries.items():
            if key not in stats:
                ingestion_info = manifest_doc.get("ingestion", {}) or {}
                stats[key] = {
                    "source_doc": ingestion_info.get("source_doc") or key,
                    "name": manifest_doc.get("title") or manifest_doc.get("filename") or key,
                    "title": manifest_doc.get("title"),
                    "version": manifest_doc.get("version"),
                    "owner": manifest_doc.get("owner"),
                    "tags": manifest_doc.get("tags") or [],
                    "chunks": 0,
                    "last_chunk_at": None,
                    "ingested_at": ingestion_info.get("last_ingested"),
                    "preview": None,
                }

        # Finalize defaults
        for entry in stats.values():
            entry.setdefault("tags", [])
            entry.setdefault("ingested_at", entry.get("last_chunk_at"))
            entry["ingested_at"] = _normalize_timestamp(entry.get("ingested_at"))
            entry["last_chunk_at"] = _normalize_timestamp(entry.get("last_chunk_at"))

        sorted_docs = sorted(
            stats.values(),
            key=lambda item: (item.get("name") or item.get("source_doc") or "").lower()
        )

        return sorted_docs
    
    def _load_or_create_index(self) -> None:
        """Load existing index or create new one."""
        # First check if we have an existing index file
        if self.index_path.exists():
            try:
                logger.info(f"Loading existing index from {self.index_path}")
                self.index = faiss.read_index(str(self.index_path))
                
                # Set embedding dimension from loaded index
                self.embedding_dim = self.index.d
                logger.info(f"Set embedding dimension to {self.embedding_dim} from loaded index")
                
                # Load metadata
                if self.metadata_path.exists():
                    try:
                        with open(self.metadata_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.chunks = data.get('chunks', [])
                            self.metadata = data.get('metadata', [])
                        
                        # Verify chunk count matches index
                        if len(self.chunks) != self.index.ntotal:
                            logger.warning(
                                f"Chunk count ({len(self.chunks)}) doesn't match index size "
                                f"({self.index.ntotal}). Resetting chunks."
                            )
                            self.chunks = []
                            self.metadata = []
                        else:
                            # If metadata is missing, create default entries
                            if len(self.metadata) != len(self.chunks):
                                logger.info(f"Regenerating metadata for {len(self.chunks)} chunks")
                                self.metadata = [{"source_doc": "unknown", "chunk_index": i} for i in range(len(self.chunks))]
                            
                            # Only mark as fitted if we have chunks to work with
                            if len(self.chunks) > 0:
                                # Try to fit the TF-IDF model on existing chunks
                                try:
                                    self.embedding_model.fit(self.chunks)
                                    self._is_fitted = True
                                    logger.info(f"TF-IDF model fitted on {len(self.chunks)} existing chunks")
                                except Exception as e:
                                    logger.warning(f"Could not fit TF-IDF on existing chunks: {e}")
                                    self._is_fitted = False
                            else:
                                self._is_fitted = False
                                logger.info("No existing chunks found, TF-IDF model not fitted yet")
                                
                            logger.info(f"Loaded index with {len(self.chunks)} chunks and metadata")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing metadata JSON: {e}")
                        self.chunks = []
                        self.metadata = []
                    except Exception as e:
                        logger.error(f"Error loading metadata: {e}", exc_info=True)
                        self.chunks = []
                        self.metadata = []
                else:
                    logger.warning("Metadata file not found, starting with empty chunks")
                    self.chunks = []
                    self.metadata = []
            except Exception as e:
                logger.error(f"Error loading index: {e}. Will create new index when embedding dimension is known.", exc_info=True)
                self.index = None
                self.chunks = []
                self.metadata = []
        else:
            logger.info("No existing index found or embedding dimension not set. Will create index when needed.")
            self.index = None
            self.chunks = []
            self.metadata = []
    
    def add_chunks(self, chunks: List[str], document_name: str = "unknown") -> None:
        """
        Add chunks with embeddings to index with comprehensive logging.
        Removes existing chunks from the same document first to avoid duplicates.
        
        Args:
            chunks: List of text chunks to add
            document_name: Name of the source document
        """
        logger.info(f"=== Starting add_chunks flow for document: {document_name} ===")
        
        # Step 0: Remove existing chunks from this document (avoid duplicates)
        existing_count = sum(1 for m in self.metadata if m.get("source_doc") == document_name)
        if existing_count > 0:
            logger.info(f"ADD_CHUNKS STEP 0: Removing {existing_count} existing chunks from '{document_name}'")
            self.delete_document(document_name)
            logger.info(f"ADD_CHUNKS STEP 0 COMPLETE: Cleared previous version of document")
        
        # Step 1: Validate chunks
        if not chunks:
            logger.warning("ADD_CHUNKS STEP 1 FAILED: No chunks provided")
            return
        logger.info(f"ADD_CHUNKS STEP 1 COMPLETE: {len(chunks)} chunk(s) validated")
        
        try:
            # Step 2: Generate TF-IDF embeddings
            logger.info(f"ADD_CHUNKS STEP 2: Generating embeddings for {len(chunks)} chunks")
            
            if not self._is_fitted:
                # Fit on all existing chunks + new chunks
                all_texts = self.chunks + chunks
                self.embedding_model.fit(all_texts)
                self._is_fitted = True
                
                # Set the actual embedding dimension after fitting
                test_embedding = self.embedding_model.transform(["test"]).toarray()
                self.embedding_dim = test_embedding.shape[1]
                logger.info(f"TF-IDF vectorizer fitted on corpus, embedding_dim set to {self.embedding_dim}")
                
                # Create index now that we know the dimension
                if self.index is None:
                    self.index = faiss.IndexFlatIP(self.embedding_dim)
                    logger.info(f"Created new FAISS index with dimension {self.embedding_dim}")
            
            embeddings = self.embedding_model.transform(chunks).toarray()
            embeddings = np.array(embeddings, dtype=np.float32)
            
            # Normalize embeddings for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            embeddings = embeddings / norms
            
            logger.info(f"ADD_CHUNKS STEP 2 COMPLETE: Embeddings generated and normalized (shape: {embeddings.shape})")
            
            # Step 3: Validate embeddings shape
            if embeddings.shape[1] != self.embedding_dim:
                logger.error(f"ADD_CHUNKS STEP 3 FAILED: Dimension mismatch ({embeddings.shape[1]} vs {self.embedding_dim})")
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                    f"got {embeddings.shape[1]}"
                )
            logger.info(f"ADD_CHUNKS STEP 3 COMPLETE: Embeddings shape validated")
            
            # Step 4: Add to index and track metadata
            logger.info(f"ADD_CHUNKS STEP 4: Adding embeddings to FAISS index")
            self.index.add(embeddings)
            start_index = len(self.chunks)
            self.chunks.extend(chunks)
            
            # Store enhanced metadata for each chunk with source document and page info
            import re
            from datetime import datetime
            
            for chunk_index, chunk in enumerate(chunks):
                # Extract page number from chunk if available (from PDF markers)
                page_match = re.search(r'\[PAGE (\d+)\]', chunk)
                page_num = int(page_match.group(1)) if page_match else None
                
                # Extract first heading/section if available
                heading_match = re.search(r'^#+\s*(.+?)$|^([A-Z][A-Za-z\s]+:)', chunk, re.MULTILINE)
                section = heading_match.group(1) or heading_match.group(2) if heading_match else None
                
                # Get preview (first 100 chars without page markers)
                preview_text = re.sub(r'\[PAGE \d+\]', '', chunk).strip()[:100]
                
                chunk_metadata = {
                    "source_doc": document_name,
                    "chunk_index": start_index + chunk_index,
                    "chunk_length": len(chunk),
                    "page": page_num,
                    "section": section.strip() if section else None,
                    "preview": preview_text,
                    "timestamp": datetime.now().isoformat()
                }
                self.metadata.append(chunk_metadata)
            
            logger.info(f"ADD_CHUNKS STEP 4 COMPLETE: Added to index (total chunks: {len(self.chunks)})")
            
            # Step 5: Save index
            logger.info("ADD_CHUNKS STEP 5: Saving index to disk")
            self._save_index()
            logger.info(f"ADD_CHUNKS STEP 5 COMPLETE: Index saved")
            logger.info(f"=== add_chunks flow COMPLETE: {len(chunks)} chunks from '{document_name}' ===")
        except Exception as e:
            logger.error(f"ADD_CHUNKS FAILED: Error adding chunks: {e}", exc_info=True)
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """
        Search for similar chunks with metadata backtracking.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of (chunk, similarity_score, metadata) tuples
        """
        logger.debug(f"=== Starting search flow: query length={len(query)}, top_k={top_k} ===")
        
        # Step 1: Validate chunks
        if not self.chunks:
            logger.warning("SEARCH STEP 1 FAILED: No chunks available")
            return []
        logger.debug(f"SEARCH STEP 1 COMPLETE: {len(self.chunks)} chunks available")
        
        # Step 2: Validate query
        if not query or not query.strip():
            logger.warning("SEARCH STEP 2 FAILED: Empty query provided")
            return []
        logger.debug(f"SEARCH STEP 2 COMPLETE: Query validated ({len(query)} chars)")
        
        try:
            # Step 3: Generate query embedding using TF-IDF
            logger.debug("SEARCH STEP 3: Generating query embedding")
            
            if not self._is_fitted:
                logger.warning("TF-IDF not fitted yet, using simple fallback")
                return []
                
            query_emb = self.embedding_model.transform([query]).toarray()
            query_emb = np.array(query_emb, dtype=np.float32)
            
            # Normalize query embedding
            norm = np.linalg.norm(query_emb)
            if norm > 0:
                query_emb = query_emb / norm
            faiss.normalize_L2(query_emb)
            logger.debug(f"SEARCH STEP 3 COMPLETE: Embedding generated and normalized (shape: {query_emb.shape})")
            
            # Step 4: Search index
            k = min(top_k, len(self.chunks))
            logger.debug(f"SEARCH STEP 4: Searching index with k={k}")
            distances, indices = self.index.search(query_emb, k)
            logger.debug(f"SEARCH STEP 4 COMPLETE: Found {len(indices[0])} candidate(s)")
            
            # Step 5: Process results with metadata
            logger.debug("SEARCH STEP 5: Processing search results with metadata")
            results = []
            invalid_count = 0
            
            for idx, dist in zip(indices[0], distances[0]):
                if 0 <= idx < len(self.chunks):
                    idx_int = int(idx)
                    
                    # Improved similarity calculation based on metric type
                    if hasattr(self.index, 'metric_type') and self.index.metric_type == faiss.METRIC_INNER_PRODUCT:
                        # For normalized vectors with inner product, dist is cosine similarity [-1, 1]
                        # Convert to [0, 1] range: (cosine_sim + 1) / 2
                        similarity = float(max(0.0, min(1.0, (dist + 1.0) / 2.0)))
                    else:
                        # For L2 distance, convert to similarity score
                        # Higher distance = lower similarity
                        similarity = float(max(0.0, min(1.0, 1.0 / (1.0 + dist))))
                    
                    # Include metadata for backtracking
                    chunk_metadata = self.metadata[idx_int] if idx_int < len(self.metadata) else {"source_doc": "unknown"}
                    results.append((self.chunks[idx_int], similarity, chunk_metadata))
                else:
                    invalid_count += 1
                    logger.warning(f"SEARCH STEP 5: Invalid index {idx} returned")
            
            if invalid_count > 0:
                logger.warning(f"SEARCH STEP 5: {invalid_count} invalid index(es) filtered out")
            
            logger.info(f"SEARCH COMPLETE: Returned {len(results)} result(s) with metadata")
            return results
        except Exception as e:
            logger.error(f"SEARCH FAILED: Error during search: {e}", exc_info=True)
            return []
    
    def clear(self) -> None:
        """Clear vector store and reset index with logging."""
        logger.info("=== Starting clear vector store flow ===")
        
        try:
            old_count = len(self.chunks)
            logger.info(f"CLEAR STEP 1: Resetting index (current chunks: {old_count})")
            
            # Reset the vectorizer fitted state when clearing
            self._is_fitted = False
            
            # Create new empty index if we have an embedding dimension
            if self.embedding_dim:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
            else:
                self.index = None
                
            self.chunks = []
            self.metadata = []
            logger.info("CLEAR STEP 1 COMPLETE: Index and metadata cleared")
            
            logger.info("CLEAR STEP 2: Saving cleared index")
            self._save_index()
            logger.info("CLEAR STEP 2 COMPLETE: Index saved")
            logger.info(f"=== Clear flow COMPLETE: Removed {old_count} chunk(s) ===")
        except Exception as e:
            logger.error(f"CLEAR FAILED: Error clearing vector store: {e}", exc_info=True)
            raise
    
    def delete_document(self, document_name: str) -> int:
        """
        Delete all chunks from a specific document.
        
        Args:
            document_name: Name of the document to delete
            
        Returns:
            Number of chunks deleted
        """
        logger.info(f"=== Starting delete_document flow for: {document_name} ===")
        
        try:
            # Find indices of chunks to keep
            indices_to_keep = []
            indices_to_delete = []
            
            for i, meta in enumerate(self.metadata):
                if meta.get("source_doc") == document_name:
                    indices_to_delete.append(i)
                else:
                    indices_to_keep.append(i)
            
            if not indices_to_delete:
                logger.info(f"DELETE_DOC: No chunks found for document '{document_name}'")
                return 0
            
            deleted_count = len(indices_to_delete)
            logger.info(f"DELETE_DOC: Found {deleted_count} chunks to delete")
            
            # Filter chunks and metadata
            new_chunks = [self.chunks[i] for i in indices_to_keep]
            new_metadata = [self.metadata[i] for i in indices_to_keep]
            
            # Rebuild index with remaining chunks
            logger.info(f"DELETE_DOC: Rebuilding index with {len(new_chunks)} remaining chunks")
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.chunks = []
            self.metadata = []
            
            if new_chunks:
                # Re-add remaining chunks with TF-IDF
                if not self._is_fitted:
                    self.embedding_model.fit(new_chunks)
                    self._is_fitted = True
                
                embeddings = self.embedding_model.transform(new_chunks).toarray()
                embeddings = np.array(embeddings, dtype=np.float32)
                
                # Normalize embeddings
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms[norms == 0] = 1
                embeddings = embeddings / norms
                
                self.index.add(embeddings)
                self.chunks = new_chunks
                self.metadata = new_metadata
            
            self._save_index()
            logger.info(f"=== delete_document COMPLETE: Removed {deleted_count} chunks ===")
            return deleted_count
            
        except Exception as e:
            logger.error(f"DELETE_DOC FAILED: Error deleting document: {e}", exc_info=True)
            raise
    
    def _save_index(self) -> None:
        """Save index and metadata to disk."""
        try:
            # Only save if index exists
            if self.index is not None:
                # Save FAISS index
                faiss.write_index(self.index, str(self.index_path))
                logger.debug(f"Saved index ({self.index.ntotal} vectors)")
            else:
                logger.debug("No index to save (index is None)")
            
            # Always save metadata and chunks
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'chunks': self.chunks,
                    'metadata': self.metadata
                }, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved metadata ({len(self.metadata)} entries) and chunks ({len(self.chunks)})")
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
