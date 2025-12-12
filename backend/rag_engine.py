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
        top_k: int = 5,
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
    
    def answer_query_with_context(self, question: str) -> Dict[str, Any]:
        """
        Answer query and return context and sources.
        
        Args:
            question: Question to answer
            
        Returns:
            Dictionary with answer, context, and sources
        """
        if not question or not question.strip():
            logger.warning("Empty question provided")
            return {
                "answer": "Please provide a valid question.",
                "context": "",
                "sources": []
            }
        
        if not self.llm_engine.is_ready():
            logger.error("LLM engine not ready")
            return {
                "answer": "Error: LLM service not available. Please check configuration.",
                "context": "",
                "sources": []
            }
        
        try:
            results = self.vector_store.search(question, top_k=self.top_k)
            
            if not results:
                logger.warning("No documents found for query")
                return {
                    "answer": "No documents found. Please upload documents first.",
                    "context": "",
                    "sources": []
                }
            
            # Build context and sources
            context_parts = []
            sources = []
            
            for i, (chunk, similarity) in enumerate(results, 1):
                context_parts.append(f"[Document {i}]\n{chunk}")
                sources.append({
                    "index": i,
                    "chunk": chunk[:500] + "..." if len(chunk) > 500 else chunk,  # Truncate for response
                    "similarity": round(similarity, 4),
                    "chunk_length": len(chunk)
                })
            
            context = "\n\n".join(context_parts)
            prompt = self._build_prompt(question, context)
            
            logger.debug(f"Generating answer with context for query: {question[:100]}...")
            answer = self.llm_engine.generate(
                prompt,
                max_tokens=settings.MAX_TOKENS,
                temperature=self.temperature
            )
            
            return {
                "answer": answer,
                "context": context,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Error answering query with context: {e}", exc_info=True)
            return {
                "answer": f"Error processing query: {str(e)}",
                "context": "",
                "sources": []
            }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build RAG prompt from question and context.
        
        Args:
            question: User question
            context: Retrieved context chunks
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from documents. 
Use only the information from the context to answer the question. If the context doesn't contain enough information to answer the question, say so clearly.

Context from documents:
{context}

Question: {question}

Please provide a clear and accurate answer based on the context above. If the context doesn't contain relevant information, state that clearly."""
        
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get RAG engine statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "llm_ready": self.llm_engine.is_ready() if self.llm_engine else False,
            "top_k": self.top_k,
            "temperature": self.temperature,
            "vector_store_chunks": len(self.vector_store.chunks) if self.vector_store else 0
        }
