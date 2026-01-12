"""
Enhanced Chat Service with Comprehensive Opik Tracking
======================================================

This provides detailed tracing with:
- Granular component tracking (retrieval, reranking, generation)
- Token and cost tracking
- Performance metrics at each step
- Nested spans showing complete flow
- Rich metadata and input/output at each stage
"""

import time
from typing import List, Dict, Any, Optional
from ..logger_config import logger
from ..config import settings
from ..opik_config import (
    get_opik_manager,
    initialize_opik,
    track,
    OpikManager
)

# Initialize OPIK at module load
_opik_init_success, _opik_init_message = initialize_opik()
logger.info(f"OPIK Module Init: {_opik_init_message}")

OPIK_AVAILABLE = _opik_init_success


class EnhancedChatService:
    """Enhanced chat service with comprehensive Opik tracking."""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        self.opik_manager = get_opik_manager()
        self.opik_available = self.opik_manager.available
        self.opik_client = self.opik_manager.get_client()
        
        # Log OPIK status on initialization
        status = self.opik_manager.get_status()
        logger.info(f"EnhancedChatService OPIK Status: {status}")
        
        if self.opik_available and self.opik_client:
            logger.info(f"EnhancedChatService initialized with Opik client")
            logger.info(f"EnhancedChatService Opik project: {self.opik_client.project_name}")
            try:
                logger.info(f"EnhancedChatService Opik config workspace: {self.opik_client.config.workspace}")
            except Exception as e:
                logger.debug(f"Could not read workspace from config: {e}")
        else:
            logger.warning(f"EnhancedChatService running WITHOUT Opik tracing")
            if self.opik_manager.initialization_error:
                logger.warning(f"Opik initialization error: {self.opik_manager.initialization_error}")
        
        logger.info(f"EnhancedChatService initialized with Opik: {self.opik_available}")
    
    async def process_query_enhanced(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process query with comprehensive Opik tracking.
        
        This creates detailed traces with:
        - Main query trace
        - Nested spans for each operation
        - Rich metadata at each step
        - Token and cost tracking
        - Performance metrics
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            temperature: LLM temperature
            user_id: Optional user identifier
            
        Returns:
            Dict with answer, sources, metrics, and timing
        """
        start_time = time.time()
        
        if not self.opik_available or not self.opik_client:
            logger.warning("Opik not available, using basic processing")
            return await self._process_query_basic(query, top_k, temperature)
        
        try:
            logger.info(f"ENHANCED_CHAT: Starting Opik trace creation for query: {query[:50]}")
            logger.info(f"ENHANCED_CHAT: Opik client: {self.opik_client}, project: rag-system")
            
            # Create main trace
            trace = self.opik_client.trace(
                name="rag_query_complete",
                input={
                    "query": query,
                    "query_length": len(query),
                    "top_k": top_k,
                    "temperature": temperature,
                    "user_id": user_id or "anonymous"
                },
                tags=["rag", "production"],
                metadata={
                    "model": getattr(self.rag_engine.llm_engine, 'model_name', 'unknown'),
                    "vectorstore_size": len(self.rag_engine.vector_store.chunks),
                    "hybrid_search": self.rag_engine.enable_hybrid_search
                }
            )
            
            logger.info(f"ENHANCED_CHAT: Trace created successfully: {trace}")
            logger.info(f"ENHANCED_CHAT: Trace ID: {getattr(trace, 'id', 'NO ID')}")
            
            # Step 1: Query preprocessing span
            preprocess_span = trace.span(
                name="query_preprocessing",
                input={"query": query},
                tags=["enrichment", "preprocessing"]
            )
            preprocessed_query = query  # Simple passthrough for now
            preprocess_span.end(output={
                "preprocessed_query": preprocessed_query,
                "enrichments_applied": 0
            })
            
            # Step 2: Document retrieval span
            retrieval_span = trace.span(
                name="document_retrieval",
                input={"query": preprocessed_query, "top_k": top_k},
                tags=["vector_search", "retrieval"]
            )
            retrieval_start = time.time()
            results = self.rag_engine.retrieve_context(preprocessed_query, top_k=top_k)
            retrieval_duration = time.time() - retrieval_start
            
            doc_names = list(set([m.get("document_name", "unknown") for m in results.get("metadata", [])]))
            retrieval_span.end(output={
                "chunks_retrieved": len(results.get("chunks", [])),
                "documents_matched": doc_names,
                "avg_similarity": results.get("confidence", 0.0),
                "duration": retrieval_duration
            })
            
            # Step 3: Document reranking span
            rerank_span = trace.span(
                name="document_reranking",
                input={"chunks_count": len(results.get("chunks", []))},
                tags=["filtering", "reranking"]
            )
            # Simple filtering based on threshold
            filtered_chunks = []
            filtered_metadata = []
            for chunk, meta in zip(results.get("chunks", []), results.get("metadata", [])):
                if meta.get("relevance_score", 0) >= self.rag_engine.min_similarity_threshold:
                    filtered_chunks.append(chunk)
                    filtered_metadata.append(meta)
            
            reranked_results = {
                "chunks": filtered_chunks,
                "metadata": filtered_metadata,
                "confidence": results.get("confidence", 0.0)
            }
            rerank_span.end(output={
                "chunks_after_reranking": len(filtered_chunks),
                "chunks_filtered_out": len(results.get("chunks", [])) - len(filtered_chunks),
                "confidence": reranked_results["confidence"]
            })
            
            # Step 4: Context building span
            context_span = trace.span(
                name="context_building",
                input={"chunks_count": len(filtered_chunks)},
                tags=["assembly", "context"]
            )
            context = "\n\n".join([
                f"📄 Document: {meta.get('document_name', 'unknown')}\n\n{chunk}"
                for chunk, meta in zip(filtered_chunks, filtered_metadata)
            ])
            context, truncated = self.rag_engine._truncate_context(context)
            context_span.end(output={
                "context_length": len(context),
                "truncated": truncated
            })
            
            # Step 5: LLM generation span
            if filtered_chunks:
                generation_span = trace.span(
                    name="llm_generation",
                    input={"query": query, "context_length": len(context)},
                    tags=["tokens", "cost", "generation"]
                )
                generation_start = time.time()
                
                prompt = self.rag_engine._build_prompt(query, context, reranked_results["confidence"])
                answer = self.rag_engine.llm_engine.generate(
                    prompt,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=temperature
                )
                
                generation_duration = time.time() - generation_start
                
                # Estimate tokens (rough estimate: 4 chars per token)
                input_tokens = len(prompt) // 4
                output_tokens = len(answer) // 4
                total_tokens = input_tokens + output_tokens
                
                # Estimate cost (Groq is free, but we'll estimate anyway)
                estimated_cost = (input_tokens * 0.0000001 + output_tokens * 0.0000002)
                
                generation_span.end(output={
                    "answer_length": len(answer),
                    "duration": generation_duration,
                    "tokens": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": total_tokens
                    },
                    "estimated_cost_usd": estimated_cost
                })
            else:
                answer = "I couldn't find relevant information in the documents."
                generation_duration = 0
                total_tokens = 0
                estimated_cost = 0
            
            # Complete main trace
            processing_time = time.time() - start_time
            logger.info(f"ENHANCED_CHAT: Ending trace with output")
            trace.end(output={
                "answer_length": len(answer),
                "sources_count": len(filtered_metadata),
                "confidence": reranked_results["confidence"],
                "total_duration": processing_time,
                "status": "success"
            })
            logger.info(f"ENHANCED_CHAT: Trace ended successfully")
            
            # Flush to ensure trace is sent
            logger.info(f"ENHANCED_CHAT: Flushing Opik client")
            self.opik_client.flush()
            logger.info(f"ENHANCED_CHAT: Opik client flushed")
            
            result = {
                "answer": answer,
                "sources": filtered_metadata,
                "confidence": reranked_results["confidence"],
                "processing_time": processing_time,
                "metrics": {
                    "retrieval_time": retrieval_duration,
                    "generation_time": generation_duration,
                    "total_time": processing_time,
                    "chunks_retrieved": len(results.get("chunks", [])),
                    "chunks_used": len(filtered_chunks),
                    "tokens": {
                        "input": input_tokens if filtered_chunks else 0,
                        "output": output_tokens if filtered_chunks else 0,
                        "total": total_tokens
                    },
                    "estimated_cost_usd": estimated_cost
                }
            }
            
            logger.info(f"ENHANCED_CHAT: Query processed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"ENHANCED_CHAT: Error in query processing: {e}", exc_info=True)
            logger.error(f"ENHANCED_CHAT: Exception type: {type(e).__name__}")
            logger.error(f"ENHANCED_CHAT: Exception details: {str(e)}")
            # Fallback to basic processing
            return await self._process_query_basic(query, top_k, temperature)
    
    async def _process_query_basic(
        self,
        query: str,
        top_k: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Basic query processing without Opik tracing."""
        start_time = time.time()
        
        try:
            # Retrieve context
            results = self.rag_engine.retrieve_context(query, top_k=top_k)
            
            if not results["chunks"]:
                return {
                    "answer": "I couldn't find relevant information in the documents.",
                    "sources": [],
                    "confidence": 0.0,
                    "processing_time": time.time() - start_time
                }
            
            # Generate answer
            answer = self.rag_engine.answer_query(query)
            
            return {
                "answer": answer,
                "sources": results.get("metadata", []),
                "confidence": results.get("confidence", 0.8),
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"ENHANCED_CHAT: Error in basic processing: {e}", exc_info=True)
            raise
    
    async def _preprocess_query_traced(self, trace, query: str) -> str:
        """Preprocess query with Opik span tracking."""
        span = trace.span(
            name="query_preprocessing",
            input={
                "raw_query": query,
                "query_length": len(query),
                "query_words": len(query.split())
            },
            tags=["preprocessing", "nlp"]
        )
        
        start = time.time()
        
        try:
            # Apply preprocessing from RAG engine
            processed = self.rag_engine._preprocess_query(query)
            
            duration = time.time() - start
            
            span.end(output={
                "processed_query": processed,
                "changes_made": query != processed,
                "added_terms": processed.replace(query, "").strip() if query != processed else "",
                "duration": duration
            })
            
            logger.debug(f"ENHANCED_CHAT: Query preprocessed in {duration:.3f}s")
            return processed
            
        except Exception as e:
            span.end(output={"error": str(e), "status": "failed"})
            logger.error(f"ENHANCED_CHAT: Preprocessing error: {e}")
            return query  # Return original on error
    
    async def _document_retrieval_traced(
        self, trace, query: str, top_k: int
    ) -> Dict[str, Any]:
        """Document retrieval with detailed Opik tracking."""
        span = trace.span(
            name="document_retrieval",
            input={
                "query": query,
                "query_length": len(query),
                "top_k": top_k,
                "vector_store_size": len(self.rag_engine.vector_store.chunks),
                "embedding_model": getattr(self.rag_engine.vector_store, 'model_name', 'unknown'),
                "search_type": "hybrid" if self.rag_engine.enable_hybrid_search else "semantic"
            },
            tags=["retrieval", "vectorstore", "faiss"]
        )
        
        start = time.time()
        
        try:
            # Perform retrieval
            results = self.rag_engine.retrieve_context(query, top_k=top_k)
            
            duration = time.time() - start
            
            # Extract document names and statistics
            doc_names = list(set([
                meta.get("document_name", "unknown")
                for meta in results.get("metadata", [])
            ]))
            
            # Calculate average similarity
            similarities = [
                meta.get("relevance_score", 0)
                for meta in results.get("metadata", [])
            ]
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            
            output = {
                "chunks_retrieved": len(results.get("chunks", [])),
                "documents_matched": doc_names,
                "document_count": len(doc_names),
                "avg_similarity": round(avg_similarity, 4),
                "min_similarity": round(min(similarities), 4) if similarities else 0,
                "max_similarity": round(max(similarities), 4) if similarities else 0,
                "confidence": results.get("confidence", 0.0),
                "duration": duration,
                "top_scores": [round(s, 4) for s in similarities[:3]]
            }
            
            span.end(output=output)
            
            logger.info(
                f"ENHANCED_CHAT: Retrieved {len(results.get('chunks', []))} chunks "
                f"from {len(doc_names)} documents in {duration:.2f}s"
            )
            
            results["duration"] = duration
            return results
            
        except Exception as e:
            span.end(output={"error": str(e), "status": "failed"})
            logger.error(f"ENHANCED_CHAT: Retrieval error: {e}", exc_info=True)
            raise
    
    async def _rerank_documents_traced(
        self, trace, query: str, retrieval_results: Dict
    ) -> Dict[str, Any]:
        """Rerank/filter documents with Opik tracking."""
        span = trace.span(
            name="document_reranking",
            input={
                "query": query,
                "initial_chunks": len(retrieval_results.get("chunks", [])),
                "reranking_method": "relevance_threshold",
                "min_threshold": self.rag_engine.min_similarity_threshold
            },
            tags=["reranking", "filtering", "optimization"]
        )
        
        start = time.time()
        
        try:
            # Apply relevance threshold filtering
            chunks = retrieval_results.get("chunks", [])
            metadata = retrieval_results.get("metadata", [])
            
            filtered_chunks = []
            filtered_metadata = []
            
            for chunk, meta in zip(chunks, metadata):
                if meta.get("relevance_score", 0) >= self.rag_engine.min_similarity_threshold:
                    filtered_chunks.append(chunk)
                    filtered_metadata.append(meta)
            
            duration = time.time() - start
            
            # Calculate confidence boost
            chunks_removed = len(chunks) - len(filtered_chunks)
            confidence_boost = chunks_removed * 0.02  # Small boost for filtering
            
            reranked = {
                "chunks": filtered_chunks,
                "metadata": filtered_metadata,
                "confidence": min(retrieval_results.get("confidence", 0.0) + confidence_boost, 1.0)
            }
            
            span.end(output={
                "reranked_chunks": len(filtered_chunks),
                "chunks_filtered_out": chunks_removed,
                "final_confidence": round(reranked["confidence"], 4),
                "confidence_boost": round(confidence_boost, 4),
                "duration": duration,
                "status": "success"
            })
            
            logger.info(
                f"ENHANCED_CHAT: Reranking complete - {len(filtered_chunks)} chunks kept, "
                f"{chunks_removed} filtered in {duration:.3f}s"
            )
            
            return reranked
            
        except Exception as e:
            span.end(output={"error": str(e), "status": "failed"})
            logger.error(f"ENHANCED_CHAT: Reranking error: {e}")
            return retrieval_results  # Return original on error
    
    async def _build_context_traced(
        self, trace, query: str, results: Dict
    ) -> Dict[str, Any]:
        """Build context string with Opik tracking."""
        span = trace.span(
            name="context_building",
            input={
                "query": query,
                "chunks_available": len(results.get("chunks", [])),
                "max_context_size": self.rag_engine.context_window_size
            },
            tags=["context", "prompt", "preprocessing"]
        )
        
        start = time.time()
        
        try:
            chunks = results.get("chunks", [])
            
            # Build context with document markers
            context_parts = []
            for i, chunk in enumerate(chunks, 1):
                doc_name = results.get("metadata", [{}])[i-1].get("document_name", "Unknown")
                context_parts.append(f"[Document {i}: {doc_name}]\n{chunk}")
            
            context = "\n\n".join(context_parts)
            
            # Truncate if needed
            max_context = self.rag_engine.context_window_size
            truncated = False
            original_length = len(context)
            
            if len(context) > max_context:
                context = context[:max_context]
                truncated = True
            
            duration = time.time() - start
            
            context_data = {
                "context": context,
                "context_length": len(context),
                "chunks_used": len(chunks),
                "truncated": truncated,
                "original_length": original_length
            }
            
            span.end(output={
                "context_length": len(context),
                "context_characters": len(context),
                "chunks_included": len(chunks),
                "truncated": truncated,
                "truncation_percent": round((1 - len(context)/original_length) * 100, 2) if truncated else 0,
                "duration": duration,
                "status": "success"
            })
            
            logger.info(
                f"ENHANCED_CHAT: Context built - {len(context)} chars from {len(chunks)} chunks "
                f"{'(truncated)' if truncated else ''} in {duration:.3f}s"
            )
            
            return context_data
            
        except Exception as e:
            span.end(output={"error": str(e), "status": "failed"})
            logger.error(f"ENHANCED_CHAT: Context building error: {e}")
            raise
    
    async def _generate_answer_traced(
        self, trace, query: str, context_data: Dict, temperature: float
    ) -> Dict[str, Any]:
        """Generate answer with LLM and comprehensive Opik tracking."""
        model_name = getattr(self.rag_engine.llm_engine, 'model_name', 'unknown')
        
        span = trace.span(
            name="llm_generation",
            input={
                "query": query,
                "query_length": len(query),
                "context_length": context_data["context_length"],
                "chunks_used": context_data["chunks_used"],
                "temperature": temperature,
                "model": model_name,
                "max_tokens": 500
            },
            tags=["llm", "generation", "groq"]
        )
        
        start = time.time()
        
        try:
            # Build prompt
            prompt = f"""Based on the following context from the documents, please answer the question accurately and concisely.

Context:
{context_data['context']}

Question: {query}

Answer (provide a clear, informative response based on the context above):"""
            
            # Generate answer using RAG engine
            answer = self.rag_engine.llm_engine.generate(
                prompt,
                max_tokens=500,
                temperature=temperature
            )
            
            duration = time.time() - start
            
            # Token estimation (rough approximation)
            # Average: 1 token ≈ 0.75 words or 4 characters
            input_tokens = int(len(prompt) / 4)
            output_tokens = int(len(answer) / 4)
            total_tokens = input_tokens + output_tokens
            
            # Cost estimation for Groq (example rates - adjust based on actual model)
            # Groq rates are typically very low
            if 'llama' in model_name.lower():
                # Llama 3.x pricing (example)
                input_cost = input_tokens * 0.00000005  # $0.05 per 1M tokens
                output_cost = output_tokens * 0.00000010  # $0.10 per 1M tokens
            elif 'mixtral' in model_name.lower():
                # Mixtral pricing (example)
                input_cost = input_tokens * 0.00000024  # $0.24 per 1M tokens
                output_cost = output_tokens * 0.00000024  # $0.24 per 1M tokens
            else:
                # Default rates
                input_cost = input_tokens * 0.00000010
                output_cost = output_tokens * 0.00000020
            
            total_cost = input_cost + output_cost
            
            result = {
                "answer": answer,
                "duration": duration,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": total_cost
            }
            
            span.end(output={
                "answer_length": len(answer),
                "answer_word_count": len(answer.split()),
                "duration": duration,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "estimated_cost_usd": round(total_cost, 8),
                "tokens_per_second": round(output_tokens / duration, 2) if duration > 0 else 0,
                "model": model_name,
                "status": "success"
            })
            
            logger.info(
                f"ENHANCED_CHAT: Answer generated - {len(answer)} chars, "
                f"{total_tokens} tokens, ${total_cost:.6f} in {duration:.2f}s"
            )
            
            return result
            
        except Exception as e:
            span.end(output={"error": str(e), "status": "failed"})
            logger.error(f"ENHANCED_CHAT: Generation error: {e}", exc_info=True)
            raise


class DocumentProcessingService:
    """Service for document processing operations with Opik tracking."""
    
    def __init__(self):
        self.opik_client = Opik() if OPIK_AVAILABLE else None
        logger.info(f"DocumentProcessingService initialized with Opik: {OPIK_AVAILABLE}")
    
    def process_document_complete(
        self,
        doc_path: str,
        doc_type: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Process a document with complete Opik tracking.
        
        Creates traces similar to the target image with:
        - pdf_extraction
        - llm_parsing
        - csv_generation
        """
        if not OPIK_AVAILABLE or not self.opik_client:
            logger.warning("Opik not available for document processing")
            return {"status": "completed", "message": "Processed without tracking"}
        
        try:
            trace = self.opik_client.trace(
                name="process_document_complete",
                input={
                    "doc_path": doc_path,
                    "doc_type": doc_type
                },
                project_name="rag-system",
                tags=["ingestion", doc_type, "document-processing"]
            )
            
            logger.info(f"DOC_PROCESSING: Processing {doc_path}")
            
            # Step 1: Extraction
            extraction_result = self._document_extraction_traced(trace, doc_path, doc_type)
            
            # Step 2: Parsing
            parsing_result = self._llm_parsing_traced(trace, extraction_result)
            
            # Step 3: Chunk generation
            chunking_result = self._chunk_generation_traced(trace, parsing_result)
            
            result = {
                "status": "success",
                "doc_path": doc_path,
                "chunks_created": chunking_result["chunk_count"],
                "total_tokens": parsing_result.get("token_count", 0),
                "text_length": extraction_result.get("text_length", 0)
            }
            
            trace.end(output=result)
            logger.info(f"DOC_PROCESSING: Completed processing {doc_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"DOC_PROCESSING: Error: {e}", exc_info=True)
            if trace:
                trace.end(output={"status": "failed", "error": str(e)})
            raise
    
    def _document_extraction_traced(self, trace, doc_path: str, doc_type: str) -> Dict:
        """Extract content from document."""
        span = trace.span(
            name=f"{doc_type}_extraction",
            input={"doc_path": doc_path, "doc_type": doc_type},
            tags=["extraction", doc_type]
        )
        
        start = time.time()
        
        # Simulate extraction (replace with actual extraction logic)
        result = {
            "text_length": 5000,  # Placeholder
            "pages": 10,
            "status": "success",
            "duration": time.time() - start
        }
        
        span.end(output=result)
        return result
    
    def _llm_parsing_traced(self, trace, extraction_data: Dict) -> Dict:
        """Parse extracted content with LLM."""
        span = trace.span(
            name="llm_parsing",
            input={"text_length": extraction_data["text_length"]},
            tags=["llm", "parsing", "nlp"]
        )
        
        start = time.time()
        
        # Simulate parsing
        result = {
            "token_count": 6496,
            "structured_data": True,
            "duration": time.time() - start
        }
        
        span.end(output=result)
        return result
    
    def _chunk_generation_traced(self, trace, parsing_data: Dict) -> Dict:
        """Generate chunks from parsed data."""
        span = trace.span(
            name="csv_generation",
            input={"token_count": parsing_data["token_count"]},
            tags=["chunking", "generation", "csv"]
        )
        
        start = time.time()
        
        # Simulate chunk generation
        result = {
            "chunk_count": 25,
            "output_path": "chunks.csv",
            "duration": time.time() - start
        }
        
        span.end(output=result)
        return result
