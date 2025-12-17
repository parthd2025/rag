"""
RAG (Retrieval-Augmented Generation) engine with improved error handling and type hints.
"""

from typing import List, Tuple, Dict, Optional, Any
from logger_config import logger
from config import settings


class RAGEngine:
    """Main RAG engine combining retrieval and generation."""
    
    def __init__(
        self,
        vector_store,
        llm_engine,
        top_k: int = 8,
        temperature: float = 0.7
    ):
        """
        Initialize RAG engine.
        
        Args:
            vector_store: Vector store instance for retrieval
            llm_engine: LLM engine instance for generation
            top_k: Number of chunks to retrieve
            temperature: LLM temperature parameter
        """
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        
        self.vector_store = vector_store
        self.llm_engine = llm_engine
        self.top_k = top_k
        self.temperature = temperature
        self.min_similarity_threshold = 0.3
        
        logger.info(f"RAGEngine initialized: top_k={top_k}, temperature={temperature}")
    
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
            
            context = "\n\n".join([f"[Document]\n{chunk}" for chunk, _ in results])
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
    
    def _retrieve_context_with_fallback(self, question: str) -> Tuple[List[Tuple[str, float, dict]], float]:
        """
        Retrieve context with fallback mechanism for low-similarity results.
        
        Args:
            question: Question to search for
            
        Returns:
            Tuple of (results with metadata, average_similarity)
        """
        logger.info(f"Retrieving context with fallback: top_k={self.top_k}")
        results = self.vector_store.search(question, top_k=self.top_k)
        if not results:
            logger.warning("No results found in initial retrieval")
            return results, 0.0
        similarities = [sim for _, sim, _ in results]
        avg_similarity = sum(similarities) / len(similarities)
        logger.info(f"Initial retrieval: {len(results)} results, avg_similarity: {avg_similarity:.4f}")
        if avg_similarity < self.min_similarity_threshold and len(results) < 20:
            logger.info(f"Average similarity ({avg_similarity:.4f}) below threshold. Retrieving more chunks...")
            more_results = self.vector_store.search(question, top_k=min(self.top_k * 2, 20))
            if more_results:
                results = sorted(more_results, key=lambda x: x[1], reverse=True)[:self.top_k + 5]
                similarities = [sim for _, sim, _ in results]
                avg_similarity = sum(similarities) / len(similarities)
                logger.info(f"Fallback retrieval: {len(results)} results, avg_similarity: {avg_similarity:.4f}")
        return results, avg_similarity
    
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
                "sources": []
            }
        logger.info("RAG STEP 2 COMPLETE: LLM engine validated")
        
        # Step 3: Search vector store with fallback
        try:
            logger.info(f"RAG STEP 3: Searching vector store with fallback mechanism")
            results, avg_similarity = self._retrieve_context_with_fallback(question)
            
            if not results:
                logger.warning("RAG STEP 3 FAILED: No documents found for query")
                return {
                    "answer": "No documents found. Please upload documents first.",
                    "context": "",
                    "sources": []
                }
            logger.info(f"RAG STEP 3 COMPLETE: Found {len(results)} relevant chunk(s), avg_similarity: {avg_similarity:.4f}")
        except Exception as e:
            logger.error(f"RAG STEP 3 FAILED: Error searching vector store: {e}", exc_info=True)
            return {
                "answer": f"Error searching documents: {str(e)}",
                "context": "",
                "sources": []
            }
        
        # Step 4: Build context and sources with metadata backtracking
        try:
            logger.info("RAG STEP 4: Building context and sources with metadata")
            context_parts = []
            sources = []
            
            for i, (chunk, similarity, metadata) in enumerate(results, 1):
                context_parts.append(f"[Document {i}]\n{chunk}")
                sources.append({
                    "index": i,
                    "chunk": chunk[:500] + "..." if len(chunk) > 500 else chunk,
                    "similarity": round(similarity, 4),
                    "chunk_length": len(chunk),
                    "source_doc": metadata.get("source_doc", "unknown"),
                    "chunk_index": metadata.get("chunk_index", -1)
                })
            
            context = "\n\n".join(context_parts)
            logger.info(f"RAG STEP 4 COMPLETE: Context built ({len(context)} chars, {len(sources)} sources with metadata)")
        except Exception as e:
            logger.error(f"RAG STEP 4 FAILED: Error building context: {e}", exc_info=True)
            return {
                "answer": f"Error building context: {str(e)}",
                "context": "",
                "sources": []
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
                "sources": sources
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
                logger.info(f"=== RAG query flow COMPLETE ===")
                return {
                    "answer": answer,
                    "context": context,
                    "sources": sources
                }
            else:
                logger.warning("RAG STEP 6 FAILED: Empty answer generated")
                return {
                    "answer": "Error: Empty response from LLM.",
                    "context": context,
                    "sources": sources
                }
        except Exception as e:
            logger.error(f"RAG STEP 6 FAILED: Error generating answer: {e}", exc_info=True)
            return {
                "answer": f"Error processing query: {str(e)}",
                "context": context,
                "sources": sources
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
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from documents.

{confidence_instruction}

Context from documents:
{context}

Question: {question}

Instructions:
1. Answer the question based primarily on the context provided
2. If the context contains relevant information, use it to formulate your answer
3. If specific details are missing from the context, acknowledge what is not covered but provide what information is available
4. Be clear and accurate in your response
5. If absolutely no relevant information is available in the context, state this clearly

Please provide your answer:"""
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
            "vector_store_chunks": len(self.vector_store.chunks) if self.vector_store else 0,
            "source_documents": self.get_documents_by_source()
        }
