"""
Tracked RAG Chat Service with Full Opik Pipeline Visibility
============================================================

This service provides complete observability for the RAG pipeline:

User Query
   ↓
[OPIK] rag_pipeline (main trace)
   ├── query_preprocessing
   ├── document_retrieval
   ├── context_reranking  
   ├── context_building
   ├── llm_generation (auto-tracked via LiteLLM)
   └── response_formatting

All operations appear as nested spans in Opik dashboard.
"""

import time
import os
from typing import List, Dict, Any, Optional

from ..logger_config import logger
from ..config import settings
from ..opik_config import get_opik_manager, initialize_opik

# Set project name and Groq API key for LiteLLM
os.environ["OPIK_PROJECT_NAME"] = os.getenv("OPIK_PROJECT_NAME", "rag-system")
if settings.GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

# Initialize LiteLLM with Opik integration (with fallback)
LITELLM_AVAILABLE = False
try:
    import litellm
    from litellm.integrations.opik.opik import OpikLogger
    from opik import track
    from opik.opik_context import get_current_span_data
    
    # Initialize Opik logger for LiteLLM - this auto-tracks all LLM calls
    opik_logger = OpikLogger()
    litellm.callbacks = [opik_logger]
    LITELLM_AVAILABLE = True
    logger.info("TrackedRAGService: LiteLLM + Opik integration initialized")
except Exception as e:
    logger.warning(f"TrackedRAGService: LiteLLM integration failed, using fallback: {e}")
    # Fallback track decorator
    def track(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def get_current_span_data():
        return None


class TrackedRAGService:
    """
    RAG service with full Opik tracing using @track decorators.
    
    Every step of the RAG pipeline is traced as nested spans:
    - Query preprocessing
    - Document retrieval (vector search)
    - Context reranking
    - Context assembly
    - LLM generation (auto-tracked)
    - Response formatting
    """
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        self.opik_manager = get_opik_manager()
        
        # LiteLLM model for Groq
        self.litellm_model = f"groq/{settings.LLM_MODEL}"
        
        logger.info(f"TrackedRAGService initialized with Opik: {self.opik_manager.available}")
        logger.info(f"LiteLLM model: {self.litellm_model}")
    
    @track(name="rag_pipeline", tags=["rag", "production", "pipeline"])
    async def process_query(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main RAG pipeline with full Opik tracing.
        
        Each step creates a nested span visible in Opik dashboard.
        """
        start_time = time.time()
        
        try:
            # Step 1: Preprocess query
            processed_query = self._preprocess_query(query)
            
            # Step 2: Retrieve documents
            retrieval_result = self._retrieve_documents(processed_query, top_k)
            
            if not retrieval_result["chunks"]:
                return self._format_empty_response(query, time.time() - start_time)
            
            # Step 3: Rerank and filter chunks
            reranked = self._rerank_chunks(
                retrieval_result["chunks"],
                retrieval_result["metadata"],
                query
            )
            
            # Step 4: Build context
            context = self._build_context(reranked["chunks"], reranked["metadata"])
            
            # Step 5: Generate answer with LLM (auto-tracked by LiteLLM + OpikLogger)
            answer, generation_metrics = self._generate_answer(
                query=query,
                context=context,
                temperature=temperature
            )
            
            # Step 6: Format response
            response = self._format_response(
                query=query,
                answer=answer,
                sources=reranked["metadata"],
                confidence=retrieval_result["confidence"],
                metrics={
                    "processing_time": time.time() - start_time,
                    "chunks_retrieved": len(retrieval_result["chunks"]),
                    "chunks_used": len(reranked["chunks"]),
                    **generation_metrics
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"RAG Pipeline error: {e}", exc_info=True)
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "processing_time": time.time() - start_time
            }
    
    @track(name="query_preprocessing", tags=["preprocessing", "nlp"])
    def _preprocess_query(self, query: str) -> str:
        """Preprocess and expand query for better retrieval."""
        start = time.time()
        
        # Use RAG engine's preprocessing
        processed = self.rag_engine._preprocess_query(query)
        
        logger.debug(f"Query preprocessed in {time.time() - start:.3f}s")
        return processed
    
    @track(name="document_retrieval", tags=["retrieval", "vectorstore", "faiss"])
    def _retrieve_documents(self, query: str, top_k: int) -> Dict[str, Any]:
        """Retrieve relevant document chunks using vector search."""
        start = time.time()
        
        # Get vectorstore size for context
        vectorstore_size = len(self.rag_engine.vector_store.chunks)
        
        # Perform retrieval using RAG engine
        results = self.rag_engine.retrieve_context(query, top_k=top_k)
        
        duration = time.time() - start
        
        # Extract document statistics
        doc_names = list(set([
            meta.get("document_name", "unknown")
            for meta in results.get("metadata", [])
        ]))
        
        logger.info(
            f"Retrieved {len(results.get('chunks', []))} chunks from "
            f"{len(doc_names)} documents in {duration:.2f}s"
        )
        
        return results
    
    @track(name="context_reranking", tags=["reranking", "filtering"])
    def _rerank_chunks(
        self,
        chunks: List[str],
        metadata: List[Dict],
        query: str
    ) -> Dict[str, Any]:
        """Rerank and filter chunks based on relevance."""
        start = time.time()
        
        # Filter based on minimum similarity threshold
        threshold = self.rag_engine.min_similarity_threshold
        
        filtered_chunks = []
        filtered_metadata = []
        
        for chunk, meta in zip(chunks, metadata):
            score = meta.get("relevance_score", 0)
            if score >= threshold:
                filtered_chunks.append(chunk)
                filtered_metadata.append(meta)
        
        duration = time.time() - start
        
        logger.debug(
            f"Reranking: {len(chunks)} -> {len(filtered_chunks)} chunks "
            f"(threshold={threshold}) in {duration:.3f}s"
        )
        
        return {
            "chunks": filtered_chunks,
            "metadata": filtered_metadata,
            "filtered_count": len(chunks) - len(filtered_chunks)
        }
    
    @track(name="context_building", tags=["context", "assembly"])
    def _build_context(self, chunks: List[str], metadata: List[Dict]) -> str:
        """Assemble chunks into context string."""
        start = time.time()
        
        # Build context with document attribution
        context_parts = []
        for chunk, meta in zip(chunks, metadata):
            doc_name = meta.get("document_name", "Unknown")
            context_parts.append(f"📄 Source: {doc_name}\n{chunk}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Truncate if needed
        context, truncated = self.rag_engine._truncate_context(context)
        
        duration = time.time() - start
        
        logger.debug(
            f"Built context: {len(context)} chars from {len(chunks)} chunks "
            f"(truncated={truncated}) in {duration:.3f}s"
        )
        
        return context
    
    @track(name="llm_generation", tags=["generation", "llm", "groq"])
    def _generate_answer(
        self,
        query: str,
        context: str,
        temperature: float
    ) -> tuple:
        """
        Generate answer using LLM.
        
        The actual LLM call is automatically traced by LiteLLM + OpikLogger
        as a child span with full token/cost tracking.
        """
        start = time.time()
        
        # Build prompt
        prompt = self.rag_engine._build_prompt(query, context, avg_similarity=0.8)
        
        try:
            if LITELLM_AVAILABLE:
                # Get current span data for linking
                current_span = get_current_span_data()
                
                # Make LLM call via LiteLLM - automatically traced with tokens/cost
                response = litellm.completion(
                    model=self.litellm_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=settings.MAX_TOKENS,
                    temperature=temperature,
                    metadata={
                        "opik": {
                            "current_span_data": current_span,
                            "tags": ["rag-generation"]
                        }
                    }
                )
                
                answer = response.choices[0].message.content.strip()
                
                # Extract token usage
                usage = response.usage
                metrics = {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                    "generation_time": time.time() - start,
                    "model": self.litellm_model
                }
            else:
                # Fallback to direct LLM engine
                answer = self.rag_engine.llm_engine.generate(
                    prompt,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=temperature
                )
                metrics = {
                    "generation_time": time.time() - start,
                    "model": self.litellm_model,
                    "fallback": True
                }
            
            logger.info(
                f"Generated answer: {len(answer)} chars in {metrics['generation_time']:.2f}s"
            )
            
            return answer, metrics
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}", exc_info=True)
            return f"Error generating response: {str(e)}", {
                "error": str(e),
                "generation_time": time.time() - start
            }
    
    @track(name="response_formatting", tags=["formatting", "output"])
    def _format_response(
        self,
        query: str,
        answer: str,
        sources: List[Dict],
        confidence: float,
        metrics: Dict
    ) -> Dict[str, Any]:
        """Format the final response with all metadata."""
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "processing_time": metrics.get("processing_time", 0),
            "metrics": metrics
        }
    
    def _format_empty_response(self, query: str, processing_time: float) -> Dict[str, Any]:
        """Format response when no documents are found."""
        return {
            "answer": "I couldn't find relevant information in the documents. Please try rephrasing your question or upload relevant documents.",
            "sources": [],
            "confidence": 0.0,
            "processing_time": processing_time,
            "metrics": {
                "chunks_retrieved": 0,
                "chunks_used": 0
            }
        }


# Factory function
def get_tracked_rag_service(rag_engine) -> TrackedRAGService:
    """Create a tracked RAG service instance."""
    return TrackedRAGService(rag_engine)
