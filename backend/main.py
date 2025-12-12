"""
RAG Chatbot API - FastAPI backend with improved error handling, security, and configuration.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uvicorn

from config import settings
from logger_config import logger
from ingest import DocumentIngestor
from vectorstore import FAISSVectorStore
from llm_loader import get_llm_engine
from rag_engine import RAGEngine


class QueryRequest(BaseModel):
    """Request model for chat queries."""
    question: str = Field(..., min_length=1, max_length=1000, description="Question to ask")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")
    
    @validator("question")
    def validate_question(cls, v):
        """Validate question is not empty after stripping."""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class QueryResponse(BaseModel):
    """Response model for chat queries."""
    answer: str
    sources: Optional[List[dict]] = None


# FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0",
    description="Retrieval-Augmented Generation API for document Q&A"
)

# CORS Configuration - Security improvement
cors_origins = settings.cors_origins_list if not settings.PRODUCTION else settings.cors_origins_list
if not cors_origins:
    cors_origins = ["http://localhost:8501", "http://127.0.0.1:8501"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Global state
vector_store: Optional[FAISSVectorStore] = None
llm_engine = None
rag_engine: Optional[RAGEngine] = None
ingestor: Optional[DocumentIngestor] = None


def init_components() -> None:
    """Initialize all components with proper error handling."""
    global vector_store, llm_engine, rag_engine, ingestor
    
    try:
        logger.info("Initializing RAG system components...")
        
        # Initialize document ingestor
        ingestor = DocumentIngestor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        logger.info(f"Document ingestor initialized (chunk_size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")
        
        # Initialize vector store
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        logger.info(f"Vector store initialized with {len(vector_store.chunks)} existing chunks")
        
        # Initialize LLM engine
        llm_engine = get_llm_engine(use_groq=(settings.LLM_PROVIDER.lower() == "groq"))
        if not llm_engine.is_ready():
            logger.warning("LLM engine not ready - check API key configuration")
        else:
            logger.info(f"LLM engine initialized: {settings.LLM_MODEL}")
        
        # Initialize RAG engine
        rag_engine = RAGEngine(
            vector_store=vector_store,
            llm_engine=llm_engine,
            top_k=settings.TOP_K,
            temperature=settings.TEMPERATURE
        )
        logger.info("RAG engine initialized")
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        raise


@app.on_event("startup")
async def startup() -> None:
    """Startup event handler."""
    try:
        init_components()
    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown() -> None:
    """Shutdown event handler with graceful cleanup."""
    logger.info("Shutting down...")
    try:
        if vector_store:
            vector_store._save_index()
            logger.info("Vector store saved successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)
    logger.info("Shutdown complete")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please check logs for details."}
    )


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    try:
        return {
            "status": "ok",
            "llm_ready": llm_engine.is_ready() if llm_engine else False,
            "chunks": len(vector_store.chunks) if vector_store else 0,
            "vector_store_initialized": vector_store is not None,
            "rag_engine_initialized": rag_engine is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)) -> dict:
    """
    Upload and process documents with validation.
    
    Validates file size, extension, and processes documents.
    """
    if not vector_store:
        logger.error("Upload attempted but vector store not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector store not initialized"
        )
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    results = []
    allowed_extensions = settings.allowed_extensions_set
    
    for file in files:
        try:
            # Validate file extension
            file_ext = None
            if file.filename:
                file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else None
            
            if not file_ext or file_ext not in allowed_extensions:
                logger.warning(f"Rejected file {file.filename}: invalid extension")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
                })
                continue
            
            # Read and validate file size
            content = await file.read()
            file_size = len(content)
            
            if file_size > settings.MAX_FILE_SIZE:
                logger.warning(f"Rejected file {file.filename}: size {file_size} exceeds limit {settings.MAX_FILE_SIZE}")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({settings.MAX_FILE_SIZE / 1024 / 1024:.2f}MB)"
                })
                continue
            
            if file_size == 0:
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": "File is empty"
                })
                continue
            
            # Process file
            logger.info(f"Processing file: {file.filename} ({file_size} bytes)")
            chunks, doc_name = ingestor.process_uploaded_file(content, file.filename or "unknown")
            
            if chunks:
                vector_store.add_chunks(chunks, doc_name)
                logger.info(f"Successfully processed {file.filename}: {len(chunks)} chunks")
                results.append({
                    "filename": file.filename,
                    "chunks": len(chunks),
                    "status": "ok"
                })
            else:
                logger.warning(f"No chunks extracted from {file.filename}")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": "No text extracted from file"
                })
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
            results.append({
                "filename": file.filename or "unknown",
                "status": "error",
                "msg": f"Processing error: {str(e)}"
            })
    
    total_chunks = len(vector_store.chunks) if vector_store else 0
    logger.info(f"Upload complete. Total chunks in store: {total_chunks}")
    return {"results": results, "total_chunks": total_chunks}


@app.post("/chat", response_model=QueryResponse)
async def chat(req: QueryRequest) -> QueryResponse:
    """Chat with RAG system."""
    if not rag_engine:
        logger.error("Chat attempted but RAG engine not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG engine not initialized"
        )
    
    if not llm_engine or not llm_engine.is_ready():
        logger.error("Chat attempted but LLM not ready")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Check API key configuration."
        )
    
    if not vector_store or not vector_store.chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents loaded. Please upload documents first."
        )
    
    try:
        logger.info(f"Processing query: {req.question[:100]}...")
        rag_engine.set_top_k(req.top_k or settings.TOP_K)
        result = rag_engine.answer_query_with_context(req.question)
        logger.info("Query processed successfully")
        return QueryResponse(answer=result["answer"], sources=result["sources"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/documents")
async def get_documents() -> dict:
    """Get document statistics."""
    try:
        chunk_count = len(vector_store.chunks) if vector_store else 0
        return {
            "chunks": chunk_count,
            "vector_store_ready": vector_store is not None
        }
    except Exception as e:
        logger.error(f"Error getting documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document information"
        )


@app.delete("/clear")
async def clear() -> dict:
    """Clear all documents from vector store."""
    try:
        if vector_store:
            vector_store.clear()
            logger.info("Vector store cleared")
            return {"status": "ok", "message": "All documents cleared"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Vector store not initialized"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing vector store: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing documents: {str(e)}"
        )


@app.get("/")
async def root() -> dict:
    """API information endpoint."""
    return {
        "api": "RAG Chatbot",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "upload": "POST /upload",
            "chat": "POST /chat",
            "documents": "GET /documents",
            "clear": "DELETE /clear"
        },
        "status": "operational"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
