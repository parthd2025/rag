"""
FAISS-based vector store for RAG system with neural or TF-IDF embeddings.
"""

import os
import json
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Any as AnyType
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .logger_config import logger
from .docling_reranker import rerank_using_links
from functools import lru_cache


# Cached embedding models
@lru_cache(maxsize=1)
def _get_neural_model(model_name: str):
    """Get cached neural embedding model (SentenceTransformer)."""
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        model = SentenceTransformer(model_name)
        logger.info(f"✓ Neural model loaded successfully (dim={model.get_sentence_embedding_dimension()})")
        return model
    except ImportError:
        logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
        raise
    except Exception as e:
        logger.error(f"Failed to load neural model: {e}")
        raise


@lru_cache(maxsize=1)
def _get_tfidf_model(model_name: str):
    """Get cached TF-IDF vectorizer for local embeddings (fallback)."""
    return TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2),
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
        
        # Load embedding model based on config setting
        from .config import settings
        self.embedding_mode = getattr(settings, 'EMBEDDING_MODE', 'neural')
        
        if self.embedding_mode == "neural":
            try:
                logger.info(f"Using neural embeddings (SentenceTransformer): {embedding_model_name}")
                self.encoder = _get_neural_model(embedding_model_name)
                self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
                self._is_fitted = True  # Neural models don't need fitting
                logger.info(f"✓ Neural embeddings ready (dim={self.embedding_dim})")
            except Exception as e:
                logger.warning(f"Neural embeddings failed, falling back to TF-IDF: {e}")
                self.embedding_mode = "tfidf"
        
        if self.embedding_mode == "tfidf":
            logger.info(f"Using TF-IDF embeddings (legacy mode)")
            self.embedding_model = _get_tfidf_model(embedding_model_name)
            self.embedding_dim = None  # Will be set after first fitting
            self._is_fitted = False
            logger.info(f"TF-IDF embedding model ready (requires fitting)")
        
        self.index: Optional[faiss.Index] = None
        self.chunks: List[str] = []
        self.metadata: List[dict] = []
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
                
                # Verify embedding dimension matches
                if self.embedding_dim and self.index.d != self.embedding_dim:
                    logger.warning(
                        f"Index dimension ({self.index.d}) doesn't match model dimension ({self.embedding_dim}). "
                        f"Need re-indexing."
                    )
                    self.index = None
                else:
                    self.embedding_dim = self.index.d
                    logger.info(f"✓ Loaded index with {self.index.ntotal} vectors (dim={self.embedding_dim})")
                
                # Load metadata
                if self.metadata_path.exists():
                    try:
                        with open(self.metadata_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.chunks = data.get('chunks', [])
                            self.metadata = data.get('metadata', [])
                        
                        # Verify chunk count matches index
                        if self.index and len(self.chunks) != self.index.ntotal:
                            logger.warning(
                                f"Chunk count ({len(self.chunks)}) doesn't match index size "
                                f"({self.index.ntotal}). Resetting."
                            )
                            self.chunks = []
                            self.metadata = []
                            self.index = None
                        else:
                            # If metadata is missing, create default entries
                            if len(self.metadata) != len(self.chunks):
                                logger.info(f"Regenerating metadata for {len(self.chunks)} chunks")
                                self.metadata = [{"source_doc": "unknown", "chunk_index": i} for i in range(len(self.chunks))]
                            
                            # For TF-IDF mode, fit on existing chunks
                            if self.embedding_mode == "tfidf" and len(self.chunks) > 0:
                                try:
                                    logger.info("Fitting TF-IDF model on existing chunks...")
                                    self.embedding_model.fit(self.chunks)
                                    self._is_fitted = True
                                    logger.info(f"✓ TF-IDF fitted on {len(self.chunks)} chunks")
                                except Exception as e:
                                    logger.warning(f"Could not fit TF-IDF: {e}")
                                    self._is_fitted = False
                                
                            logger.info(f"✓ Loaded {len(self.chunks)} chunks with metadata")
                    except Exception as e:
                        logger.error(f"Error loading metadata: {e}", exc_info=True)
                        self.chunks = []
                        self.metadata = []
                else:
                    logger.warning("Metadata file not found")
                    self.chunks = []
                    self.metadata = []
            except Exception as e:
                logger.error(f"Error loading index: {e}", exc_info=True)
                self.index = None
                self.chunks = []
                self.metadata = []
        else:
            logger.info("No existing index found. Will create when needed.")
            self.index = None
            self.chunks = []
            self.metadata = []
    
    def add_chunks(self, chunks: List[AnyType], document_name: str = "unknown") -> None:
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
        
        # Step 1: Validate chunks and normalize input
        if not chunks:
            logger.warning("ADD_CHUNKS STEP 1 FAILED: No chunks provided")
            return

        # Support either list of raw strings or list of dicts returned by Docling client
        normalized_texts: List[str] = []
        normalized_inputs: List[dict] = []
        for i, c in enumerate(chunks):
            if isinstance(c, dict):
                text = c.get("text") or c.get("chunk") or ""
                normalized_texts.append(text)
                normalized_inputs.append(c)
            else:
                text = str(c)
                normalized_texts.append(text)
                normalized_inputs.append({"text": text})

        logger.info(f"ADD_CHUNKS STEP 1 COMPLETE: {len(normalized_texts)} chunk(s) validated")
        
        try:
            # Step 2: Generate embeddings
            logger.info(f"ADD_CHUNKS STEP 2: Generating embeddings for {len(normalized_texts)} chunks")
            
            if self.embedding_mode == "neural":
                # Neural embeddings (SentenceTransformer)
                embeddings = self.encoder.encode(
                    normalized_texts,
                    normalize_embeddings=True,
                    batch_size=32,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                embeddings = np.array(embeddings, dtype=np.float32)
                logger.info(f"✓ Neural embeddings generated (shape: {embeddings.shape})")
                
            else:
                # TF-IDF embeddings (legacy)
                if not self._is_fitted:
                    # Fit on all existing chunks + new chunks
                    all_texts = self.chunks + chunks
                    self.embedding_model.fit(all_texts)
                    self._is_fitted = True
                    
                    # Set the actual embedding dimension after fitting
                    test_embedding = self.embedding_model.transform(["test"]).toarray()
                    self.embedding_dim = test_embedding.shape[1]
                    logger.info(f"TF-IDF vectorizer fitted, embedding_dim={self.embedding_dim}")
                    
                    # Create index now that we know the dimension
                    if self.index is None:
                        self.index = faiss.IndexFlatIP(self.embedding_dim)
                        logger.info(f"Created new FAISS index (dim={self.embedding_dim})")
                
                embeddings = self.embedding_model.transform(chunks).toarray()
                embeddings = np.array(embeddings, dtype=np.float32)
                
                # Normalize embeddings for cosine similarity
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms[norms == 0] = 1
                embeddings = embeddings / norms
                
                logger.info(f"✓ TF-IDF embeddings generated (shape: {embeddings.shape})")
            
            # Step 3: Create index if needed
            if self.index is None:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                logger.info(f"Created new FAISS index (dim={self.embedding_dim})")
            
            # Step 4: Validate embeddings shape
            if embeddings.shape[1] != self.embedding_dim:
                logger.error(f"Dimension mismatch: {embeddings.shape[1]} vs {self.embedding_dim}")
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                    f"got {embeddings.shape[1]}"
                )
            
            # Step 5: Add to index and track metadata
            logger.info(f"ADD_CHUNKS STEP 5: Adding embeddings to FAISS index")
            self.index.add(embeddings)
            start_index = len(self.chunks)
            # Store texts into chunks list (normalized_texts)
            self.chunks.extend(normalized_texts)

            # Store enhanced metadata for each chunk
            import re

            for chunk_index, input_obj in enumerate(normalized_inputs):
                chunk_text = input_obj.get("text", "")

                # Extract page number from chunk if available
                page_match = re.search(r'\[PAGE (\d+)\]', chunk_text)
                page_num = int(page_match.group(1)) if page_match else None

                # Extract first heading/section if available
                heading_match = re.search(r'^#+\s*(.+?)$|^([A-Z][A-Za-z\s]+:)', chunk_text, re.MULTILINE)
                section = heading_match.group(1) or heading_match.group(2) if heading_match else None

                # Get preview (first 100 chars without page markers)
                preview_text = re.sub(r'\[PAGE \d+\]', '', chunk_text).strip()[:100]

                # Base metadata (existing fields)
                chunk_metadata = {
                    "source_doc": document_name,
                    "chunk_index": start_index + chunk_index,
                    "chunk_length": len(chunk_text),
                    "page": page_num,
                    "section": section.strip() if section else None,
                    "preview": preview_text,
                    "timestamp": datetime.now().isoformat(),
                    "embedding_mode": self.embedding_mode
                }

                # If input provided its own meta/node_id/links (from Docling), merge them
                provided_meta = input_obj.get("meta") or input_obj.get("metadata") or {}
                if provided_meta:
                    # Merge but don't overwrite the base keys unless explicitly provided
                    for k, v in provided_meta.items():
                        if k not in chunk_metadata or chunk_metadata.get(k) is None:
                            chunk_metadata[k] = v
                        else:
                            # keep both under a namespaced key
                            chunk_metadata.setdefault("provided_meta", {})[k] = v

                # Node id and links from enriched node
                node_id = input_obj.get("id") or input_obj.get("node_id") or (provided_meta.get("node_id") if isinstance(provided_meta, dict) else None)
                if node_id:
                    chunk_metadata["node_id"] = node_id

                links = input_obj.get("links") or provided_meta.get("links") if isinstance(provided_meta, dict) else input_obj.get("links") or []
                if links:
                    chunk_metadata["links"] = links

                self.metadata.append(chunk_metadata)
            
            logger.info(f"ADD_CHUNKS STEP 5 COMPLETE: Added to index (total: {len(self.chunks)} chunks)")
            
            # Step 6: Save index
            logger.info("ADD_CHUNKS STEP 6: Saving index to disk")
            self._save_index()
            logger.info(f"ADD_CHUNKS STEP 6 COMPLETE: Index saved")
            logger.info(f"=== add_chunks flow COMPLETE: {len(chunks)} chunks from '{document_name}' ===")
        except Exception as e:
            logger.error(f"ADD_CHUNKS FAILED: {e}", exc_info=True)
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
            # Step 3: Generate query embedding
            logger.debug("SEARCH STEP 3: Generating query embedding")
            
            if self.embedding_mode == "neural":
                # Neural embeddings
                query_emb = self.encoder.encode(
                    [query],
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
                query_emb = np.array(query_emb, dtype=np.float32)
                logger.debug(f"✓ Neural query embedding generated (shape: {query_emb.shape})")
                
            else:
                # TF-IDF embeddings
                if not self._is_fitted:
                    logger.warning("TF-IDF not fitted yet")
                    return []
                    
                query_emb = self.embedding_model.transform([query]).toarray()
                query_emb = np.array(query_emb, dtype=np.float32)
                
                # Normalize query embedding
                norm = np.linalg.norm(query_emb)
                if norm > 0:
                    query_emb = query_emb / norm
                logger.debug(f"✓ TF-IDF query embedding generated (shape: {query_emb.shape})")
            
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
                    
                    # For inner product on normalized vectors, dist is cosine similarity
                    # Convert to [0, 1] range
                    similarity = float(max(0.0, min(1.0, (dist + 1.0) / 2.0)))
                    
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
            logger.error(f"SEARCH FAILED: {e}", exc_info=True)
            return []

    def search_with_docling(self, query: str, top_k: int = 5, expand_factor: int = 2) -> List[Tuple[str, float, dict]]:
        """Search and rerank results using Docling links when available.

        This method performs a regular search for a larger candidate set (top_k * expand_factor),
        then applies a simple Docling-link-based reranker and returns the top_k results.
        """
        # Get a larger candidate set to allow reranking via links
        candidate_k = max(top_k * expand_factor, top_k)
        candidates = self.search(query, top_k=candidate_k)

        if not candidates:
            return []

        # Use reranker which expects (text, score, metadata) entries
        try:
            reranked = rerank_using_links(candidates)
            # Return top_k after rerank
            return reranked[:top_k]
        except Exception:
            logger.exception("Docling rerank failed—returning original candidates")
            return candidates[:top_k]
    
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

    def get_all_chunks_by_document(self, document_name: str) -> List[tuple]:
        """
        Retrieve ALL chunks from a specific document (for table-aware retrieval).
        
        Args:
            document_name: Name of the document to retrieve
            
        Returns:
            List of tuples: [(chunk_text, 1.0, metadata), ...]
        """
        logger.info(f"TABLE-AWARE: Retrieving all chunks from document '{document_name}'")
        
        results = []
        for i, meta in enumerate(self.metadata):
            if meta.get("source_doc") == document_name:
                # Return with score 1.0 since we're not doing similarity ranking
                results.append((self.chunks[i], 1.0, meta))
        
        logger.info(f"TABLE-AWARE: Retrieved {len(results)} chunks from '{document_name}'")
        return results
    
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
