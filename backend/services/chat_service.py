"""Chat service for query handling."""

import time
from typing import List, Dict, Any
from ..logger_config import logger


class ChatService:
    """Service for handling chat queries."""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
    
    async def process_query(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process a user query and generate an answer.
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            temperature: LLM temperature
            
        Returns:
            Dict with answer, sources, confidence, and timing
        """
        try:
            logger.info(f"CHAT_SERVICE: Processing query: {query[:50]}...")
            start_time = time.time()
            
            # Retrieve relevant chunks
            results = self.rag_engine.retrieve_context(query, top_k=top_k)
            
            if not results["chunks"]:
                logger.warning("CHAT_SERVICE: No relevant chunks found")
                return {
                    "answer": "I couldn't find relevant information in the documents. Please try a different question.",
                    "sources": [],
                    "confidence": 0.0,
                    "processing_time": time.time() - start_time
                }
            
            # Generate answer using LLM
            answer = self.rag_engine.generate_answer(
                query,
                results["chunks"],
                temperature=temperature
            )
            
            processing_time = time.time() - start_time
            logger.info(f"CHAT_SERVICE: Query processed in {processing_time:.2f}s")
            
            return {
                "answer": answer,
                "sources": results.get("metadata", []),
                "confidence": results.get("confidence", 0.8),
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"CHAT_SERVICE: Error processing query: {e}", exc_info=True)
            raise
    
    def get_conversation_context(self, conversation_history: List[Dict]) -> str:
        """
        Build context from conversation history.
        
        Args:
            conversation_history: List of previous messages
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content'][:200]}")
        
        return "\n".join(context_parts)
