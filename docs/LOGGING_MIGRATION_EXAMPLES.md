# Module-Specific Logging Implementation Guide

This guide shows how to update your existing modules to use the new modular logging system.

## 1. Document Service

### Before (Single Unified Log)
```python
# src/backend/services/document_service.py
from ..logger_config import logger

class DocumentService:
    def ingest_document(self, file_path: str):
        logger.info(f"Ingesting: {file_path}")
        # code...
```

### After (Component-Specific Log)
```python
# src/backend/services/document_service.py
from ..logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__, "document_ingestion")

class DocumentService:
    def ingest_document(self, file_path: str):
        logger.info(f"Starting document ingestion | File: {file_path}")
        
        trace_id = LogContext.get_trace_id()
        logger.debug(f"Trace ID: {trace_id}")
        
        try:
            # Document processing logic
            logger.info(f"Document parsed | Chunks: {chunk_count} | Size: {doc_size} bytes")
            logger.info(f"Embeddings generated | Dimension: 384 | Time: 2.5s")
            logger.info(f"Successfully ingested document | Total vectors: {vector_count}")
        except Exception as e:
            logger.error(f"Failed to ingest document: {file_path}", exc_info=True)
            raise
```

**Result:** Logs go to `logs/components/document_ingestion.log`

---

## 2. Vector Store Service

### Before
```python
# src/backend/vector_store.py
from .logger_config import logger

class FAISSVectorStore:
    def add_documents(self, docs: List[Document]):
        logger.info(f"Adding {len(docs)} documents")
        # code...
```

### After
```python
# src/backend/vector_store.py
from .logger_config import LoggerManager
import time

logger = LoggerManager.get_logger(__name__, "vector_store")

class FAISSVectorStore:
    def add_documents(self, docs: List[Document]):
        logger.info(f"Adding documents to FAISS | Count: {len(docs)}")
        start_time = time.time()
        
        try:
            # Process embeddings
            for i, doc in enumerate(docs):
                self._add_single(doc)
                if (i + 1) % 10 == 0:
                    logger.debug(f"Processed {i + 1}/{len(docs)} documents")
            
            elapsed = time.time() - start_time
            logger.info(
                f"Added to FAISS successfully | "
                f"Count: {len(docs)} | "
                f"Time: {elapsed:.2f}s | "
                f"Speed: {len(docs) / elapsed:.1f} docs/sec"
            )
            
            # Save index
            self.save()
            logger.info(f"Index saved | File size: {os.path.getsize(self.index_path) / 1024 / 1024:.2f}MB")
            
        except Exception as e:
            logger.error(f"Failed to add documents to FAISS", exc_info=True)
            raise
    
    def search(self, query_vector, k: int = 5):
        logger.info(f"Searching vector store | Query dimension: {len(query_vector)} | Top-K: {k}")
        start_time = time.time()
        
        try:
            distances, indices = self.index.search(query_vector, k)
            elapsed = time.time() - start_time
            
            logger.info(
                f"Search completed | "
                f"Results: {len(indices[0])} | "
                f"Time: {elapsed * 1000:.1f}ms | "
                f"Min distance: {distances[0].min():.4f} | "
                f"Max distance: {distances[0].max():.4f}"
            )
            
            return indices, distances
        except Exception as e:
            logger.error(f"Vector search failed", exc_info=True)
            raise
```

**Result:** Logs go to `logs/components/vector_store.log`

---

## 3. LLM Engine

### Before
```python
# src/backend/llm_engine.py
from .logger_config import logger

class GroqLLMEngine:
    async def generate(self, prompt: str):
        logger.info(f"Generating with Groq")
        # code...
```

### After
```python
# src/backend/llm_engine.py
from .logger_config import LoggerManager
import time

logger = LoggerManager.get_logger(__name__, "llm_queries")

class GroqLLMEngine:
    async def generate(self, prompt: str, **kwargs):
        """Generate response with comprehensive logging."""
        prompt_tokens = len(prompt.split())
        
        logger.info(
            f"LLM Query Started | "
            f"Model: {self.model} | "
            f"Input tokens (~): {prompt_tokens} | "
            f"Temperature: {self.temperature} | "
            f"Max tokens: {self.max_tokens}"
        )
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            latency = time.time() - start_time
            
            # Extract usage information
            usage = response.usage
            total_cost = self._estimate_cost(usage)
            
            logger.info(
                f"LLM Query Completed | "
                f"Latency: {latency:.2f}s | "
                f"Input tokens: {usage.prompt_tokens} | "
                f"Output tokens: {usage.completion_tokens} | "
                f"Total tokens: {usage.total_tokens} | "
                f"Estimated cost: ${total_cost:.6f}"
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            latency = time.time() - start_time
            logger.error(
                f"LLM Query Failed | "
                f"Model: {self.model} | "
                f"Latency: {latency:.2f}s | "
                f"Error: {str(e)}",
                exc_info=True
            )
            raise
    
    def _estimate_cost(self, usage):
        """Estimate API cost for tracking."""
        # Groq pricing (adjust based on current rates)
        input_cost_per_token = 0.05 / 1000  # $0.05 per 1M tokens
        output_cost_per_token = 0.10 / 1000  # $0.10 per 1M tokens
        
        total_cost = (
            usage.prompt_tokens * input_cost_per_token +
            usage.completion_tokens * output_cost_per_token
        )
        return total_cost
```

**Result:** Logs go to `logs/components/llm_queries.log`

---

## 4. API Endpoints

### Before
```python
# src/backend/main.py
from .logger_config import logger

@app.post("/chat")
async def chat(req: QueryRequest):
    logger.info(f"Chat request received")
    # code...
```

### After
```python
# src/backend/main.py
from .logger_config import LoggerManager, LogContext
import time

api_logger = LoggerManager.get_logger("api", "api_endpoints")

@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware to log all HTTP requests."""
    # Generate trace ID for this request
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])
    LogContext.set_trace_id(trace_id)
    
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    api_logger.info(
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time * 1000:.1f}ms"
    )
    
    return response


@app.post("/chat", response_model=QueryResponse)
async def chat(req: QueryRequest) -> QueryResponse:
    """Chat endpoint with comprehensive logging."""
    api_logger.info(
        f"Chat endpoint | "
        f"Query length: {len(req.query)} chars | "
        f"Top-K: {req.top_k}"
    )
    
    start_time = time.time()
    
    try:
        # Process query
        response = await enhanced_chat_service.process_query(req)
        
        elapsed = time.time() - start_time
        response_length = len(response.answer) if response.answer else 0
        
        api_logger.info(
            f"Chat endpoint success | "
            f"Query length: {len(req.query)} | "
            f"Response length: {response_length} | "
            f"Sources: {len(response.sources)} | "
            f"Time: {elapsed:.2f}s"
        )
        
        return response
        
    except Exception as e:
        elapsed = time.time() - start_time
        api_logger.error(
            f"Chat endpoint failed | "
            f"Query: {req.query[:100]}... | "
            f"Time: {elapsed:.2f}s | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to process query")


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    """Upload endpoint with detailed logging."""
    api_logger.info(f"Upload endpoint | Files: {len(files)}")
    
    doc_logger = LoggerManager.get_logger("upload", "document_ingestion")
    
    try:
        for file in files:
            file_size = len(await file.read())
            await file.seek(0)
            
            doc_logger.info(
                f"Processing upload | "
                f"Filename: {file.filename} | "
                f"Size: {file_size / 1024:.1f}KB | "
                f"MIME type: {file.content_type}"
            )
            
            # Process file...
            doc_logger.info(f"Upload processed | Filename: {file.filename}")
        
        api_logger.info(f"Upload complete | Files processed: {len(files)}")
        return {"status": "success", "files_uploaded": len(files)}
        
    except Exception as e:
        api_logger.error(f"Upload failed", exc_info=True)
        raise HTTPException(status_code=400, detail="Upload failed")
```

**Result:** Logs go to `logs/components/api_endpoints.log`

---

## 5. RAG Engine

### Before
```python
# src/backend/rag_engine.py
from .logger_config import logger

class RAGEngine:
    def answer_question(self, question: str):
        logger.info(f"Processing question")
        # code...
```

### After
```python
# src/backend/rag_engine.py
from .logger_config import LoggerManager
import time

logger = LoggerManager.get_logger(__name__, "rag_engine")
vector_logger = LoggerManager.get_logger(__name__, "vector_store")
llm_logger = LoggerManager.get_logger(__name__, "llm_queries")

class RAGEngine:
    def answer_question(self, question: str, top_k: int = 5) -> str:
        """Answer question using RAG pipeline with full tracing."""
        logger.info(f"RAG pipeline started | Question: {question[:60]}... | Top-K: {top_k}")
        
        total_start = time.time()
        
        try:
            # Step 1: Embed question
            logger.info(f"Step 1: Embedding question...")
            embed_start = time.time()
            question_embedding = self.embedding_model.embed([question])[0]
            embed_time = time.time() - embed_start
            logger.info(f"Question embedded | Time: {embed_time * 1000:.1f}ms | Dimension: {len(question_embedding)}")
            
            # Step 2: Retrieve relevant documents
            logger.info(f"Step 2: Retrieving documents...")
            retrieve_start = time.time()
            
            vector_logger.info(f"Searching for top-{top_k} documents")
            docs = self.vector_store.search(question_embedding, k=top_k)
            
            retrieve_time = time.time() - retrieve_start
            logger.info(
                f"Documents retrieved | "
                f"Count: {len(docs)} | "
                f"Time: {retrieve_time * 1000:.1f}ms | "
                f"Avg relevance: {sum(d['score'] for d in docs) / len(docs):.3f}"
            )
            
            # Step 3: Build context
            logger.info(f"Step 3: Building context...")
            context = self._build_context(docs)
            logger.info(f"Context built | Length: {len(context)} chars | Docs: {len(docs)}")
            
            # Step 4: Generate answer
            logger.info(f"Step 4: Generating answer with LLM...")
            gen_start = time.time()
            
            llm_logger.info(f"Calling LLM with context length: {len(context)}")
            answer = self.llm_engine.generate(
                prompt=self._build_prompt(question, context),
                max_tokens=500
            )
            
            gen_time = time.time() - gen_start
            logger.info(f"Answer generated | Length: {len(answer)} chars | Time: {gen_time:.2f}s")
            
            # Summary
            total_time = time.time() - total_start
            logger.info(
                f"RAG pipeline completed | "
                f"Total time: {total_time:.2f}s | "
                f"Steps: Embed({embed_time*1000:.0f}ms) > "
                f"Retrieve({retrieve_time*1000:.0f}ms) > "
                f"Generate({gen_time*1000:.0f}ms)"
            )
            
            return answer
            
        except Exception as e:
            total_time = time.time() - total_start
            logger.error(
                f"RAG pipeline failed | "
                f"Time: {total_time:.2f}s | "
                f"Question: {question[:60]}... | "
                f"Error: {str(e)}",
                exc_info=True
            )
            raise
```

**Result:** Logs go to `logs/components/rag_engine.log`

---

## 6. Dataset Service

### Example with New Logger
```python
# src/backend/services/dataset_service.py
from ..logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__, "dataset")

class DatasetService:
    def create_dataset(self, dataset_id: str, name: str):
        logger.info(f"Creating dataset | ID: {dataset_id} | Name: {name}")
        
        try:
            # Dataset creation logic...
            logger.info(f"Dataset created successfully | ID: {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to create dataset | ID: {dataset_id}", exc_info=True)
            raise
```

**Result:** Logs go to `logs/components/dataset_service.log`

---

## 7. Frontend (Streamlit)

### Example with New Logger
```python
# src/frontend/app.py
from backend.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__, "frontend")

def main():
    logger.info("Streamlit app started")
    
    if st.button("Upload Document"):
        logger.info("Upload button clicked")
        # Handle upload...
        logger.info("Upload completed successfully")
```

**Result:** Logs go to `logs/frontend/streamlit_app.log`

---

## Migration Checklist

Use this checklist to migrate modules systematically:

- [ ] **Step 1**: Import new LoggerManager
  ```python
  from ..logger_config import LoggerManager
  logger = LoggerManager.get_logger(__name__, "module_name")
  ```

- [ ] **Step 2**: Identify module type and use correct module name:
  - `document_ingestion` - Document processing
  - `vector_store` - FAISS operations
  - `llm_queries` - LLM calls
  - `api_endpoints` - HTTP endpoints
  - `rag_engine` - RAG pipeline
  - `dataset` - Dataset management
  - `frontend` - Streamlit app
  - `opik_tracing` - Observability

- [ ] **Step 3**: Add structured logging with context:
  ```python
  logger.info(f"Operation | Param1: {value1} | Param2: {value2}")
  ```

- [ ] **Step 4**: Include timing for performance tracking:
  ```python
  import time
  start = time.time()
  # do work
  elapsed = time.time() - start
  logger.info(f"Operation completed | Time: {elapsed:.2f}s")
  ```

- [ ] **Step 5**: Use exc_info=True for errors:
  ```python
  logger.error(f"Operation failed", exc_info=True)
  ```

- [ ] **Step 6**: Test logs are going to correct file:
  ```bash
  tail -f logs/components/module_name.log
  ```

---

## Quick Commands for Testing

```bash
# Watch document ingestion logs
tail -f logs/components/document_ingestion.log

# Watch LLM queries and costs
tail -f logs/components/llm_queries.log

# Watch API requests
tail -f logs/components/api_endpoints.log

# Monitor all errors
tail -f logs/errors.log

# Search for a specific trace ID
grep "a1b2c3d4" logs/components/*.log

# Find slow operations (> 5 seconds)
grep "Time: [5-9]\|Time: [0-9][0-9]" logs/components/llm_queries.log

# Count errors by module
for f in logs/components/*.log; do echo "$(basename $f): $(grep -c ERROR $f)"; done

# Watch all logs in real-time (requires 'multitail' tool)
# multitail logs/components/*.log logs/errors.log
```

---

## Next Steps

1. **Decide on migration strategy**:
   - Gradual: Migrate one module per day
   - Aggressive: Migrate all at once (if time allows)

2. **Start with high-volume modules**:
   - Document ingestion
   - LLM queries
   - Vector store

3. **Add trace ID support** (optional but recommended):
   - Add middleware to set trace ID
   - Use trace ID to track requests across logs

4. **Set up log monitoring** (optional):
   - Watch specific logs for errors
   - Monitor performance metrics
   - Set up alerts for ERROR level logs

5. **Archive old logs**:
   - Implement weekly log archiving
   - Keep recent logs for quick access
   - Keep old logs for historical analysis
