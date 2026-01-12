"""
RAG (Retrieval-Augmented Generation) engine with improved error handling and type hints.
"""

from typing import List, Tuple, Dict, Optional, Any, Set
from .logger_config import logger
from .config import settings
import re
from collections import Counter

try:
    import opik
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    logger.warning("Opik not available - tracing disabled")
    # Create a no-op decorator
    def track(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class RAGEngine:
    """Main RAG engine combining retrieval and generation."""
    
    def __init__(
        self,
        vector_store,
        llm_engine,
        top_k: int = 8,
        temperature: float = 0.7,
        context_window_size: Optional[int] = None,
        enable_hybrid_search: bool = True,
        keyword_weight: float = 0.4,
        semantic_weight: float = 0.6
    ):
        """
        Initialize RAG engine with hybrid search capabilities.
        
        Args:
            vector_store: Vector store instance for retrieval
            llm_engine: LLM engine instance for generation
            top_k: Number of chunks to retrieve
            temperature: LLM temperature parameter
            context_window_size: Maximum characters allowed in aggregated context
            enable_hybrid_search: Whether to use hybrid (semantic + keyword) search
            keyword_weight: Weight for keyword search component (0.0-1.0)
            semantic_weight: Weight for semantic search component (0.0-1.0)
        """
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        if not (0.0 <= keyword_weight <= 1.0) or not (0.0 <= semantic_weight <= 1.0):
            raise ValueError("Search weights must be between 0.0 and 1.0")
        if abs(keyword_weight + semantic_weight - 1.0) > 0.01:
            raise ValueError("Keyword and semantic weights should sum to 1.0")
        
        self.vector_store = vector_store
        self.llm_engine = llm_engine
        self.top_k = top_k
        self.temperature = temperature
        self.min_similarity_threshold = 0.4  # Improved threshold for better quality
        self.context_window_size = context_window_size or settings.CONTEXT_WINDOW_SIZE
        
        # Hybrid search configuration
        self.enable_hybrid_search = enable_hybrid_search
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
        
        logger.info(
            f"RAGEngine initialized: top_k={top_k}, temperature={temperature}, "
            f"hybrid_search={enable_hybrid_search}, keyword_weight={keyword_weight}, "
            f"semantic_weight={semantic_weight}"
        )

    def _extract_document_name(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Extract clean document name from metadata."""
        if not metadata:
            return "Unknown Document"
        
        # Try different metadata fields for document name
        document = metadata.get("document") or metadata.get("source_doc")
        
        if isinstance(document, list) and document:
            # If it's a list, join the names
            return " + ".join(str(d) for d in document)
        elif document:
            return str(document)
        
        return "Unknown Document"
    
    def _format_source_entry(
        self,
        index: int,
        chunk: str,
        similarity: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Normalize chunk metadata for downstream consumers with enhanced formatting."""
        metadata = metadata or {}
        document = metadata.get("document") or metadata.get("source_doc") or "Unknown"
        doc_name = self._extract_document_name(metadata)
        
        # Create detailed preview (3 lines instead of 1)
        preview_lines = chunk.split('\n')[:3]
        preview = '\n'.join(preview_lines)
        if len(chunk) > len(preview):
            preview += "..."
        
        return {
            "index": index,
            "document": document,
            "document_name": doc_name,
            "source_doc": document,
            "chunk": chunk,
            "content": chunk,
            "chunk_preview": preview,
            "formatted_preview": f"{chunk[:200]}{'...' if len(chunk) > 200 else ''}",
            "similarity": round(similarity, 4),
            "relevance_score": similarity,
            "chunk_length": len(chunk),
            "chunk_index": metadata.get("chunk_index"),
            "page": metadata.get("page"),
            "section": metadata.get("section"),
            "timestamp": metadata.get("timestamp"),
        }

    def _preprocess_query(self, query: str) -> str:
        """Preprocess query with term expansion for better matching."""
        # Handle common variations and synonyms
        query_lower = query.lower()
        
        # M2 specific expansions
        if 'm2' in query_lower:
            query += ' mileage allowance transportation'
        
        # Add document-specific terms
        if any(term in query_lower for term in ['benefit', 'policy', 'allowance']):
            query += ' mindbowser'
        
        return query
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text for keyword search."""
        # Remove punctuation and convert to lowercase, preserve alphanumeric
        cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words and filter out short words and common stopwords
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
            'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with',
            'this', 'but', 'they', 'have', 'had', 'what', 'said', 'each', 'which', 'she',
            'do', 'how', 'their', 'if', 'up', 'out', 'many', 'then', 'them', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more', 'go', 'no',
            'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'oil', 'its', 'now',
            'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
        }
        
        words = [word for word in cleaned_text.split() 
                if len(word) > 2 and word not in stopwords]
        
        return set(words)

    def _calculate_keyword_score(self, query_keywords: Set[str], chunk_text: str) -> float:
        """Calculate keyword-based relevance score for a chunk."""
        if not query_keywords:
            return 0.0
        
        chunk_keywords = self._extract_keywords(chunk_text)
        
        if not chunk_keywords:
            return 0.0
        
        # Calculate intersection score
        intersection = query_keywords.intersection(chunk_keywords)
        
        if not intersection:
            return 0.0
        
        # Use Jaccard similarity with frequency weighting
        intersection_score = len(intersection) / len(query_keywords)
        
        # Boost score if keywords appear multiple times
        chunk_lower = chunk_text.lower()
        frequency_boost = 0
        for keyword in intersection:
            frequency_boost += chunk_lower.count(keyword) - 1  # -1 because we already counted once
        
        # Normalize frequency boost
        frequency_boost = min(frequency_boost * 0.1, 0.5)  # Max 0.5 boost
        
        return min(intersection_score + frequency_boost, 1.0)
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query with term expansion for better matching."""
        # Handle common variations and synonyms
        query_lower = query.lower()
        
        # M2 specific expansions
        if 'm2' in query_lower:
            query += ' mileage allowance transportation'
        
        # Add document-specific terms
        if any(term in query_lower for term in ['benefit', 'policy', 'allowance']):
            query += ' mindbowser'
        
        return query

    def _search_with_document_boost(self, question: str, top_k: int) -> List[Tuple[str, float, dict]]:
        """Search with document-specific boosting for M2 queries."""
        logger.info("Performing search with document boosting for M2 queries")
        
        # First try normal hybrid search
        if self.enable_hybrid_search:
            results = self._hybrid_search(question, top_k * 2)
        else:
            results = self.vector_store.search(question, top_k=top_k * 2)
        
        # Boost M2/mileage document results
        boosted_results = []
        m2_results = []
        other_results = []
        
        for chunk, score, metadata in results:
            doc_name = self._extract_document_name(metadata).lower()
            
            # Identify M2 or mileage related documents
            if any(term in doc_name for term in ['m2', 'mileage', 'miles', 'travel']):
                # Apply significant boost to M2 documents
                boosted_score = min(score * 1.5, 1.0)  # 50% boost
                m2_results.append((chunk, boosted_score, metadata))
                logger.info(f"M2 Document found and boosted: {doc_name} (score: {score:.3f} -> {boosted_score:.3f})")
            else:
                other_results.append((chunk, score, metadata))
        
        # Prioritize M2 results
        boosted_results = m2_results + other_results
        boosted_results.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Document boosting: {len(m2_results)} M2 results, {len(other_results)} other results")
        return boosted_results[:top_k]

    def _hybrid_search(self, question: str, top_k: int) -> List[Tuple[str, float, dict]]:
        """Perform hybrid search combining semantic and keyword search."""
        logger.info(f"Performing hybrid search: semantic_weight={self.semantic_weight}, keyword_weight={self.keyword_weight}")
        
        # Preprocess query for better matching
        expanded_question = self._preprocess_query(question)
        logger.info(f"Expanded query: {expanded_question[:100]}...")
        
        # Step 1: Get semantic search results with expanded query
        semantic_results = self.vector_store.search(expanded_question, top_k=min(top_k * 2, 50))
        
        if not semantic_results:
            logger.warning("No semantic search results found")
            return []
        
        # Step 2: Extract keywords from expanded query
        query_keywords = self._extract_keywords(expanded_question)
        logger.info(f"Extracted {len(query_keywords)} keywords from expanded query: {list(query_keywords)[:5]}")
        
        # Step 3: Re-rank results using hybrid scoring
        hybrid_results = []
        
        for chunk, semantic_score, metadata in semantic_results:
            # Calculate keyword score
            keyword_score = self._calculate_keyword_score(query_keywords, chunk)
            
            # Combine scores using weights
            hybrid_score = (
                self.semantic_weight * semantic_score +
                self.keyword_weight * keyword_score
            )
            
            hybrid_results.append((chunk, hybrid_score, metadata))
            
        # Step 4: Sort by hybrid score and return top-k
        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        
        # Log scoring details for top results
        for i, (chunk, score, metadata) in enumerate(hybrid_results[:3]):
            semantic_score = next((s for c, s, m in semantic_results if c == chunk), 0.0)
            keyword_score = self._calculate_keyword_score(query_keywords, chunk)
            doc_name = self._extract_document_name(metadata)
            logger.info(
                f"Result {i+1}: {doc_name[:30]} - Hybrid: {score:.3f} "
                f"(Semantic: {semantic_score:.3f}, Keyword: {keyword_score:.3f})"
            )
        
        return hybrid_results[:top_k]

    def _document_specific_search(self, question: str, document_names: List[str], top_k: int) -> List[Tuple[str, float, dict]]:
        """Search within specific documents only."""
        logger.info(f"Performing document-specific search for documents: {document_names}")
        
        # Get all results first
        if self.enable_hybrid_search:
            all_results = self._hybrid_search(question, top_k * 3)  # Get more results to filter
        else:
            all_results = self.vector_store.search(question, top_k=top_k * 3)
        
        # Filter results by document names
        filtered_results = []
        for chunk, score, metadata in all_results:
            doc_name = self._extract_document_name(metadata)
            
            # Check if document name matches any of the specified documents
            if any(doc.lower() in doc_name.lower() or doc_name.lower() in doc.lower() 
                   for doc in document_names):
                filtered_results.append((chunk, score, metadata))
        
        logger.info(f"Document filtering: {len(all_results)} -> {len(filtered_results)} results")
        
        return filtered_results[:top_k]

    def _cross_document_search(self, question: str, top_k: int) -> Dict[str, List[Tuple[str, float, dict]]]:
        """Perform cross-document search for comparative queries."""
        logger.info("Performing cross-document search for comparative analysis")
        
        # Get results using hybrid search
        if self.enable_hybrid_search:
            all_results = self._hybrid_search(question, top_k * 2)
        else:
            all_results = self.vector_store.search(question, top_k=top_k * 2)
        
        # Group results by document
        doc_results = {}
        for chunk, score, metadata in all_results:
            doc_name = self._extract_document_name(metadata)
            
            if doc_name not in doc_results:
                doc_results[doc_name] = []
            
            doc_results[doc_name].append((chunk, score, metadata))
        
        # Ensure we have results from multiple documents for comparison
        if len(doc_results) < 2:
            logger.info(f"Cross-document search: Only {len(doc_results)} document(s) found")
        else:
            logger.info(f"Cross-document search: {len(doc_results)} documents with comparative results")
        
        # Sort results within each document and limit
        for doc_name in doc_results:
            doc_results[doc_name] = sorted(
                doc_results[doc_name], 
                key=lambda x: x[1], 
                reverse=True
            )[:top_k // len(doc_results) + 1]
        
        return doc_results

    @track(
        name="Document Retrieval",
        project_name="rag-system",
        tags=["retrieval", "vectorstore"]
    )
    def retrieve_context(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """Return top matching chunks with normalized metadata."""
        if not question or not question.strip():
            raise ValueError("question must be a non-empty string")

        k = top_k or self.top_k
        if k <= 0:
            raise ValueError("top_k must be positive")

        logger.info(f"Retrieving context: question_len={len(question)}, top_k={k}")
        results = self.vector_store.search(question, top_k=k)
        if not results:
            logger.info("No context retrieved")
            return {"chunks": [], "metadata": [], "confidence": 0.0}

        formatted_sources = [
            self._format_source_entry(i, chunk, similarity, metadata)
            for i, (chunk, similarity, metadata) in enumerate(results, 1)
        ]

        avg_similarity = sum(item["relevance_score"] for item in formatted_sources) / len(formatted_sources)

        return {
            "chunks": [chunk for chunk, _, _ in results],
            "metadata": formatted_sources,
            "confidence": avg_similarity,
        }
    
    @track(
        name="Answer Query",
        project_name="rag-system",
        tags=["generation", "llm"]
    )
    def answer_query(self, question: str) -> str:
        """
        Answer a question using RAG (simple version without context).
        
        Args:
            question: Question to answer
            
        Returns:
            Answer string
        """
        if not question or not question.strip():
            logger.warning("Empty question provided")
            return "Please provide a valid question."
        
        if not self.llm_engine.is_ready():
            logger.error("LLM engine not ready")
            return "Error: LLM service not available. Please check configuration."
        
        try:
            results = self.vector_store.search(question, top_k=self.top_k)
            
            if not results:
                logger.warning("No documents found for query")
                return "No documents found. Please upload documents first."
            
            context = "\n\n".join([f"[Document]\n{chunk}" for chunk, _, _ in results])
            context, truncated = self._truncate_context(context)
            if truncated:
                logger.debug(
                    "Context truncated to %s characters for simple answer flow",
                    self.context_window_size
                )
            prompt = self._build_prompt(question, context)
            
            logger.debug(f"Generating answer for query: {question[:100]}...")
            answer = self.llm_engine.generate(
                prompt,
                max_tokens=settings.MAX_TOKENS,
                temperature=self.temperature
            )
            
            return answer
        except Exception as e:
            logger.error(f"Error answering query: {e}", exc_info=True)
            return f"Error processing query: {str(e)}"
    
    def _retrieve_context_with_fallback(self, question: str, document_filter: Optional[List[str]] = None) -> Tuple[List[Tuple[str, float, dict]], float]:
        """
        Retrieve context with enhanced search capabilities and fallback mechanism.
        Uses dynamic multi-document detection based on actual search results.
        
        Args:
            question: Question to search for
            document_filter: Optional list of document names to search within
            
        Returns:
            Tuple of (results with metadata, average_similarity)
        """
        logger.info(f"Retrieving context with enhanced search: top_k={self.top_k}, hybrid={self.enable_hybrid_search}")
        
        # Step 0: Detect if this is a table/aggregation query
        query_type = self._detect_query_type(question)
        logger.info(f"Query type detected: {query_type}")
        
        # Step 1: Always do initial broad search to understand document landscape
        if self.enable_hybrid_search:
            initial_results = self._hybrid_search(question, self.top_k * 2)
        else:
            initial_results = self.vector_store.search(question, top_k=self.top_k * 2)
        
        if not initial_results:
            logger.warning("No results found in initial retrieval")
            return [], 0.0
        
        # Step 1.5: For aggregation queries on tables, retrieve ALL chunks from the document
        if query_type == "aggregation":
            # Get the most relevant document from initial results
            doc_relevance = self._analyze_document_relevance(initial_results)
            if doc_relevance:
                # Find document with highest average score
                best_doc = max(doc_relevance.items(), key=lambda x: sum(x[1]) / len(x[1]))[0]
                
                # Check if this looks like structured data (table/Excel)
                if self._is_structured_document(best_doc, initial_results):
                    logger.info(f"🔢 TABLE-AWARE: Aggregation query detected on structured document '{best_doc}'")
                    logger.info(f"🔢 TABLE-AWARE: Retrieving ALL chunks from '{best_doc}' for complete calculation")
                    
                    # Retrieve all chunks from this document
                    all_chunks = self.vector_store.get_all_chunks_by_document(best_doc)
                    
                    if all_chunks:
                        logger.info(f"🔢 TABLE-AWARE: Retrieved {len(all_chunks)} chunks for complete table processing")
                        return all_chunks, 1.0  # Return all chunks with high confidence
        
        # Step 2: Analyze which documents are relevant (dynamic detection)
        doc_relevance = self._analyze_document_relevance(initial_results)
        num_relevant_docs = len([d for d, scores in doc_relevance.items() if max(scores) > 0.5])
        
        logger.info(f"Document relevance analysis: {len(doc_relevance)} docs found, {num_relevant_docs} highly relevant")
        
        # Step 3: Choose strategy based on document distribution
        if document_filter:
            # User specified documents - filter results
            results = self._document_specific_search(question, document_filter, self.top_k)
        elif num_relevant_docs > 1:
            # Multi-document query detected dynamically - ensure diversity
            results = self._ensure_document_diversity(initial_results, self.top_k)
            logger.info(f"Multi-document query: Ensuring diversity across {num_relevant_docs} documents")
        else:
            # Single document focus - use standard results
            results = initial_results[:self.top_k]
        
        if not results:
            return [], 0.0
            
        similarities = [sim for _, sim, _ in results]
        avg_similarity = sum(similarities) / len(similarities)
        logger.info(f"Enhanced retrieval: {len(results)} results, avg_similarity: {avg_similarity:.4f}")
        
        # Fallback mechanism for low-similarity results
        if avg_similarity < self.min_similarity_threshold and len(results) < 20:
            logger.info(f"Average similarity ({avg_similarity:.4f}) below threshold. Retrieving more chunks...")
            
            if self.enable_hybrid_search:
                more_results = self._hybrid_search(question, min(self.top_k * 2, 20))
            else:
                more_results = self.vector_store.search(question, top_k=min(self.top_k * 2, 20))
                
            if more_results:
                results = sorted(more_results, key=lambda x: x[1], reverse=True)[:self.top_k + 5]
                similarities = [sim for _, sim, _ in results]
                avg_similarity = sum(similarities) / len(similarities)
                logger.info(f"Fallback retrieval: {len(results)} results, avg_similarity: {avg_similarity:.4f}")
        
        return results, avg_similarity

    def _is_structured_document(self, doc_name: str, sample_results: List[Tuple[str, float, dict]]) -> bool:
        """
        Determine if a document contains structured data (tables).
        
        Args:
            doc_name: Document name to check
            sample_results: Sample results to analyze content
            
        Returns:
            True if document appears to be structured/tabular
        """
        # Check file extension
        doc_lower = doc_name.lower()
        if any(ext in doc_lower for ext in ['.xlsx', '.xls', '.csv', '.tsv']):
            return True
        
        # Check content patterns - look for table indicators
        table_indicators = ['===', '|', '[R', 'row', 'column', 'sheet:', 'table']
        
        for chunk, _, metadata in sample_results:
            if self._extract_document_name(metadata) == doc_name:
                chunk_lower = chunk.lower()
                # If chunk has multiple table indicators, likely structured
                indicator_count = sum(1 for indicator in table_indicators if indicator in chunk_lower)
                if indicator_count >= 2:
                    return True
                
                # Check for pipe-separated or bracket-notation rows
                if '|' in chunk and chunk.count('|') > 5:
                    return True
                if '[R' in chunk and ']' in chunk:  # Row notation like [R1], [R2]
                    return True
        
        return False

    def _analyze_document_relevance(self, results: List[Tuple[str, float, dict]]) -> Dict[str, List[float]]:
        """
        Analyze which documents are relevant based on search results.
        Returns dict of document_name -> list of similarity scores.
        """
        doc_scores: Dict[str, List[float]] = {}
        
        for chunk, score, metadata in results:
            doc_name = self._extract_document_name(metadata)
            if doc_name not in doc_scores:
                doc_scores[doc_name] = []
            doc_scores[doc_name].append(score)
        
        return doc_scores

    def _ensure_document_diversity(self, results: List[Tuple[str, float, dict]], top_k: int) -> List[Tuple[str, float, dict]]:
        """
        Ensure results include chunks from multiple relevant documents.
        Uses round-robin selection to maintain diversity while respecting relevance.
        """
        # Group by document
        doc_chunks: Dict[str, List[Tuple[str, float, dict]]] = {}
        for chunk, score, metadata in results:
            doc_name = self._extract_document_name(metadata)
            if doc_name not in doc_chunks:
                doc_chunks[doc_name] = []
            doc_chunks[doc_name].append((chunk, score, metadata))
        
        # Sort each document's chunks by score
        for doc_name in doc_chunks:
            doc_chunks[doc_name].sort(key=lambda x: x[1], reverse=True)
        
        # Round-robin selection ensuring diversity
        diverse_results = []
        doc_indices = {doc: 0 for doc in doc_chunks}
        docs = list(doc_chunks.keys())
        
        while len(diverse_results) < top_k and any(doc_indices[d] < len(doc_chunks[d]) for d in docs):
            for doc_name in docs:
                if len(diverse_results) >= top_k:
                    break
                idx = doc_indices[doc_name]
                if idx < len(doc_chunks[doc_name]):
                    diverse_results.append(doc_chunks[doc_name][idx])
                    doc_indices[doc_name] += 1
        
        # Final sort by score while maintaining some diversity
        diverse_results.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Document diversity: Selected {len(diverse_results)} chunks from {len(docs)} documents")
        return diverse_results
    
    def _detect_query_type(self, question: str) -> str:
        """Detect the type of query to optimize search strategy."""
        question_lower = question.lower()
        
        # Table/Aggregation queries (needs complete table data)
        aggregation_indicators = [
            'total', 'sum', 'count', 'average', 'mean', 'max', 'maximum', 'min', 'minimum',
            'all', 'every', 'complete', 'entire', 'full list', 'how many', 'calculate',
            'aggregate', 'group by', 'breakdown', 'distribution', 'statistics', 'stats'
        ]
        
        if any(indicator in question_lower for indicator in aggregation_indicators):
            return "aggregation"
        
        # Comparative queries (explicit comparison language)
        comparative_indicators = [
            'compare', 'comparison', 'versus', 'vs', 'difference', 'differences',
            'contrast', 'similar', 'different', 'better', 'worse', 'advantages',
            'disadvantages', 'pros', 'cons', 'between', 'against'
        ]
        
        if any(indicator in question_lower for indicator in comparative_indicators):
            return "comparative"
        
        # Summary queries
        summary_indicators = [
            'summarize', 'summary', 'overview', 'main points', 'key points',
            'highlights', 'conclusions', 'findings', 'results'
        ]
        
        if any(indicator in question_lower for indicator in summary_indicators):
            return "summary"
        
        # Specific fact queries
        fact_indicators = [
            'what is', 'who is', 'when', 'where', 'how many', 'define',
            'definition', 'explain', 'meaning'
        ]
        
        if any(indicator in question_lower for indicator in fact_indicators):
            return "factual"
        
        # Process/how-to queries
        process_indicators = [
            'how to', 'steps', 'process', 'procedure', 'method', 'way to',
            'approach', 'technique'
        ]
        
        if any(indicator in question_lower for indicator in process_indicators):
            return "process"
        
        return "general"
    
    def _calculate_table_aggregation(self, question: str, results: List[Tuple[str, float, dict]]) -> Optional[Dict[str, Any]]:
        """
        Calculate aggregation directly from table data.
        
        Args:
            question: User question containing aggregation request
            results: Retrieved chunks with table data
            
        Returns:
            Dict with 'value', 'count', 'summary' or None if calculation fails
        """
        question_lower = question.lower()
        
        # Detect filter criteria (e.g., "for New York", "where City = Chicago")
        filter_value = None
        filter_patterns = [
            r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # "for New York"
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',   # "in Chicago"
            r'where.*?=\s*["\']?([^"\']+)["\']?',       # "where City = 'New York'"
        ]
        
        for pattern in filter_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                filter_value = match.group(1).strip()
                break
        
        if not filter_value:
            logger.warning("TABLE-CALC: No filter value detected in question")
            return None
        
        logger.info(f"TABLE-CALC: Filter detected: '{filter_value}'")
        
        # Detect aggregation type and target column
        agg_type = "sum"  # default
        if any(w in question_lower for w in ['average', 'mean', 'avg']):
            agg_type = "average"
        elif any(w in question_lower for w in ['count', 'how many']):
            agg_type = "count"
        elif any(w in question_lower for w in ['max', 'maximum', 'highest']):
            agg_type = "max"
        elif any(w in question_lower for w in ['min', 'minimum', 'lowest']):
            agg_type = "min"
        
        # Detect target column from question
        target_column = None
        column_keywords = ['sales', 'calls', 'amount', 'quantity', 'hours', 'score', 'total', 'revenue']
        for kw in column_keywords:
            if kw in question_lower:
                target_column = kw
                break
        
        if not target_column:
            target_column = "sales"  # default
        
        logger.info(f"TABLE-CALC: Aggregation type='{agg_type}', column='{target_column}'")
        
        # Find column index from header
        column_index = None
        header_line = None
        for chunk, _, _ in results:
            if '[Columns:' in chunk or 'Columns:' in chunk:
                for line in chunk.split('\n'):
                    if 'Columns:' in line:
                        header_line = line
                        # Parse columns
                        parts = line.replace('[Columns:', '').replace('Columns:', '').strip().rstrip(']').split('|')
                        for i, col in enumerate(parts):
                            if target_column.lower() in col.lower().strip():
                                column_index = i
                                break
                        break
                if column_index is not None:
                    break
        
        if column_index is None:
            logger.warning(f"TABLE-CALC: Column '{target_column}' not found in headers")
            return None
        
        logger.info(f"TABLE-CALC: Found column '{target_column}' at index {column_index}")
        
        # Extract matching rows and values
        values = []
        matching_rows = []
        seen_row_ids = set()
        
        for chunk, _, _ in results:
            lines = chunk.split('\n')
            for line in lines:
                if filter_value in line and line.startswith('[R'):
                    # Extract row ID to avoid duplicates from chunk overlap
                    row_id = line.split(']')[0] + ']'
                    if row_id in seen_row_ids:
                        continue
                    seen_row_ids.add(row_id)
                    
                    # Extract value from target column
                    parts = line.split('|')
                    if len(parts) > column_index:
                        try:
                            # First part may contain [R#] ID, so column_index might be off by 1
                            # The actual data starts after [R#] in first cell
                            val_str = parts[column_index].strip()
                            val = float(val_str)
                            values.append(val)
                            matching_rows.append(line.strip())
                        except (ValueError, IndexError):
                            pass
        
        if not values:
            logger.warning(f"TABLE-CALC: No values found for filter '{filter_value}'")
            return None
        
        # Calculate result
        if agg_type == "sum":
            result_value = sum(values)
        elif agg_type == "average":
            result_value = sum(values) / len(values)
        elif agg_type == "count":
            result_value = len(values)
        elif agg_type == "max":
            result_value = max(values)
        elif agg_type == "min":
            result_value = min(values)
        else:
            result_value = sum(values)
        
        # Format result
        if agg_type in ["sum", "max", "min"] and result_value == int(result_value):
            result_value = int(result_value)
        
        summary = f"""
Found {len(values)} rows matching '{filter_value}'.
Column: {target_column.title()} (position {column_index + 1})
{agg_type.title()} calculation: {' + '.join(str(int(v)) for v in values[:10])}{'...' if len(values) > 10 else ''} = {result_value}

Sample matching rows:
{chr(10).join(matching_rows[:5])}
{'...' if len(matching_rows) > 5 else ''}

ANSWER: The {agg_type} of {target_column} for {filter_value} is {result_value} (based on {len(values)} rows)
"""
        
        logger.info(f"TABLE-CALC: Result = {result_value} from {len(values)} values")
        
        return {
            "value": result_value,
            "count": len(values),
            "agg_type": agg_type,
            "column": target_column,
            "filter": filter_value,
            "summary": summary.strip()
        }

    def answer_query_with_context(self, question: str) -> Dict[str, Any]:
        """
        Answer query and return context and sources with comprehensive logging.
        
        Args:
            question: Question to answer
            
        Returns:
            Dictionary with answer, context, and sources
        """
        logger.info(f"=== Starting RAG query flow for: {question[:100]}... ===")
        
        # Step 1: Validate question
        if not question or not question.strip():
            logger.warning("RAG STEP 1 FAILED: Empty question provided")
            return {
                "answer": "Please provide a valid question.",
                "context": "",
                "sources": []
            }
        logger.info(f"RAG STEP 1 COMPLETE: Question validated ({len(question)} chars)")
        
        # Step 2: Validate LLM engine
        if not self.llm_engine.is_ready():
            logger.error("RAG STEP 2 FAILED: LLM engine not ready")
            return {
                "answer": "Error: LLM service not available. Please check configuration.",
                "context": "",
                "sources": [],
                "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": ["LLM service not available"]}
            }
        logger.info("RAG STEP 2 COMPLETE: LLM engine validated")
        
        # Step 3: Search vector store with fallback
        try:
            logger.info(f"RAG STEP 3: Searching vector store with fallback mechanism")
            results, avg_similarity = self._retrieve_context_with_fallback(question)
            
            # Enhanced debug logging for search results
            logger.info(f"RAG DEBUG: Search results details:")
            for i, (chunk, sim, meta) in enumerate(results[:3], 1):
                doc_name = meta.get('source_doc', 'unknown') if meta else 'unknown'
                logger.info(f"  Result {i}: similarity={sim:.4f}, doc={doc_name}, chunk_len={len(chunk)}")
            logger.info(f"RAG DEBUG: avg_similarity={avg_similarity:.4f}, threshold={self.min_similarity_threshold}")
            
            if not results:
                logger.warning("RAG STEP 3 FAILED: No documents found for query")
                return {
                    "answer": "No documents found. Please upload documents first.",
                    "context": "",
                    "sources": [],
                    "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": ["No documents available"]}
                }
            logger.info(f"RAG STEP 3 COMPLETE: Found {len(results)} relevant chunk(s), avg_similarity: {avg_similarity:.4f}")
        except Exception as e:
            logger.error(f"RAG STEP 3 FAILED: Error searching vector store: {e}", exc_info=True)
            return {
                "answer": f"Error searching documents: {str(e)}",
                "context": "",
                "sources": [],
                "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": [f"Search error: {str(e)}"]}
            }
        
        # Step 4: Build context and sources with metadata backtracking
        try:
            logger.info("RAG STEP 4: Building context and sources with metadata")
            context_parts = []
            sources = []
            
            truncated = False
            
            # Check if this is an aggregation query on structured data
            query_type = self._detect_query_type(question)
            is_table_aggregation = query_type == "aggregation" and avg_similarity >= 0.9 and len(results) > 20
            
            # For table aggregation, calculate programmatically
            if is_table_aggregation:
                logger.info("🔢 TABLE-AWARE: Calculating aggregation programmatically")
                calc_result = self._calculate_table_aggregation(question, results)
                
                if calc_result:
                    # Use calculated result instead of sending all data to LLM
                    for i, (chunk, similarity, metadata) in enumerate(results[:5], 1):  # Only first 5 as samples
                        doc_name = self._extract_document_name(metadata)
                        context_parts.append(f"📄 Document: {doc_name} (Relevance: {similarity:.1%})\n\n{chunk[:500]}...")
                        source_entry = self._format_source_entry(i, chunk, similarity, metadata)
                        source_entry['document_name'] = doc_name
                        sources.append(source_entry)
                    
                    # Add calculation summary to context
                    context = "\n\n".join(context_parts)
                    context += f"\n\n📊 PRE-CALCULATED RESULT:\n{calc_result['summary']}"
                    
                    logger.info(f"🔢 TABLE-AWARE: Calculation complete - {calc_result['summary'][:100]}")
                else:
                    # Fallback to normal context building
                    is_table_aggregation = False

            if not is_table_aggregation:
                for i, (chunk, similarity, metadata) in enumerate(results, 1):
                    # Extract actual document name from metadata
                    doc_name = self._extract_document_name(metadata)
                    
                    # Use full chunk content for LLM context (not truncated preview)
                    context_parts.append(f"📄 Document: {doc_name} (Relevance: {similarity:.1%})\n\n{chunk}")
                    
                    # Create enhanced source entry
                    source_entry = self._format_source_entry(i, chunk, similarity, metadata)
                    source_entry['document_name'] = doc_name
                    source_entry['formatted_preview'] = f"{chunk[:200]}{'...' if len(chunk) > 200 else ''}"
                    sources.append(source_entry)
                
                context = "\n\n".join(context_parts)
                context, truncated = self._truncate_context(context)
                if truncated:
                    logger.info(
                        "RAG STEP 4 NOTE: Context truncated to %s characters per context window",
                        self.context_window_size
                    )
            
            logger.info(f"RAG STEP 4 COMPLETE: Context built ({len(context)} chars, {len(sources)} sources with metadata)")
        except Exception as e:
            logger.error(f"RAG STEP 4 FAILED: Error building context: {e}", exc_info=True)
            return {
                "answer": f"Error building context: {str(e)}",
                "context": "",
                "sources": [],
                "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": [f"Context error: {str(e)}"]}
            }
        
        # Step 5: Build prompt
        try:
            logger.info("RAG STEP 5: Building prompt")
            prompt = self._build_prompt(question, context, avg_similarity)
            logger.info(f"RAG STEP 5 COMPLETE: Prompt built ({len(prompt)} chars)")
        except Exception as e:
            logger.error(f"RAG STEP 5 FAILED: Error building prompt: {e}", exc_info=True)
            return {
                "answer": f"Error building prompt: {str(e)}",
                "context": context,
                "sources": sources,
                "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": [f"Prompt error: {str(e)}"]}
            }
        
        # Step 6: Generate answer
        try:
            logger.info(f"RAG STEP 6: Generating answer (max_tokens={settings.MAX_TOKENS}, temperature={self.temperature})")
            answer = self.llm_engine.generate(
                prompt,
                max_tokens=settings.MAX_TOKENS,
                temperature=self.temperature
            )
            
            if answer:
                logger.info(f"RAG STEP 6 COMPLETE: Answer generated ({len(answer)} chars)")
                
                # Step 7: Verify answer with metadata
                logger.info("RAG STEP 7: Verifying answer with metadata")
                verification = self._verify_answer_with_metadata(answer, sources, question)
                logger.info(f"RAG STEP 7 COMPLETE: Verification score={verification['confidence_score']:.3f}")
                
                logger.info(f"=== RAG query flow COMPLETE ===\nVerification: {verification['is_verified']}, Confidence: {verification['confidence_score']:.3f}")
                return {
                    "answer": answer,
                    "context": context,
                    "sources": sources,
                    "verification": verification
                }
            else:
                logger.warning("RAG STEP 6 FAILED: Empty answer generated")
                return {
                    "answer": "Error: Empty response from LLM.",
                    "context": context,
                    "sources": sources,
                    "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": ["Empty response generated"]}
                }
        except Exception as e:
            logger.error(f"RAG STEP 6 FAILED: Error generating answer: {e}", exc_info=True)
            return {
                "answer": f"Error processing query: {str(e)}",
                "context": context,
                "sources": sources,
                "verification": {"is_verified": False, "confidence_score": 0.0, "recommendations": [f"Generation error: {str(e)}"]}
            }
    
    def _build_prompt(self, question: str, context: str, avg_similarity: float = 1.0) -> str:
        """
        Build RAG prompt from question and context with adaptive instructions.
        
        Args:
            question: User question
            context: Retrieved context chunks
            avg_similarity: Average similarity score of retrieved chunks
            
        Returns:
            Formatted prompt string
        """
        if avg_similarity >= 0.7:
            confidence_instruction = "The context is highly relevant to the question."
        elif avg_similarity >= 0.5:
            confidence_instruction = "The context is moderately relevant to the question. Try to extract relevant information even if not perfectly matching."
        else:
            confidence_instruction = "The context may have partial relevance. Please provide the best answer possible based on available information, and clarify what information was not found."
        
        # Detect if this is an aggregation/calculation query
        question_lower = question.lower()
        aggregation_keywords = ['total', 'sum', 'count', 'average', 'mean', 'max', 'min', 'how many', 'calculate']
        is_aggregation = any(kw in question_lower for kw in aggregation_keywords)
        
        if is_aggregation:
            calculation_instruction = """
IMPORTANT - CALCULATION REQUIRED:
This question requires a numerical calculation. You MUST:
1. First identify which column contains the values to aggregate (look for "Columns:" header line that shows: "A:Name | B:ID | E:Sales..." etc.)
2. Find ALL rows that match the filter criteria (e.g., all rows where City = "New York")
3. DO NOT skip or deduplicate rows - count EVERY matching row even if values repeat
4. Extract the numeric value from the CORRECT column for EACH matching row
5. Add up ALL values: value1 + value2 + value3 + ... = TOTAL
6. Show your complete calculation with all values
7. State how many rows were included

CRITICAL: 
- Some rows may appear in multiple chunks due to overlap - count each UNIQUE row ID only once (e.g., [R2], [R8] are different rows)
- The Sales column is typically column E or F (check the Columns header)
- Include ALL rows, not just a sample

Format your answer as:
"Found X rows for [criteria]. 
Sales values: [list all values]
Calculation: sum of all values = TOTAL
Answer: The total [metric] for [criteria] is TOTAL"
"""
        else:
            calculation_instruction = ""
        
        prompt = f"""You are an expert document analysis assistant. Your task is to answer questions based on provided document context with high accuracy and clarity.

{confidence_instruction}
{calculation_instruction}

Document Context:
{context}

User Question: {question}

Critical Instructions:
1. ALWAYS answer based ONLY on the context provided - do not use external knowledge
2. If the context directly answers the question, provide a complete and detailed response with specific examples
3. Structure your answer with clear bullet points or numbered lists when appropriate
4. Include relevant quotes or specific details from the context to support your answer
5. If information is partially available, clearly state what you found and what specific information is missing
6. If no relevant information is found, state "I cannot find information about this question in the provided documents."
7. When the context contains conditions, requirements, or step-by-step processes, present them clearly in your answer
8. Reference specific document sections or pages when available in the metadata
9. IMPORTANT: When the question involves multiple topics (e.g., loans AND notice period), synthesize information from ALL relevant document sections provided
10. Look for both direct answers AND related policies that may apply to the situation

Provide a comprehensive and well-structured answer:

Answer:"""
        return prompt
    
    def set_top_k(self, top_k: int) -> None:
        """
        Set retrieval parameter.
        
        Args:
            top_k: Number of chunks to retrieve
        """
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        self.top_k = top_k
        logger.debug(f"Set top_k to {top_k}")
    
    def set_temperature(self, temp: float) -> None:
        """
        Set generation parameter.
        
        Args:
            temp: Temperature value (0.0 to 2.0)
        """
        if not (0.0 <= temp <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        self.temperature = temp
        logger.debug(f"Set temperature to {temp}")
    
    def set_context_window_size(self, size: int) -> None:
        """Update the context window limit."""
        if size <= 0:
            raise ValueError("context_window_size must be positive")
        self.context_window_size = size
        logger.debug(f"Set context_window_size to {size}")

    def _truncate_context(self, context: str) -> Tuple[str, bool]:
        """Trim context to configured window, preserving document boundaries when possible."""
        if not self.context_window_size or self.context_window_size <= 0:
            return context, False
        if len(context) <= self.context_window_size:
            return context, False

        indicator = "\n\n[Context truncated]"
        limit = max(0, self.context_window_size - len(indicator))
        if limit <= 0:
            return indicator[: self.context_window_size], True

        trunc_point = context.rfind("\n\n", 0, limit)
        if trunc_point == -1:
            trunc_point = limit

        trimmed = context[:trunc_point].rstrip()
        if len(trimmed) + len(indicator) > self.context_window_size:
            trimmed = trimmed[: self.context_window_size - len(indicator)]

        return f"{trimmed}{indicator}", True

    def get_documents_by_source(self) -> Dict[str, int]:
        """
        Get list of all source documents and chunk counts for backtracking.
        
        Returns:
            Dictionary mapping source_doc name to chunk count
        """
        doc_counts = {}
        if hasattr(self.vector_store, 'metadata'):
            for meta in self.vector_store.metadata:
                source = meta.get("source_doc", "unknown")
                doc_counts[source] = doc_counts.get(source, 0) + 1
        logger.debug(f"Document sources: {doc_counts}")
        return doc_counts
    
    def search_by_document(self, source_doc: str) -> Dict[str, Any]:
        """
        Get all chunks from a specific source document.
        
        Args:
            source_doc: Name of the source document
            
        Returns:
            Dictionary with document info and chunks
        """
        chunks_in_doc = []
        if hasattr(self.vector_store, 'metadata'):
            for i, meta in enumerate(self.vector_store.metadata):
                if meta.get("source_doc") == source_doc:
                    chunks_in_doc.append({
                        "chunk_index": i,
                        "chunk": self.vector_store.chunks[i],
                        "length": len(self.vector_store.chunks[i])
                    })
        logger.info(f"Retrieved {len(chunks_in_doc)} chunks from document '{source_doc}'")
        return {
            "source_doc": source_doc,
            "total_chunks": len(chunks_in_doc),
            "chunks": chunks_in_doc
        }
    
    def _verify_answer_with_metadata(self, answer: str, sources: List[Dict], question: str) -> Dict[str, Any]:
        """
        Verify answer quality using metadata and source analysis.
        
        Args:
            answer: Generated answer
            sources: List of source chunks with metadata
            question: Original question
            
        Returns:
            Verification results with confidence score and recommendations
        """
        verification = {
            "is_verified": False,
            "confidence_score": 0.0,
            "source_coverage": {},
            "recommendations": [],
            "metadata_analysis": {}
        }
        
        if not sources or not answer or answer.strip() in ["I cannot find information about this question in the provided documents.", "No documents found. Please upload documents first."]:
            verification["recommendations"].append("No valid sources or answer to verify")
            return verification
        
        try:
            # Analyze source distribution
            source_docs = {}
            total_similarity = 0.0
            high_similarity_count = 0
            
            for source in sources:
                similarity = source.get("similarity", 0.0)
                metadata = source.get("metadata", {})
                source_doc = metadata.get("source_doc", "unknown")
                
                total_similarity += similarity
                if similarity > 0.6:
                    high_similarity_count += 1
                
                if source_doc not in source_docs:
                    source_docs[source_doc] = {"count": 0, "avg_similarity": 0.0, "similarities": []}
                
                source_docs[source_doc]["count"] += 1
                source_docs[source_doc]["similarities"].append(similarity)
            
            # Calculate averages
            avg_similarity = total_similarity / len(sources) if sources else 0.0
            for doc, info in source_docs.items():
                info["avg_similarity"] = sum(info["similarities"]) / len(info["similarities"])
            
            # Determine confidence based on multiple factors
            confidence_score = 0.0
            
            # Factor 1: Average similarity (40% weight)
            if avg_similarity >= 0.8:
                confidence_score += 0.4
            elif avg_similarity >= 0.6:
                confidence_score += 0.3
            elif avg_similarity >= 0.4:
                confidence_score += 0.2
            elif avg_similarity >= 0.2:
                confidence_score += 0.1
            
            # Factor 2: Source diversity (20% weight)
            if len(source_docs) > 1:
                confidence_score += 0.2
            elif len(source_docs) == 1 and source_docs[list(source_docs.keys())[0]]["count"] > 2:
                confidence_score += 0.15
            
            # Factor 3: High similarity chunks (20% weight)
            high_sim_ratio = high_similarity_count / len(sources)
            if high_sim_ratio >= 0.5:
                confidence_score += 0.2
            elif high_sim_ratio >= 0.3:
                confidence_score += 0.15
            elif high_sim_ratio >= 0.1:
                confidence_score += 0.1
            
            # Factor 4: Answer completeness (20% weight)
            if len(answer.strip()) > 100 and not any(phrase in answer.lower() for phrase in ["cannot find", "not found", "no information", "error"]):
                confidence_score += 0.2
            elif len(answer.strip()) > 50:
                confidence_score += 0.1
            
            verification["confidence_score"] = confidence_score
            verification["is_verified"] = confidence_score >= 0.6
            verification["source_coverage"] = source_docs
            verification["metadata_analysis"] = {
                "total_sources": len(sources),
                "unique_documents": len(source_docs),
                "avg_similarity": avg_similarity,
                "high_similarity_count": high_similarity_count,
                "answer_length": len(answer.strip())
            }
            
            # Generate recommendations
            if confidence_score < 0.4:
                verification["recommendations"].append("Low confidence - consider rephrasing question or uploading more relevant documents")
            if avg_similarity < 0.3:
                verification["recommendations"].append("Low similarity scores - question may not match document content")
            if len(source_docs) == 1 and source_docs[list(source_docs.keys())[0]]["count"] == 1:
                verification["recommendations"].append("Answer based on single source - consider cross-referencing")
            if high_similarity_count == 0:
                verification["recommendations"].append("No high-similarity matches found - answer may be speculative")
            
            if confidence_score >= 0.8:
                verification["recommendations"].append("High confidence answer with good source coverage")
            elif confidence_score >= 0.6:
                verification["recommendations"].append("Moderate confidence answer - sources support the response")
                
            logger.info(f"Answer verification: confidence={confidence_score:.3f}, verified={verification['is_verified']}")
            
        except Exception as e:
            logger.error(f"Error during answer verification: {e}", exc_info=True)
            verification["recommendations"].append(f"Verification error: {str(e)}")
        
        return verification

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "llm_ready": self.llm_engine.is_ready() if self.llm_engine else False,
            "top_k": self.top_k,
            "temperature": self.temperature,
            "context_window_size": self.context_window_size,
            "vector_store_chunks": len(self.vector_store.chunks) if self.vector_store else 0,
            "source_documents": self.get_documents_by_source()
        }
