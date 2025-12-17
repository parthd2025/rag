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
from quiz import generate_quiz_from_chunks


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


class QuizRequest(BaseModel):
    """Request model for quiz generation."""
    num_questions: Optional[int] = Field(5, ge=1, le=20, description="Number of quiz questions to generate")


class QuizResponse(BaseModel):
    """Response model for quiz generation."""
    questions: List[dict]


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
    """Initialize all components with proper error handling and comprehensive logging."""
    global vector_store, llm_engine, rag_engine, ingestor
    
    logger.info("=== Starting RAG system initialization flow ===")
    
    try:
        # Step 1: Initialize document ingestor
        logger.info("INIT STEP 1: Initializing document ingestor")
        ingestor = DocumentIngestor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            enable_ocr=settings.ENABLE_OCR
        )
        logger.info(f"INIT STEP 1 COMPLETE: Document ingestor initialized (chunk_size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP}, ocr={settings.ENABLE_OCR})")
        
        # Step 2: Initialize vector store
        logger.info(f"INIT STEP 2: Initializing vector store (model={settings.EMBEDDING_MODEL})")
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        logger.info(f"INIT STEP 2 COMPLETE: Vector store initialized with {len(vector_store.chunks)} existing chunks")
        
        # Step 3: Initialize LLM engine
        logger.info(f"INIT STEP 3: Initializing LLM engine (provider={settings.LLM_PROVIDER}, model={settings.LLM_MODEL})")
        llm_engine = get_llm_engine(use_groq=(settings.LLM_PROVIDER.lower() == "groq"))
        if not llm_engine.is_ready():
            logger.warning("INIT STEP 3 FAILED: LLM engine not ready - check API key configuration")
        else:
            logger.info(f"INIT STEP 3 COMPLETE: LLM engine initialized and ready")
        
        # Step 4: Initialize RAG engine
        logger.info(f"INIT STEP 4: Initializing RAG engine (top_k={settings.TOP_K}, temperature={settings.TEMPERATURE})")
        rag_engine = RAGEngine(
            vector_store=vector_store,
            llm_engine=llm_engine,
            top_k=settings.TOP_K,
            temperature=settings.TEMPERATURE
        )
        logger.info("INIT STEP 4 COMPLETE: RAG engine initialized")
        
        logger.info("=== RAG system initialization flow COMPLETE ===")
        
    except Exception as e:
        logger.error(f"INIT FAILED: Failed to initialize components: {e}", exc_info=True)
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
    Upload and process documents with validation and comprehensive logging.
    
    Validates file size, extension, and processes documents.
    """
    logger.info(f"=== Starting upload endpoint flow for {len(files)} file(s) ===")
    
    # Step 1: Validate vector store
    if not vector_store:
        logger.error("UPLOAD STEP 1 FAILED: Vector store not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector store not initialized"
        )
    logger.info("UPLOAD STEP 1 COMPLETE: Vector store validated")
    
    # Step 2: Validate files list
    if not files:
        logger.warning("UPLOAD STEP 2 FAILED: No files provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    logger.info(f"UPLOAD STEP 2 COMPLETE: {len(files)} file(s) received")
    
    # Step 3: Process each file
    results = []
    allowed_extensions = settings.allowed_extensions_set
    success_count = 0
    error_count = 0
    
    for idx, file in enumerate(files, 1):
        logger.info(f"UPLOAD STEP 3.{idx}: Processing file {idx}/{len(files)}: {file.filename}")
        
        try:
            # Step 3.1: Validate file extension
            file_ext = None
            if file.filename:
                file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else None
            
            if not file_ext or file_ext not in allowed_extensions:
                logger.warning(f"UPLOAD STEP 3.{idx}.1 FAILED: Invalid extension {file_ext}")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
                })
                error_count += 1
                continue
            logger.info(f"UPLOAD STEP 3.{idx}.1 COMPLETE: Extension validated: {file_ext}")
            
            # Step 3.2: Read and validate file size
            content = await file.read()
            file_size = len(content)
            
            if file_size > settings.MAX_FILE_SIZE:
                logger.warning(f"UPLOAD STEP 3.{idx}.2 FAILED: File size {file_size} exceeds limit")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({settings.MAX_FILE_SIZE / 1024 / 1024:.2f}MB)"
                })
                error_count += 1
                continue
            
            if file_size == 0:
                logger.warning(f"UPLOAD STEP 3.{idx}.2 FAILED: File is empty")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": "File is empty"
                })
                error_count += 1
                continue
            
            logger.info(f"UPLOAD STEP 3.{idx}.2 COMPLETE: File size validated ({file_size} bytes)")
            
            # Step 3.3: Process file
            logger.info(f"UPLOAD STEP 3.{idx}.3: Processing file content")
            chunks, doc_name, stats = ingestor.process_uploaded_file(content, file.filename or "unknown")
            
            if chunks:
                # Step 3.4: Add to vector store
                logger.info(f"UPLOAD STEP 3.{idx}.4: Adding {len(chunks)} chunks to vector store")
                vector_store.add_chunks(chunks, doc_name)
                logger.info(f"UPLOAD STEP 3.{idx} COMPLETE: Successfully processed {file.filename}")

                # Derive simple pattern + chunking description for the frontend
                patterns = stats.get("patterns", [])
                chunking_desc = {}
                
                # Map detected patterns to recommended chunking strategies
                if "heading" in patterns:
                    chunking_desc["heading"] = "Section/Heading-based: Groups content under headings for strong contextual relevance"
                if "paragraph" in patterns:
                    chunking_desc["paragraph"] = "Sentence-based: Groups consecutive sentences with semantic preservation"
                if "table" in patterns:
                    chunking_desc["table"] = "Row-grouped table chunks: Keeps table rows coherent"
                if "list" in patterns:
                    chunking_desc["list"] = "Item-aware: Each list item is a logical chunk"
                if "code" in patterns:
                    chunking_desc["code"] = "Code-aware: Splits by functions, classes, or methods"
                if "kv" in patterns:
                    chunking_desc["kv"] = "Compact key-value blocks: Keeps related config/logs together"

                results.append({
                    "filename": file.filename,
                    "chunks": len(chunks),
                    "status": "ok",
                    "patterns": patterns,
                    "chunking": chunking_desc,
                })
                success_count += 1
            else:
                logger.warning(f"UPLOAD STEP 3.{idx} FAILED: No chunks extracted")
                results.append({
                    "filename": file.filename or "unknown",
                    "status": "error",
                    "msg": "No text extracted from file"
                })
                error_count += 1
                
        except HTTPException:
            logger.error(f"UPLOAD STEP 3.{idx} FAILED: HTTPException raised")
            raise
        except Exception as e:
            logger.error(f"UPLOAD STEP 3.{idx} FAILED: Error processing file {file.filename}: {e}", exc_info=True)
            results.append({
                "filename": file.filename or "unknown",
                "status": "error",
                "msg": f"Processing error: {str(e)}"
            })
            error_count += 1
    
    # Step 4: Finalize
    total_chunks = len(vector_store.chunks) if vector_store else 0
    logger.info(f"=== Upload endpoint flow COMPLETE: {success_count} succeeded, {error_count} failed, {total_chunks} total chunks ===")
    return {"results": results, "total_chunks": total_chunks}


@app.post("/chat", response_model=QueryResponse)
async def chat(req: QueryRequest) -> QueryResponse:
    """Chat with RAG system with comprehensive logging."""
    logger.info(f"=== Starting chat endpoint flow for query: {req.question[:100]}... ===")
    
    # Step 1: Validate RAG engine
    if not rag_engine:
        logger.error("CHAT STEP 1 FAILED: RAG engine not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG engine not initialized"
        )
    logger.info("CHAT STEP 1 COMPLETE: RAG engine validated")
    
    # Step 2: Validate LLM engine
    if not llm_engine or not llm_engine.is_ready():
        logger.error("CHAT STEP 2 FAILED: LLM not ready")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Check API key configuration."
        )
    logger.info("CHAT STEP 2 COMPLETE: LLM engine validated")
    
    # Step 3: Validate vector store
    if not vector_store or not vector_store.chunks:
        logger.warning("CHAT STEP 3 FAILED: No documents loaded")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents loaded. Please upload documents first."
        )
    logger.info(f"CHAT STEP 3 COMPLETE: Vector store validated ({len(vector_store.chunks)} chunks)")
    
    # Step 4: Process query
    try:
        logger.info(f"CHAT STEP 4: Processing query with top_k={req.top_k or settings.TOP_K}")
        rag_engine.set_top_k(req.top_k or settings.TOP_K)
        result = rag_engine.answer_query_with_context(req.question)
        
        if result.get("answer"):
            logger.info(f"CHAT STEP 4 COMPLETE: Query processed successfully, answer length: {len(result['answer'])} chars")
            logger.info(f"=== Chat endpoint flow COMPLETE ===")
            return QueryResponse(answer=result["answer"], sources=result["sources"])
        else:
            logger.warning("CHAT STEP 4 FAILED: Empty answer returned")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Empty response from RAG engine"
            )
    except HTTPException:
        logger.error("CHAT STEP 4 FAILED: HTTPException raised")
        raise
    except Exception as e:
        logger.error(f"CHAT STEP 4 FAILED: Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/quiz", response_model=QuizResponse)
async def generate_quiz(req: QuizRequest) -> QuizResponse:
    """Generate a multiple-choice quiz from the currently loaded document chunks."""
    logger.info(f"=== Starting quiz endpoint flow: num_questions={req.num_questions} ===")

    # Validate vector store
    if not vector_store or not vector_store.chunks:
        logger.warning("QUIZ STEP 1 FAILED: No documents loaded")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents loaded. Please upload documents first."
        )

    # Validate LLM engine
    if not llm_engine or not llm_engine.is_ready():
        logger.error("QUIZ STEP 2 FAILED: LLM not ready")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Check backend configuration."
        )

    try:
        # Select diverse chunks for better quiz generation
        all_chunks = vector_store.chunks
        
        # Use a mix of chunks from different parts of the document
        # This provides better variety for quiz question generation
        if len(all_chunks) > 50:
            # Use chunks from start, middle, and end for diversity
            step = len(all_chunks) // 50
            context_chunks = all_chunks[::step][:50]
        else:
            context_chunks = all_chunks

        logger.info(f"QUIZ: Using {len(context_chunks)} chunks from {len(all_chunks)} total chunks for context")

        result = generate_quiz_from_chunks(
            llm_engine=llm_engine,
            chunks=context_chunks,
            num_questions=req.num_questions or 5,
        )

        questions = result.get("questions", [])
        logger.info(f"QUIZ COMPLETE: Generated {len(questions)} question(s)")
        return QuizResponse(questions=questions)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QUIZ FAILED: Error generating quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
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
