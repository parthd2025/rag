"""API middleware for request handling."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from logger_config import logger
import time
import uuid


class RequestTrackerMiddleware(BaseHTTPMiddleware):
    """Track and log API requests."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        start_time = time.time()
        
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"[{request_id}] {response.status_code} "
                f"completed in {process_time:.3f}s"
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[{request_id}] Error after {process_time:.3f}s: {e}")
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Handle errors gracefully."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return {
                "error": "Internal Server Error",
                "detail": str(e),
                "request_id": request.state.get("request_id", "unknown")
            }
