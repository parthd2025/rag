"""Quiz/Question generation service."""

from typing import List, Dict, Any
from logger_config import logger
import quiz as quiz_module


class QuizService:
    """Service for generating suggested questions."""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
    
    async def generate_questions(
        self,
        num_questions: int = 5,
        include_comparative: bool = True
    ) -> Dict[str, Any]:
        """
        Generate suggested questions from loaded documents.
        
        Args:
            num_questions: Number of questions to generate
            include_comparative: Whether to include comparative questions
            
        Returns:
            Dict with suggested questions
        """
        try:
            logger.info(f"QUIZ_SERVICE: Generating {num_questions} questions")
            
            # Get available chunks
            chunks = self.rag_engine.get_all_chunks()
            
            if not chunks:
                logger.warning("QUIZ_SERVICE: No chunks available for question generation")
                return {"questions": [], "document_count": 0}
            
            # Generate questions using quiz module
            result = quiz_module.generate_quiz_from_chunks(
                self.rag_engine.llm,
                chunks,
                num_questions=num_questions
            )
            
            return {
                "questions": result.get("questions", []),
                "document_count": len(set(c.get("metadata", {}).get("source") for c in chunks))
            }
            
        except Exception as e:
            logger.error(f"QUIZ_SERVICE: Error generating questions: {e}", exc_info=True)
            return {"questions": [], "document_count": 0}
    
    async def generate_document_questions(
        self,
        document_name: str,
        num_questions: int = 3
    ) -> Dict[str, Any]:
        """
        Generate questions specific to a document.
        
        Args:
            document_name: Name of the document
            num_questions: Number of questions
            
        Returns:
            Dict with document-specific questions
        """
        try:
            logger.info(f"QUIZ_SERVICE: Generating questions for {document_name}")
            
            # Get chunks for specific document
            chunks = self.rag_engine.get_chunks_by_document(document_name)
            
            if not chunks:
                logger.warning(f"QUIZ_SERVICE: No chunks found for {document_name}")
                return {"questions": []}
            
            # Generate document-specific questions
            questions = quiz_module.generate_document_specific_questions(
                self.rag_engine.llm,
                chunks,
                document_name,
                num_questions=num_questions
            )
            
            return {
                "questions": [{"question": q, "type": "document-specific"} for q in questions],
                "document": document_name
            }
            
        except Exception as e:
            logger.error(f"QUIZ_SERVICE: Error generating document questions: {e}", exc_info=True)
            return {"questions": []}
