# Model Comparison Feature - Implementation Complete ✅

## Overview
Implemented a comprehensive model comparison system with automatic LLM-based evaluation using OPIK for tracking and analysis.

## Features Implemented

### 1. **LLM-Based Evaluation Service** (`evaluation_service.py`)

#### `LLMEvaluator` Class
Automatically evaluates RAG responses using LLM-as-judge methodology:

- **Relevance** (0-1): How relevant is the answer to the question?
- **Faithfulness** (0-1): Is the answer grounded in the retrieved context?
- **Completeness** (0-1): Does the answer fully address the question?
- **Overall Score**: Weighted average (35% relevance + 40% faithfulness + 25% completeness)

Uses a structured evaluation prompt that ensures consistent scoring across different responses.

#### `ModelComparisonService` Class
Compares multiple LLM models on the same query:

- Retrieves context once (shared across all models)
- Generates answers from each model
- Evaluates each answer using LLMEvaluator
- Returns ranked results with detailed scores
- Tracks everything in OPIK for analysis

**Available Models:**
- `llama-3.3-70b-versatile` - Best quality, versatile
- `qwen/qwen3-32b` - Qwen's latest 32B model (if enabled)
- `meta-llama/llama-4-scout-17b-16e-instruct` - Latest Llama 4 (if enabled)

### 2. **API Endpoints** (added to `main.py`)

#### `POST /compare-models`
Compare responses from multiple models:
```json
{
  "question": "What is the leave policy?",
  "models": ["llama-3.3-70b-versatile", "qwen/qwen3-32b"],
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What is the leave policy?",
  "models_compared": 2,
  "comparison_time": 1.5,
  "context_chunks": 5,
  "best_model": "llama-3.3-70b-versatile",
  "results": [
    {
      "model": "llama-3.3-70b-versatile",
      "answer": "...",
      "generation_time": 0.5,
      "scores": {
        "relevance": 0.9,
        "faithfulness": 0.95,
        "completeness": 0.85,
        "overall": 0.90,
        "reasoning": {...}
      },
      "tokens": {"prompt": 200, "completion": 150, "total": 350}
    }
  ]
}
```

#### `GET /available-models`
Get list of available models for comparison:
```json
{
  "models": [
    {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "description": "Best quality, versatile"},
    ...
  ],
  "current_model": "llama-3.3-70b-versatile"
}
```

#### `POST /evaluate-response`
Evaluate a single RAG response:
```json
{
  "question": "What is the leave policy?",
  "answer": "The leave policy states...",
  "context": "Retrieved context...",
  "model_used": "llama-3.3-70b-versatile"
}
```

### 3. **OPIK Integration**

All evaluations and comparisons are tracked in OPIK:

- **Traces**: Each comparison creates a trace with nested spans
- **Metrics**: Relevance, faithfulness, completeness scores
- **Metadata**: Model name, tokens used, generation time
- **Context**: Retrieved documents and scores

View traces at: `https://www.comet.com/opik/parth-d/projects/rag-system`

### 4. **Test Script** (`scripts/test_model_comparison.py`)

Comprehensive test script that:
1. Tests single response evaluation
2. Compares multiple models on same query
3. Displays detailed results with scores and reasoning

## Usage Examples

### Via API

```python
import requests

# Compare models
response = requests.post(
    "http://localhost:8000/compare-models",
    json={
        "question": "What is the medical reimbursement policy?",
        "models": ["llama-3.3-70b-versatile"],
        "top_k": 5
    }
)
result = response.json()

print(f"Best model: {result['best_model']}")
for model_result in result['results']:
    print(f"\nModel: {model_result['model']}")
    print(f"Overall score: {model_result['scores']['overall']:.2f}")
    print(f"Answer: {model_result['answer'][:200]}...")
```

### Via Python

```python
from backend.services.evaluation_service import ModelComparisonService
from backend.rag_engine import RAGEngine

# Initialize comparison service
comparison_service = ModelComparisonService(rag_engine)

# Compare models
result = await comparison_service.compare_models(
    query="What is the leave policy?",
    models=["llama-3.3-70b-versatile"],
    top_k=5
)

# View results
for model_result in result['results']:
    scores = model_result['scores']
    print(f"Model: {model_result['model']}")
    print(f"  Relevance: {scores['relevance']:.2f}")
    print(f"  Faithfulness: {scores['faithfulness']:.2f}")
    print(f"  Completeness: {scores['completeness']:.2f}")
```

## Evaluation Methodology

### Relevance Scoring
- **1.0**: Directly answers the question with appropriate detail
- **0.5**: Partially relevant, addresses some aspects
- **0.0**: Completely irrelevant or off-topic

### Faithfulness Scoring
- **1.0**: All claims are supported by the context
- **0.5**: Some claims are supported, some are not
- **0.0**: Contains hallucinations or unsupported claims

### Completeness Scoring
- **1.0**: Comprehensive answer covering all aspects
- **0.5**: Addresses main points but misses some details
- **0.0**: Very incomplete or superficial

### Overall Score
Weighted average: `(0.35 × relevance) + (0.40 × faithfulness) + (0.25 × completeness)`

Faithfulness is weighted highest to prioritize grounding in context.

## Files Modified/Created

### Created:
- `src/backend/services/evaluation_service.py` - Full evaluation and comparison logic
- `scripts/test_model_comparison.py` - Test script

### Modified:
- `src/backend/main.py` - Added API endpoints and request models
- `src/backend/services/tracked_chat_service.py` - Added import path

## Testing

Run the test script:
```bash
python scripts/test_model_comparison.py
```

This will:
1. Test single response evaluation (fast)
2. Compare two models on a sample query
3. Display detailed scores and reasoning
4. Create traces in OPIK dashboard

## Benefits

1. **Objective Comparison**: Automatically compare models using consistent criteria
2. **Quality Insights**: Understand which models perform better for your use case
3. **Cost Optimization**: Test cheaper models vs expensive ones
4. **Response Quality**: Get detailed feedback on relevance, faithfulness, completeness
5. **Continuous Monitoring**: Track all evaluations in OPIK over time

## Next Steps (Optional Enhancements)

1. **Batch Evaluation**: Evaluate models on a test set of questions
2. **Human Feedback**: Allow users to rate answers and compare with LLM scores
3. **A/B Testing**: Automatically route queries to different models based on performance
4. **Cost Tracking**: Add cost per token analysis for model comparison
5. **Custom Metrics**: Add domain-specific evaluation criteria

## Notes

- Current implementation uses `llama-3.3-70b-versatile` for evaluation
- Most Groq models require project-level enablement
- Evaluation adds ~1-2 seconds per response
- All traces are automatically sent to OPIK dashboard
- Scores are logged with full reasoning for transparency
