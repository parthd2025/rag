"""Health and stats endpoints."""

from fastapi import APIRouter, HTTPException
from api.models.responses import HealthResponse
from ...logger_config import logger
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check system health status.
    
    Returns:
        Health status with system info
    """
    try:
        logger.info("ENDPOINT: /health")
        
        from main import rag_engine, vectorstore
        
        doc_count = 0
        try:
            metadata = vectorstore.get_metadata()
            doc_count = len(metadata) if metadata else 0
        except:
            pass
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            documents_loaded=doc_count,
            embeddings_loaded=True,
            llm_ready=True,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"ENDPOINT: /health error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
