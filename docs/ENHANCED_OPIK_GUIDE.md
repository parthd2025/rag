# Enhanced Opik Integration Guide

## 🎯 Overview

The enhanced Opik integration provides **comprehensive, granular tracing** for your RAG system, creating detailed traces similar to professional LLM applications with:

- ✅ **Nested spans** showing the complete RAG flow
- ✅ **Rich metadata** at each processing step
- ✅ **Token tracking and cost estimation**
- ✅ **Performance metrics** (retrieval time, generation time, etc.)
- ✅ **Structured input/output** at every stage
- ✅ **Multiple trace types** (query processing, document ingestion, etc.)

## 📊 What You'll See in Opik Dashboard

### Before (Simple Traces)
```
RAG Query
├─ Input: "What is machine learning?"
└─ Output: "Machine learning is..."
```

### After (Enhanced Traces)
```
rag_query_complete
├─ query_preprocessing
│  ├─ Input: {raw_query, query_length, query_words}
│  └─ Output: {processed_query, changes_made, duration}
│
├─ document_retrieval
│  ├─ Input: {query, top_k, vector_store_size, search_type}
│  └─ Output: {chunks_retrieved, documents_matched, avg_similarity, duration}
│
├─ document_reranking
│  ├─ Input: {query, initial_chunks, reranking_method}
│  └─ Output: {reranked_chunks, confidence_boost, duration}
│
├─ context_building
│  ├─ Input: {query, chunks_available, max_context_size}
│  └─ Output: {context_length, chunks_included, truncated, duration}
│
└─ llm_generation
   ├─ Input: {query, context_length, temperature, model}
   └─ Output: {answer_length, tokens{input, output, total}, cost, duration}
```

## 🏗️ Architecture

### Components Created

1. **`backend/services/chat_service_enhanced.py`**
   - `EnhancedChatService` - Main service with comprehensive tracking
   - `DocumentProcessingService` - Tracks document ingestion

2. **Updated: `backend/main.py`**
   - Integrated enhanced chat service
   - Updated `/chat` endpoint to use enhanced tracking

## 🚀 Features

### 1. Query Processing Traces

Each query creates a detailed trace with nested spans:

#### **Main Trace: `rag_query_complete`**
- Tracks the entire query lifecycle
- Includes user_id, timestamps, model info
- Shows overall success/failure status

#### **Span 1: `query_preprocessing`**
```json
Input: {
  "raw_query": "What is M2 mileage?",
  "query_length": 20,
  "query_words": 4
}

Output: {
  "processed_query": "What is M2 mileage? mileage allowance transportation",
  "changes_made": true,
  "added_terms": "mileage allowance transportation",
  "duration": 0.001
}
```

#### **Span 2: `document_retrieval`**
```json
Input: {
  "query": "What is M2 mileage?",
  "top_k": 5,
  "vector_store_size": 150,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "search_type": "hybrid"
}

Output: {
  "chunks_retrieved": 5,
  "documents_matched": ["M2 Policy.pdf", "Benefits Guide.pdf"],
  "document_count": 2,
  "avg_similarity": 0.8234,
  "min_similarity": 0.7654,
  "max_similarity": 0.9012,
  "confidence": 0.85,
  "duration": 0.124,
  "top_scores": [0.9012, 0.8567, 0.8123]
}
```

#### **Span 3: `document_reranking`**
```json
Input: {
  "query": "What is M2 mileage?",
  "initial_chunks": 5,
  "reranking_method": "relevance_threshold",
  "min_threshold": 0.4
}

Output: {
  "reranked_chunks": 4,
  "chunks_filtered_out": 1,
  "final_confidence": 0.87,
  "confidence_boost": 0.02,
  "duration": 0.003,
  "status": "success"
}
```

#### **Span 4: `context_building`**
```json
Input: {
  "query": "What is M2 mileage?",
  "chunks_available": 4,
  "max_context_size": 3000
}

Output: {
  "context_length": 2847,
  "context_characters": 2847,
  "chunks_included": 4,
  "truncated": false,
  "truncation_percent": 0,
  "duration": 0.001,
  "status": "success"
}
```

#### **Span 5: `llm_generation`**
```json
Input: {
  "query": "What is M2 mileage?",
  "query_length": 20,
  "context_length": 2847,
  "chunks_used": 4,
  "temperature": 0.7,
  "model": "llama-3.1-70b-versatile",
  "max_tokens": 500
}

Output: {
  "answer_length": 342,
  "answer_word_count": 58,
  "duration": 1.234,
  "tokens": {
    "input": 3216,
    "output": 85,
    "total": 3301
  },
  "estimated_cost_usd": 0.000017,
  "tokens_per_second": 68.88,
  "model": "llama-3.1-70b-versatile",
  "status": "success"
}
```

### 2. Document Processing Traces

When uploading documents:

```
process_document_complete
├─ pdf_extraction
│  └─ Output: {text_length, pages, status}
│
├─ llm_parsing
│  └─ Output: {token_count, structured_data}
│
└─ csv_generation
   └─ Output: {chunk_count, output_path}
```

## 📝 Usage

### Basic Usage (Automatic)

The enhanced tracking is **automatically enabled** when you make queries through the `/chat` endpoint:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

### Programmatic Usage

```python
from backend.services.chat_service_enhanced import EnhancedChatService
from backend.rag_engine import RAGEngine

# Initialize
rag_engine = RAGEngine(vector_store, llm_engine)
enhanced_service = EnhancedChatService(rag_engine)

# Process query with full tracking
result = await enhanced_service.process_query_enhanced(
    query="What is M2 mileage?",
    top_k=5,
    temperature=0.7,
    user_id="user_123"
)

# Result includes:
# - answer: Generated response
# - sources: Retrieved documents
# - confidence: Overall confidence score
# - processing_time: Total time taken
# - metrics: Detailed performance metrics
```

## 🔧 Configuration

### Environment Variables

Ensure Opik is configured:

```bash
# .env
OPIK_API_KEY=your_api_key_here
OPIK_WORKSPACE=your_workspace
```

### Opik Configuration

The system uses these Opik settings:

```python
project_name = "rag-system"
tags = ["rag", "query", "production"]
```

## 🎨 Customization

### Adding Custom Metadata

Extend the traces with custom metadata:

```python
# In chat_service_enhanced.py
trace = self.opik_client.trace(
    name="rag_query_complete",
    input={...},
    metadata={
        "model": "llama-3.1-70b",
        "user_tier": "premium",
        "request_id": "req_123",
        # Add your custom fields
        "custom_field": "custom_value"
    }
)
```

### Adding New Spans

Add additional processing steps:

```python
async def _custom_processing_traced(self, trace, data):
    """Custom processing with tracking."""
    span = trace.span(
        name="custom_processing",
        input={"data": data},
        tags=["custom", "processing"]
    )
    
    start = time.time()
    result = self._do_custom_processing(data)
    duration = time.time() - start
    
    span.end(output={
        "result": result,
        "duration": duration,
        "status": "success"
    })
    
    return result
```

## 📊 Metrics Tracked

### Performance Metrics
- Retrieval time
- Generation time
- Total processing time
- Tokens per second

### Quality Metrics
- Confidence scores
- Similarity scores
- Document relevance

### Resource Metrics
- Token usage (input/output/total)
- Estimated costs (per query)
- Context window utilization

## 🧪 Testing

Run the test script to verify the integration:

```bash
python test_enhanced_opik.py
```

Expected output:
```
✅ Opik is installed and available
✅ Vector store loaded with 150 chunks
✅ LLM engine ready
✅ RAG engine initialized
✅ Enhanced chat service initialized
✅ Answer: Machine learning is...
✅ Sources: 3 documents
✅ Confidence: 0.85
✅ Processing time: 1.45s

📊 Check your Opik dashboard for detailed traces
```

## 🎯 Best Practices

### 1. Use Meaningful Tags

```python
tags=["rag", "query", "production", "user_tier_premium"]
```

### 2. Track User Context

```python
result = await enhanced_service.process_query_enhanced(
    query=query,
    user_id=user.id,  # Track per-user performance
    ...
)
```

### 3. Monitor Error Rates

All errors are automatically logged to Opik with:
- Error message
- Stack trace
- Failed step
- Input that caused the error

### 4. Cost Tracking

Monitor cumulative costs:
```python
# In Opik dashboard, filter by:
# - estimated_cost_usd
# - Group by user_id
# - Aggregate by day/week/month
```

## 🔍 Troubleshooting

### Opik Not Available

```python
# Falls back to basic processing automatically
if not OPIK_AVAILABLE:
    logger.warning("Opik not available, using basic processing")
    return await self._process_query_basic(query, top_k, temperature)
```

### Missing Traces

1. Check Opik configuration:
   ```bash
   opik configure
   ```

2. Verify API key:
   ```python
   import opik
   client = opik.Opik()
   print(client.config)
   ```

3. Check logs:
   ```bash
   tail -f logs/app.log | grep -i opik
   ```

### Performance Impact

The enhanced tracking adds minimal overhead:
- Average: ~10-20ms per query
- Mostly async operations
- No impact on user experience

## 📈 Dashboard Views

### Recommended Opik Dashboard Setup

1. **Overview Dashboard**
   - Total queries per day
   - Average response time
   - Error rate
   - Total cost

2. **Performance Dashboard**
   - Retrieval time trends
   - Generation time trends
   - Token usage
   - Cost per query

3. **Quality Dashboard**
   - Confidence scores distribution
   - Documents matched per query
   - Chunk utilization

4. **User Analytics**
   - Queries per user
   - Cost per user
   - Error rate per user

## 🚀 Next Steps

1. **Restart your server:**
   ```bash
   # Stop current server (Ctrl+C)
   # Start with:
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Make test queries:**
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is machine learning?"}'
   ```

3. **Check Opik Dashboard:**
   - Go to https://www.comet.com/opik
   - Navigate to your "rag-system" project
   - View traces with nested spans

4. **Explore traces:**
   - Click on any trace to see nested spans
   - View input/output at each step
   - Analyze performance metrics
   - Track token usage and costs

## 🎉 Success Criteria

You'll know it's working when you see:

✅ Traces named `rag_query_complete` (not just "RAG Query")
✅ 5 nested spans per query
✅ Rich JSON input/output at each span
✅ Token counts and cost estimates
✅ Performance metrics (duration, tokens/sec)
✅ Document names and similarity scores
✅ Confidence scores and quality metrics

## 📚 References

- [Opik Documentation](https://www.comet.com/docs/opik)
- [Opik Python SDK](https://github.com/comet-ml/opik)
- [RAG Best Practices](https://docs.llamaindex.ai/en/stable/)
