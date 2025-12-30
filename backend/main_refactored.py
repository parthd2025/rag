"""
RAG Chatbot API - FastAPI backend with service layer architecture.
Refactored for better organization and maintainability.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

from backend.config import settings
from backend.logger_config import logger
from backend.ingest import DocumentIngestor
from backend.vectorstore import FAISSVectorStore
from backend.llm_loader import get_llm_engine
from backend.rag_engine import RAGEngine

# Import service layer
from backend.services.chat_service import ChatService
from backend.services.document_service import DocumentService
from backend.services.quiz_service import QuizService
from backend.services.settings_service import SettingsService

# Import routes
from backend.api.routes import chat, documents, health, quiz, settings as settings_routes

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Core components
vectorstore: FAISSVectorStore = None
llm_engine = None
rag_engine: RAGEngine = None
ingestor: DocumentIngestor = None

# Service layer instances
chat_service: ChatService = None
document_service: DocumentService = None
quiz_service: QuizService = None
settings_service: SettingsService = None


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_components() -> None:
    """Initialize all core components and services."""
    global vectorstore, llm_engine, rag_engine, ingestor
    global chat_service, document_service, quiz_service, settings_service
    
    logger.info("=== Starting RAG system initialization ===")
    
    try:
        # Step 1: Initialize document ingestor
        logger.info("INIT: Initializing document ingestor")
        ingestor = DocumentIngestor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            enable_ocr=settings.ENABLE_OCR
        )
        logger.info(f"✓ Document ingestor initialized")
        
        # Step 2: Initialize vector store
        logger.info("INIT: Initializing vector store")
        vectorstore = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        logger.info(f"✓ Vector store initialized with {len(vectorstore.chunks)} chunks")
        
        # Step 3: Initialize LLM engine
        logger.info(f"INIT: Initializing LLM engine (model={settings.LLM_MODEL_NAME})")
        llm_engine = get_llm_engine(settings.LLM_MODEL_NAME, settings.GROQ_API_KEY)
        logger.info(f"✓ LLM engine initialized")
        
        # Step 4: Initialize RAG engine
        logger.info("INIT: Initializing RAG engine")
        rag_engine = RAGEngine(
            llm_engine=llm_engine,
            vector_store=vectorstore,
            top_k=settings.TOP_K
        )
        logger.info(f"✓ RAG engine initialized")
        
        # Step 5: Initialize services
        logger.info("INIT: Initializing service layer")
        chat_service = ChatService(rag_engine)
        document_service = DocumentService(vectorstore, ingestor)
        quiz_service = QuizService(rag_engine)
        settings_service = SettingsService(settings, ingestor=ingestor, rag_engine=rag_engine)
        logger.info(f"✓ All services initialized")
        
        logger.info("=== RAG system initialization complete ===")
        
    except Exception as e:
        logger.error(f"INIT ERROR: {e}", exc_info=True)
        raise


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Document Helper - RAG API",
        version="2.0.0",
        description="Intelligent document retrieval and Q&A system"
    )
    
    # CORS middleware
    cors_origins = ["http://localhost:8501", "http://127.0.0.1:8501"]
    if not settings.PRODUCTION:
        cors_origins.extend(["*"])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    app.include_router(chat.router)
    app.include_router(documents.router)
    app.include_router(health.router)
    app.include_router(quiz.router)
    app.include_router(settings_routes.router)
    
    return app


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

app = create_app()


@app.on_event("startup")
async def startup_event():
    """Initialize components on app startup."""
    logger.info("FastAPI startup event triggered")
    init_components()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    logger.info("FastAPI shutdown event triggered")
    try:
        if vectorstore:
            vectorstore.close()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Document Helper - RAG API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting server: {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.PRODUCTION,
        log_level="info"
    )
