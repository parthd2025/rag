"""
ARCHITECTURE REFINEMENT GUIDE
===============================
Document Helper v2.0 - Enhanced Structure

This document outlines the architectural improvements made to the RAG application.
"""

# ============================================================================
# 1. BACKEND SERVICE LAYER REFACTORING
# ============================================================================

## Before (Monolithic)
```
Frontend → API Endpoints (main.py - 499 lines) → RAG Engine
```

## After (Service Layer)
```
Frontend → Modular Routes → Service Layer → Core Components
           ├─ /api/routes/chat.py
           ├─ /api/routes/documents.py
           ├─ /api/routes/health.py
           ├─ /api/routes/quiz.py
           └─ /api/routes/settings.py
                    ↓
           ├─ ChatService
           ├─ DocumentService
           ├─ QuizService
           └─ SettingsService
                    ↓
           ├─ RAGEngine
           ├─ VectorStore
           ├─ LLM Loader
           └─ Document Ingestor
```

### Benefits:
- Separation of concerns
- Easier testing (mock services)
- Reusable business logic
- Clear API contracts with Pydantic models

---

## 2. NEW DIRECTORY STRUCTURE

```
backend/
├── api/
│   ├── __init__.py
│   ├── middleware.py          # Request tracking, error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py        # Input validation models
│   │   └── responses.py       # Output response models
│   └── routes/
│       ├── __init__.py
│       ├── chat.py            # Chat endpoints
│       ├── documents.py       # Document management
│       ├── health.py          # Health & stats
│       ├── quiz.py            # Question generation
│       └── settings.py        # Configuration
│
├── services/
│   ├── __init__.py
│   ├── chat_service.py        # Query processing
│   ├── document_service.py    # Document operations
│   ├── quiz_service.py        # Question generation
│   └── settings_service.py    # Settings management
│
├── core/
│   ├── rag_engine.py          # RAG logic (existing)
│   ├── vectorstore.py         # Vector DB (existing)
│   ├── llm_loader.py          # LLM loading (existing)
│   └── ingest.py              # Ingestion (existing)
│
├── config.py                  # Configuration (existing)
├── logger_config.py           # Logging (existing)
├── main_refactored.py         # New simplified main
└── main.py                    # Original main (deprecated)

frontend/
├── app_enhanced.py            # New enhanced UI
├── app.py                     # Original UI (deprecated)
├── utils/
│   ├── __init__.py
│   ├── api_client.py          # API communication
│   └── formatters.py          # Text formatting utilities
├── components/
│   ├── __init__.py
│   └── chat_ui.py             # Reusable UI components
└── pages/                     # (For future multi-page app)
```

---

## 3. API MODELS (Pydantic)

### Request Models (api/models/requests.py)
- `QueryRequest` - Chat queries with validation
- `DocumentUploadRequest` - Document metadata
- `SettingsRequest` - Settings updates
- `ConversationMessage` - Chat message structure

### Response Models (api/models/responses.py)
- `QueryResponse` - Chat response with sources
- `DocumentInfo` - Document metadata
- `DocumentListResponse` - List of documents
- `HealthResponse` - System health status
- `QuizResponse` - Generated questions
- `ErrorResponse` - Error details

**Benefits:**
- Automatic validation
- Type safety
- Automatic OpenAPI/Swagger docs
- IDE autocomplete support

---

## 4. SERVICE LAYER OVERVIEW

### ChatService
```python
process_query(query, top_k, temperature) → Dict
- Handles query processing
- Manages retrieval and answer generation
- Tracks processing time
- Error recovery
```

### DocumentService
```python
upload_documents(file_paths) → Dict
get_documents() → Dict
delete_document(name) → bool
clear_all_documents() → bool
```

### QuizService
```python
generate_questions(num_questions, include_comparative) → Dict
generate_document_questions(doc_name, num_questions) → Dict
```

### SettingsService
```python
get_settings() → Dict
update_settings(updates) → Dict
reset_settings() → Dict
```

---

## 5. ENHANCED FRONTEND (Streamlit)

### New Features

#### 1. Multi-Tab Interface
- **💬 Chat Tab** - Conversation interface with history
- **📚 Documents Tab** - Upload and manage documents
- **📊 Analytics Tab** - Statistics and metrics
- **⚙️ Settings Tab** - Configuration management

#### 2. Conversation Management
```python
# Automatic session state management
st.session_state.messages = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "sources": [...]}
]
```

#### 3. Document Management UI
- Upload multiple files (PDF, DOCX, TXT, MD)
- View document statistics
- Display chunk counts and file sizes
- Clear all documents

#### 4. Analytics Dashboard
- Total documents count
- Total chunks processed
- Message history tracking
- Document breakdown chart

#### 5. Settings Configuration
- Adjustable top-k parameter
- Temperature control
- Chunk size customization
- Chunk overlap adjustment

---

## 6. MIDDLEWARE LAYER

### RequestTrackerMiddleware
- Request ID generation and tracking
- Processing time measurement
- Request logging

### ErrorHandlerMiddleware
- Global error handling
- Graceful error responses
- Error logging with context

---

## 7. MIGRATION GUIDE

### For Backend Developers

**Old way:**
```python
# main.py - 499 lines, mixed concerns
@app.post("/chat")
def chat(request: QueryRequest):
    # retrieval logic
    # generation logic
    # response formatting
    return response
```

**New way:**
```python
# api/routes/chat.py - Clean endpoint
@router.post("")
async def chat(request: QueryRequest) -> QueryResponse:
    result = await chat_service.process_query(...)
    return QueryResponse(**result)

# services/chat_service.py - Business logic
async def process_query(self, query, top_k, temperature):
    results = self.rag_engine.retrieve_context(query, top_k)
    answer = self.rag_engine.generate_answer(...)
    return {...}
```

### For Frontend Developers

**Old way:**
```python
# Direct API calls scattered in code
response = requests.post("http://localhost:8000/chat", ...)
```

**New way:**
```python
# Centralized API client
api_client = get_api_client()
response = api_client.chat(query, top_k, temperature)
```

---

## 8. TESTING IMPROVEMENTS

### Service Layer Testing
```python
# Easy to mock
mock_rag = Mock()
service = ChatService(mock_rag)
result = await service.process_query("test")
```

### API Endpoint Testing
```python
# Using FastAPI TestClient
client = TestClient(app)
response = client.post("/api/chat", json={"query": "test"})
assert response.status_code == 200
```

---

## 9. CONFIGURATION MANAGEMENT

### Before
- Scattered in main.py
- Hard to override

### After
- Centralized in config.py
- Environment-based
- Settings service for runtime changes

---

## 10. DEPLOYMENT CONSIDERATIONS

### Running Refactored Backend
```bash
# Using new main_refactored.py
python backend/main_refactored.py

# The refactored main automatically:
# - Initializes all components
# - Sets up service layer
# - Registers all routes
# - Configures middleware
```

### Running Enhanced Frontend
```bash
# Using new app_enhanced.py
streamlit run frontend/app_enhanced.py
```

---

## 11. PERFORMANCE IMPROVEMENTS

- **API Routes**: Modular loading (only needed routes)
- **Service Caching**: Reusable service instances
- **Request Tracking**: Better monitoring and debugging
- **Error Handling**: Faster error recovery

---

## 12. BACKWARD COMPATIBILITY

**Current Status:**
- Original `main.py` still works
- Original `app.py` still works
- New components are additions, not replacements

**Migration Path:**
1. Keep existing code working
2. Test new components in parallel
3. Gradually migrate endpoints
4. Complete migration when stable

---

## 13. NEXT STEPS

### Phase 1 (Current)
- ✅ Service layer created
- ✅ Modular routes implemented
- ✅ Enhanced frontend built
- ✅ Middleware added

### Phase 2 (Recommended)
- Add comprehensive tests
- Implement conversation persistence
- Add document tagging/filtering
- Build analytics dashboard

### Phase 3 (Future)
- WebSocket support for real-time updates
- Advanced document management
- User authentication
- Deployment automation

---

## 14. QUICK START

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run refactored server
python backend/main_refactored.py
# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
# Run enhanced UI
streamlit run frontend/app_enhanced.py
# UI runs on http://localhost:8501
```

### Verify
- Open http://localhost:8501 in browser
- Try uploading a document
- Ask a question
- Check API docs at http://localhost:8000/docs

---

**Architecture Refinement Complete!**
All changes maintain backward compatibility while providing a cleaner, more maintainable codebase.
