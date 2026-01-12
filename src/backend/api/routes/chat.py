"""Chat endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from api.models.requests import QueryRequest
from api.models.responses import QueryResponse
from ...logger_config import logger

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=QueryResponse)
async def chat(request: QueryRequest) -> QueryResponse:
    """
    Process a query and return an AI-generated answer.
    
    Args:
        request: Query request with question and parameters
        
    Returns:
        QueryResponse with answer and sources
    """
    try:
        logger.info(f"ENDPOINT: /chat - Query: {request.query[:50]}")
        
        # This will be injected from main.py
        from main import chat_service, rag_engine
        
        result = await chat_service.process_query(
            query=request.query,
            top_k=request.top_k,
            temperature=request.temperature
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.8),
            processing_time=result["processing_time"]
        )
        
    except Exception as e:
        logger.error(f"ENDPOINT: /chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
