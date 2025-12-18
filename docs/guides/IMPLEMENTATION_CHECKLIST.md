# Document Helper - Implementation Checklist

## Quick Start Guide

### Prerequisites
- Python 3.8+
- pip or conda
- Groq API key (or local LLM)

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Set environment variables
cp env.template .env
# Edit .env with your GROQ_API_KEY
```

### Running the Application

#### Option 1: Refactored Architecture (Recommended)

**Backend:**
```bash
cd backend
python main_refactored.py
# Runs on: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/api/health
```

**Frontend (in new terminal):**
```bash
streamlit run frontend/app_enhanced.py
# Runs on: http://localhost:8501
```

#### Option 2: Original Architecture (Still Supported)

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
streamlit run frontend/app.py
```

---

## Key Features to Test

### 1. Chat Interface (💬 Tab)
- [ ] Type a question
- [ ] Verify response appears
- [ ] Check sources are shown
- [ ] Verify processing time is displayed

### 2. Document Management (📚 Tab)
- [ ] Upload a PDF document
- [ ] Upload multiple documents
- [ ] View document statistics
- [ ] Verify chunk count is correct

### 3. Analytics (📊 Tab)
- [ ] Check document count metric
- [ ] View total chunks metric
- [ ] See message count
- [ ] View document breakdown chart

### 4. Settings (⚙️ Tab)
- [ ] Adjust top-k slider
- [ ] Adjust temperature slider
- [ ] Modify chunk size
- [ ] Modify chunk overlap
- [ ] Save settings
- [ ] Reset to defaults

---

## API Endpoints Reference

### Chat
```
POST /api/chat
{
  "query": "string",
  "top_k": 5,
  "temperature": 0.7
}
Response: QueryResponse
```

### Documents
```
GET    /api/documents              # List all documents
POST   /api/documents/upload       # Upload documents
DELETE /api/documents/clear        # Clear all documents
```

### Health
```
GET /api/health                    # System status
GET /api/health/stats              # Statistics
```

### Quiz
```
POST /api/quiz?num_questions=5    # Generate questions
```

### Settings
```
GET    /api/settings               # Get current settings
PUT    /api/settings               # Update settings
POST   /api/settings/reset         # Reset to defaults
```

---

## Troubleshooting

### Backend Issues

#### API not starting
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
# Kill process: taskkill /PID <PID> /F
```

#### GROQ API errors
```
Error: "API key is invalid"
→ Check GROQ_API_KEY in .env file
→ Verify key from https://console.groq.com
```

#### Vector store issues
```
Error: "No valid chunks found"
→ Upload documents first
→ Check document format (PDF, DOCX, TXT, MD)
```

### Frontend Issues

#### Cannot connect to backend
```
Error: "Connection refused"
→ Verify backend is running (port 8000)
→ Check CORS settings in main_refactored.py
```

#### Streamlit not loading
```bash
# Clear cache
streamlit cache clear

# Run with debug
streamlit run frontend/app_enhanced.py --logger.level=debug
```

---

## Development Workflow

### Adding a New API Endpoint

1. **Create request/response models** (if needed)
   ```python
   # backend/api/models/requests.py
   class MyRequest(BaseModel):
       field: str
   
   # backend/api/models/responses.py
   class MyResponse(BaseModel):
       result: str
   ```

2. **Create a service method**
   ```python
   # backend/services/my_service.py
   class MyService:
       async def do_something(self, param: str) -> Dict:
           # business logic
           return {"result": "..."}
   ```

3. **Create the route**
   ```python
   # backend/api/routes/my_route.py
   @router.post("/my-endpoint")
   async def my_endpoint(request: MyRequest) -> MyResponse:
       service = MyService()
       result = await service.do_something(request.field)
       return MyResponse(result=result["result"])
   ```

4. **Register in main_refactored.py**
   ```python
   from api.routes import my_route
   app.include_router(my_route.router)
   ```

---

## Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Run All Tests
```bash
pytest -v
```

### Test Coverage
```bash
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html
```

---

## Performance Tips

### Optimize Retrieval
```python
# In main_refactored.py
chat_service = ChatService(rag_engine)
# Adjust top_k for fewer/more results
result = await chat_service.process_query("q", top_k=3)  # Faster
result = await chat_service.process_query("q", top_k=10) # More thorough
```

### Batch Document Upload
```bash
# Create folder with documents
mkdir documents_to_upload
# Place PDFs, DOCXs, etc. in folder
# Upload via frontend (📚 Documents tab)
```

### Monitor API Performance
```
GET http://localhost:8000/api/health
# Includes processing metrics
```

---

## Deployment

### Docker Deployment
```dockerfile
# Build backend image
docker build -f Dockerfile.backend -t rag-backend .

# Run backend
docker run -p 8000:8000 rag-backend

# Run frontend
docker run -p 8501:8501 rag-frontend
```

### Cloud Deployment (AWS/GCP/Azure)
1. Containerize both frontend and backend
2. Use service orchestration (ECS, GKE, AKS)
3. Configure networking and security
4. Deploy CI/CD pipeline

---

## Documentation Files

- **ARCHITECTURE_REFINEMENT_GUIDE.md** - Detailed architecture overview
- **REFINEMENT_IMPLEMENTATION_SUMMARY.md** - Implementation details
- **README.md** - General project information
- **docs/API_DOCS.md** - API documentation

---

## Support & Contribution

### Reporting Issues
1. Check existing issues in GitHub
2. Provide: error message, steps to reproduce, environment
3. Include logs from `.logs/` directory

### Contributing
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push and create pull request

---

## Version Information

- **Document Helper**: 2.0.0
- **Architecture**: Service Layer Pattern
- **Backend Framework**: FastAPI
- **Frontend Framework**: Streamlit
- **Vector DB**: FAISS
- **LLM**: Groq / Local Models

---

## Useful Commands

```bash
# View API documentation
open http://localhost:8000/docs

# View API schema
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/api/health

# View logs
tail -f backend/logs/*.log

# Clean cache
rm -rf __pycache__ .pytest_cache

# Reset vector store
rm -rf backend/data/embeddings/*

# Format code
black backend/ frontend/

# Check types
mypy backend/

# Lint
flake8 backend/
```

---

**Happy coding! 🚀**
