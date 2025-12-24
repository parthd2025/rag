"""
RAG Chatbot API - FastAPI backend with improved error handling, security, and configuration.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
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


class SuggestedQuestionsRequest(BaseModel):
    """Request model for suggested questions generation."""
    num_questions: Optional[int] = Field(5, ge=1, le=20, description="Number of suggested questions to generate")


class SuggestedQuestionsResponse(BaseModel):
    """Response model for suggested questions."""
    questions: List[str]
    document_count: int


class SettingsUpdateRequest(BaseModel):
    """Request payload for updating runtime settings."""
    chunking_level: Optional[int] = Field(None, ge=1, le=10, description="Chunking profile level")
    context_window_size: Optional[int] = Field(None, ge=256, le=8192, description="Max context window length")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of chunks to retrieve")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="LLM temperature for answer generation")
    max_suggested_questions: Optional[int] = Field(None, ge=1, le=20, description="Maximum suggested questions to generate")


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
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Global state
vector_store: Optional[FAISSVectorStore] = None
llm_engine = None
rag_engine: Optional[RAGEngine] = None
ingestor: Optional[DocumentIngestor] = None

runtime_settings: Dict[str, Any] = {
    "chunking_level": settings.CHUNKING_LEVEL,
    "context_window_size": settings.CONTEXT_WINDOW_SIZE,
    "top_k": settings.TOP_K,
    "temperature": settings.TEMPERATURE,
    "max_suggested_questions": getattr(settings, 'MAX_SUGGESTED_QUESTIONS', 8),
}


def _generate_fast_questions(chunks: List[str], num_questions: int, llm_engine) -> List[str]:
    """Fast question generation optimized for speed over complexity."""
    try:
        # Use only first few chunks for speed
        context = "\n\n".join(chunks[:10])
        
        # Simple, direct prompt for speed
        prompt = f"""Based on this content, generate {num_questions} simple, direct questions that would help someone explore and understand the key information.

Content:
{context[:2000]}  

Return only the questions as a simple JSON list:
["Question 1?", "Question 2?", ...]

Questions should be:
- Clear and specific
- Answerable from the content
- Useful for exploration
- Different from each other"""

        response = llm_engine.generate(
            prompt=prompt,
            max_tokens=500,  # Reduced for speed
            temperature=0.7
        )
        
        # Simple parsing - look for JSON list
        import json
        try:
            # Try to find JSON array in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                questions_json = response[start:end]
                questions = json.loads(questions_json)
                if isinstance(questions, list):
                    return [q for q in questions if isinstance(q, str) and q.strip()]
        except:
            pass
        
        # Fallback: extract questions from text
        lines = response.split('\n')
        questions = []
        for line in lines:
            line = line.strip()
            if line and ('?' in line or line.endswith('?')):
                # Clean up common prefixes
                for prefix in ['"', "'", "- ", "1. ", "2. ", "3. ", "4. ", "5. "]:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                if line.endswith('"') or line.endswith("'"):
                    line = line[:-1]
                if line:
                    questions.append(line)
                    if len(questions) >= num_questions:
                        break
        
        return questions[:num_questions] if questions else ["What is the main topic discussed in this document?"]
        
    except Exception as e:
        logger.error(f"Fast question generation failed: {e}")
        return [
            "What is the main topic of this document?",
            "What are the key points mentioned?",
            "What important information should I know?"
        ][:num_questions]


def init_components() -> None:
    """Initialize all components with proper error handling and comprehensive logging."""
    global vector_store, llm_engine, rag_engine, ingestor, runtime_settings
    
    logger.info("=== Starting RAG system initialization flow ===")
    
    try:
        # Step 1: Initialize document ingestor
        logger.info("INIT STEP 1: Initializing document ingestor")
        ingestor = DocumentIngestor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            enable_ocr=settings.ENABLE_OCR,
            chunking_level=settings.CHUNKING_LEVEL
        )
        logger.info(
            "INIT STEP 1 COMPLETE: Document ingestor initialized (chunk_size=%s, overlap=%s, chunking_level=%s, ocr=%s)",
            ingestor.chunk_size,
            ingestor.chunk_overlap,
            ingestor.chunking_level,
            settings.ENABLE_OCR
        )
        runtime_settings["chunking_level"] = ingestor.chunking_level
        
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
        
        # Step 4: Initialize RAG engine with runtime settings
        logger.info(f"INIT STEP 4: Initializing RAG engine (top_k={runtime_settings['top_k']}, temperature={runtime_settings['temperature']})")
        rag_engine = RAGEngine(
            vector_store=vector_store,
            llm_engine=llm_engine,
            top_k=runtime_settings["top_k"],
            temperature=runtime_settings["temperature"],
            context_window_size=runtime_settings["context_window_size"]
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


@app.get("/config")
async def get_config() -> dict:
    """Get system configuration endpoint."""
    try:
        return {
            "llm_model": settings.LLM_MODEL,
            "llm_provider": settings.LLM_PROVIDER,
            "embedding_model": settings.EMBEDDING_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "temperature": runtime_settings["temperature"],  # Use runtime setting
            "max_tokens": settings.MAX_TOKENS,
            "top_k": runtime_settings["top_k"],  # Use runtime setting
            "chunking_level": runtime_settings["chunking_level"],
            "context_window_size": runtime_settings["context_window_size"],
            "max_suggested_questions": runtime_settings["max_suggested_questions"],
            "active_chunk_size": ingestor.chunk_size if ingestor else settings.CHUNK_SIZE,
            "active_chunk_overlap": ingestor.chunk_overlap if ingestor else settings.CHUNK_OVERLAP,
        }
    except Exception as e:
        logger.error(f"Config retrieval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve configuration"
        )


@app.put("/settings")
async def update_settings(req: SettingsUpdateRequest) -> dict:
    """Update runtime settings such as chunking level or context window size."""
    global runtime_settings

    updates = req.dict(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No settings provided"
        )

    try:
        if "chunking_level" in updates:
            runtime_settings["chunking_level"] = updates["chunking_level"]
            if ingestor:
                ingestor.set_chunking_level(updates["chunking_level"])

        if "context_window_size" in updates:
            runtime_settings["context_window_size"] = updates["context_window_size"]
            if rag_engine and hasattr(rag_engine, "set_context_window_size"):
                rag_engine.set_context_window_size(updates["context_window_size"])

        if "top_k" in updates:
            runtime_settings["top_k"] = updates["top_k"]
            if rag_engine:
                rag_engine.set_top_k(updates["top_k"])
        
        if "temperature" in updates:
            runtime_settings["temperature"] = updates["temperature"]
            if rag_engine:
                rag_engine.set_temperature(updates["temperature"])

        if "max_suggested_questions" in updates:
            runtime_settings["max_suggested_questions"] = updates["max_suggested_questions"]

        return {
            "settings": {
                **runtime_settings,
                "active_chunk_size": ingestor.chunk_size if ingestor else settings.CHUNK_SIZE,
                "active_chunk_overlap": ingestor.chunk_overlap if ingestor else settings.CHUNK_OVERLAP,
            }
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


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
                    "chunking_level": ingestor.chunking_level if ingestor else runtime_settings["chunking_level"],
                    "chunk_size": ingestor.chunk_size if ingestor else settings.CHUNK_SIZE,
                    "chunk_overlap": ingestor.chunk_overlap if ingestor else settings.CHUNK_OVERLAP,
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
    return {
        "results": results,
        "total_chunks": total_chunks,
        "chunking_level": ingestor.chunking_level if ingestor else runtime_settings["chunking_level"],
        "chunk_size": ingestor.chunk_size if ingestor else settings.CHUNK_SIZE,
        "chunk_overlap": ingestor.chunk_overlap if ingestor else settings.CHUNK_OVERLAP,
    }


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
    
    # Step 4: Process query using runtime settings
    try:
        # Use runtime settings instead of hardcoded config values
        current_top_k = req.top_k or runtime_settings["top_k"]
        logger.info(f"CHAT STEP 4: Processing query with top_k={current_top_k} (from runtime settings)")
        rag_engine.set_top_k(current_top_k)
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


@app.post("/suggested-questions", response_model=SuggestedQuestionsResponse)
async def generate_suggested_questions(req: SuggestedQuestionsRequest) -> SuggestedQuestionsResponse:
    """Generate suggested questions for document exploration (optimized for speed)."""
    
    # Quick validation without verbose logging for speed
    if not vector_store or not vector_store.chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents loaded. Please upload documents first."
        )

    if not llm_engine or not llm_engine.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Check backend configuration."
        )

    try:
        # Fast sampling - use smaller subset for speed
        all_chunks = vector_store.chunks
        sample_size = min(20, len(all_chunks))  # Reduced from 50 for speed
        
        if len(all_chunks) > sample_size:
            step = max(1, len(all_chunks) // sample_size)
            sampled_chunks = all_chunks[::step][:sample_size]
        else:
            sampled_chunks = all_chunks
        
        # Get document count for context
        metadata = getattr(vector_store, 'metadata', [])
        if metadata:
            doc_names = set(
                meta.get('source_doc', 'Document') 
                for meta in metadata[:len(sampled_chunks)]
            )
            doc_count = len(doc_names)
        else:
            doc_count = 1
        
        # Generate simple, direct questions
        questions = _generate_fast_questions(
            chunks=sampled_chunks,
            num_questions=min(req.num_questions or 5, runtime_settings["max_suggested_questions"]),
            llm_engine=llm_engine
        )

        return SuggestedQuestionsResponse(
            questions=questions,
            document_count=doc_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating suggested questions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggested questions"
        )


@app.get("/documents")
async def get_documents() -> dict:
    """Get document statistics."""
    try:
        chunk_count = len(vector_store.chunks) if vector_store else 0
        documents = (
            vector_store.get_document_stats(settings.KNOWLEDGE_MANIFEST_PATH)
            if vector_store else []
        )
        return {
            "chunks": chunk_count,
            "documents": documents,
            "total_documents": len(documents),
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


@app.post("/documents/reload")
async def reload_documents() -> dict:
    """Reload vector store contents from disk without restarting the service."""
    try:
        if not vector_store:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Vector store not initialized"
            )

        total = vector_store.reload_from_disk()
        documents = vector_store.get_document_stats(settings.KNOWLEDGE_MANIFEST_PATH)
        return {
            "status": "ok",
            "chunks": total,
            "documents": documents,
            "total_documents": len(documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reloading vector store: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reloading vector store"
        )


@app.delete("/documents/{document_name}")
async def delete_document(document_name: str) -> dict:
    """Delete a specific document from the vector store."""
    try:
        if not vector_store:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Vector store not initialized"
            )

        # URL decode the document name
        import urllib.parse
        decoded_name = urllib.parse.unquote(document_name)
        
        # Try to delete the document
        deleted_count = vector_store.delete_document(decoded_name)
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{decoded_name}' not found in vector store"
            )
        
        logger.info(f"Deleted document '{decoded_name}': {deleted_count} chunks removed")
        return {
            "status": "ok",
            "message": f"Document '{decoded_name}' deleted successfully",
            "chunks_removed": deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document '{document_name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
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
            "suggested-questions": "POST /suggested-questions",
            "documents": "GET /documents",
            "documents/reload": "POST /documents/reload",
            "documents/{name}": "DELETE /documents/{name}",
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
