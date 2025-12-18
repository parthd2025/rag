"""Quiz/suggested questions endpoints."""

from fastapi import APIRouter, HTTPException
from api.models.responses import QuizResponse
from logger_config import logger

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("", response_model=QuizResponse)
async def generate_quiz(num_questions: int = 5, include_comparative: bool = True) -> QuizResponse:
    """
    Generate suggested questions from loaded documents.
    
    Args:
        num_questions: Number of questions to generate
        include_comparative: Whether to include comparative questions
        
    Returns:
        QuizResponse with suggested questions
    """
    try:
        logger.info(f"ENDPOINT: /quiz - Generate {num_questions} questions")
        
        from main import quiz_service
        
        result = await quiz_service.generate_questions(
            num_questions=num_questions,
            include_comparative=include_comparative
        )
        
        return QuizResponse(
            questions=result["questions"],
            document_count=result["document_count"]
        )
        
    except Exception as e:
        logger.error(f"ENDPOINT: /quiz error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
