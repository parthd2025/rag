# 📊 Dataset in RAG System: Complete Flow Explanation

## 🎯 Quick Answer

When you fire a **query in Streamlit**, the dataset works as follows:

```
USER TYPES QUERY IN STREAMLIT
         ↓
    Backend receives query
         ↓
    ✅ [OPTIONAL] Evaluate against Dataset
         ├─ Compare RAG output with ground truth answers
         ├─ Calculate accuracy/similarity scores
         └─ Show evaluation results
         ↓
    Return answer to Streamlit UI
```

**Dataset's Role**: Provides test cases (question-answer pairs) to **evaluate and validate** the RAG system's performance.

---

## 🔍 How to Check Dataset & What Gets Stored

### 1️⃣ View All Datasets

**Via CLI:**
```bash
python scripts/opik/dataset_management.py list-datasets
```

**Output:**
```
Datasets:
1. ID: dataset_automotive_test_1234567890
   Name: Automotive Test Dataset
   Version: 1.0.0
   Status: active
   Test Cases: 50
   Created: 2025-01-07T10:30:00

2. ID: dataset_general_qa_9876543210
   Name: General Q&A
   Version: 1.0.0
   Status: active
   Test Cases: 100
   ...
```

### 2️⃣ View Specific Dataset Details

**Via CLI:**
```bash
python scripts/opik/dataset_management.py get-dataset --dataset-id dataset_automotive_test_1234567890
```

**Output:**
```
=== Dataset: Automotive Test Dataset ===
ID: dataset_automotive_test_1234567890
Description: Dataset for testing automotive QA
Version: 1.0.0
Status: active
Domain: automotive
Tags: test, v1
Test Cases: 50
Created: 2025-01-07T10:30:00
Updated: 2025-01-07T14:00:00

--- Statistics ---
{
  "total_test_cases": 50,
  "by_difficulty": {
    "easy": 15,
    "medium": 25,
    "hard": 10
  },
  "by_category": {
    "engine": 12,
    "safety": 15,
    "performance": 23
  }
}

--- First 5 Test Cases ---

1. Q: What is the maximum engine displacement?
   A: The maximum engine displacement is 5.0L
   Difficulty: easy, Category: engine

2. Q: How does traction control work?
   A: Traction control prevents wheel slippage by...
   Difficulty: medium, Category: safety

3. Q: Explain regenerative braking system
   A: Regenerative braking recovers kinetic energy...
   Difficulty: hard, Category: performance
   ...
```

### 3️⃣ Storage Location

**Local Storage:**
```
data/datasets/
├── dataset_automotive_test_1234567890/
│   ├── metadata.json              ← Dataset info
│   └── testcases.json             ← All test cases
├── dataset_general_qa_9876543210/
│   ├── metadata.json
│   └── testcases.json
└── ...
```

**Example metadata.json:**
```json
{
  "id": "dataset_automotive_test_1234567890",
  "name": "Automotive Test Dataset",
  "description": "Dataset for testing automotive QA",
  "version": "1.0.0",
  "status": "active",
  "domain": "automotive",
  "tags": ["test", "v1"],
  "test_case_count": 50,
  "created_at": "2025-01-07T10:30:00",
  "updated_at": "2025-01-07T14:00:00"
}
```

**Example testcases.json (first 2 entries):**
```json
[
  {
    "id": "tc_001",
    "question": "What is the maximum engine displacement?",
    "ground_truth_answer": "The maximum engine displacement is 5.0L",
    "context": "Engine specifications document",
    "difficulty_level": "easy",
    "category": "engine",
    "expected_sources": ["engine_specs.pdf"],
    "metadata": {
      "date_added": "2025-01-07",
      "author": "admin"
    }
  },
  {
    "id": "tc_002",
    "question": "How does regenerative braking work?",
    "ground_truth_answer": "Regenerative braking recovers kinetic energy...",
    "context": "Braking system documentation",
    "difficulty_level": "hard",
    "category": "performance",
    "expected_sources": ["braking_system.pdf"],
    "metadata": {
      "date_added": "2025-01-07"
    }
  }
]
```

---

## 🔄 Complete Query Flow with Dataset Role

### Scenario: User Asks Question in Streamlit

```
┌─────────────────────────────────────────────────────────────┐
│ STREAMLIT FRONTEND (User Interface)                         │
│                                                              │
│  User Types: "What is maximum engine displacement?"         │
│         ↓                                                    │
│  [Ask] button clicked                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ HTTP POST /api/search
        
┌─────────────────────────────────────────────────────────────┐
│ BACKEND - MAIN API (FastAPI)                                │
│                                                              │
│  @app.post("/api/search")                                   │
│  async def search(query):                                   │
│      # Pass query to RAG engine                             │
│      result = rag_engine.rag_query_complete(query)          │
│           ↓                                                  │
└─────────────────────┬──────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ↓                         ↓
    
┌──────────────────────┐    ┌──────────────────────────┐
│ RAG ENGINE           │    │ [OPTIONAL] DATASET       │
│                      │    │ EVALUATION               │
│ 1. Retrieve relevant │    │                          │
│    documents from    │    │ • Load test cases        │
│    FAISS index       │    │ • Compare RAG output     │
│                      │    │   with ground truth      │
│ 2. Send to LLM with  │    │ • Calculate scores:      │
│    context           │    │   - Exact match          │
│                      │    │   - Semantic similarity  │
│ 3. Get LLM response  │    │   - Token overlap        │
│    (RAG Answer)      │    │ • Return evaluation      │
└──────────┬───────────┘    │   metrics                │
           │                 └────────────┬────────────┘
           │                              │
           └──────────────┬───────────────┘
                          ↓
        ┌──────────────────────────────────┐
        │ RESULTS OBJECT                   │
        │ {                                │
        │   "answer": "The max is 5.0L",  │
        │   "sources": ["engine_specs"],  │
        │   "evaluation": {               │
        │     "passed": true,             │
        │     "score": 0.95,              │
        │     "metrics": {...}            │
        │   }                             │
        │ }                                │
        └─────────────┬────────────────────┘
                      ↓ HTTP Response
        
┌─────────────────────────────────────────────────────────────┐
│ STREAMLIT FRONTEND                                          │
│                                                              │
│ Display Results:                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Answer: "The maximum engine displacement is 5.0L"      │ │
│ │ Sources: engine_specs.pdf                              │ │
│ │                                                         │ │
│ │ [EVALUATION RESULTS]                                   │ │
│ │ ✓ Passed (Score: 0.95)                                 │ │
│ │ Exact Match: 100%                                      │ │
│ │ Semantic Similarity: 90%                               │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 What Gets Stored in Dataset

### Data Stored Per Test Case

Each test case contains:

```python
{
    "id": "tc_001",                                    # Unique identifier
    "question": "What is the max displacement?",       # The question
    "ground_truth_answer": "The max is 5.0L",          # Expected answer
    "context": "Engine specs document",                # Reference context
    "difficulty_level": "easy|medium|hard",            # Difficulty rating
    "category": "engine|safety|performance|...",       # Category/topic
    "expected_sources": ["engine_specs.pdf"],          # Source documents
    "metadata": {
        "date_added": "2025-01-07",
        "author": "admin",
        "custom_field": "value"
    }
}
```

### Dataset Metadata

```python
{
    "id": "dataset_automotive_test_1234567890",
    "name": "Automotive Test Dataset",
    "description": "Test cases for automotive QA",
    "version": "1.0.0",
    "status": "active|archived|deprecated",
    "domain": "automotive",                            # Domain/category
    "tags": ["test", "v1", "production"],              # Tags for filtering
    "test_case_count": 50,                             # Total test cases
    "created_at": "2025-01-07T10:30:00",
    "updated_at": "2025-01-07T14:00:00"
}
```

---

## 🎮 Using Dataset with Queries

### Option 1: Without Dataset Evaluation
```bash
# Just get RAG answer
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is max displacement?"}'

Response:
{
  "answer": "The maximum engine displacement is 5.0L",
  "sources": ["engine_specs.pdf"],
  "tokens_used": 125
}
```

### Option 2: With Dataset Evaluation
```bash
# Evaluate against test case
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d {
    "query": "What is max displacement?",
    "dataset_id": "dataset_automotive_test_1234567890",
    "test_case_id": "tc_001"
  }

Response:
{
  "answer": "The maximum engine displacement is 5.0L",
  "sources": ["engine_specs.pdf"],
  "evaluation": {
    "test_case_id": "tc_001",
    "passed": true,
    "score": 0.95,
    "predicted_answer": "The maximum engine displacement is 5.0L",
    "ground_truth_answer": "The max is 5.0L",
    "metrics": {
      "exact_match": 0.8,
      "semantic_similarity": 1.0,
      "overall_score": 0.9
    }
  }
}
```

---

## 🔄 Dataset's Role in Query Evaluation

### When Evaluation Happens:

```
1. USER FIRES QUERY IN STREAMLIT
   Query: "What is the maximum engine displacement?"
   
2. RAG ENGINE PROCESSES:
   • Searches FAISS index for relevant documents
   • Sends context + query to Groq LLM
   • Receives answer: "The max is 5.0L"
   
3. DATASET EVALUATION (If Enabled):
   • Load test case from dataset
   • Ground truth: "The maximum engine displacement is 5.0L"
   • Compare RAG output vs Ground truth
   
4. METRICS CALCULATED:
   • Exact Match: 
     "The max is 5.0L" vs "The maximum engine displacement is 5.0L"
     Result: 0.8 (80% match)
   
   • Semantic Similarity (token overlap):
     RAG tokens: {the, max, is, 5.0l}
     GT tokens: {the, maximum, engine, displacement, is, 5.0l}
     Overlap: 3/7 = 0.43 (43%)
   
   • Overall Score: Average = (0.8 + 0.43) / 2 = 0.615
   
   • Pass/Fail: 
     If score >= 0.5: PASS ✓
     If score < 0.5: FAIL ✗
   
5. RETURN RESULTS:
   {
     "answer": "The max is 5.0L",
     "evaluation": {
       "passed": true,
       "score": 0.615,
       "metrics": {...}
     }
   }
```

---

## 🛠️ How to Create & Add Test Cases

### Method 1: Via CLI

```bash
# Create a dataset
python scripts/opik/dataset_management.py create-dataset \
  --name "Automotive Q&A" \
  --description "Test cases for automotive questions" \
  --domain automotive \
  --tags test v1

# Add test cases one by one
python scripts/opik/dataset_management.py add-test-case \
  --dataset-id dataset_automotive_qa_1234567890 \
  --question "What is the engine displacement?" \
  --answer "The engine displacement is 5.0L" \
  --context "From engine specs" \
  --difficulty medium \
  --category engine
```

### Method 2: Import from CSV

**testcases.csv:**
```csv
question,ground_truth_answer,context,difficulty_level,category
"What is the engine displacement?","5.0L","Engine specifications","medium","engine"
"How does regenerative braking work?","Recovers kinetic energy...","Braking system docs","hard","performance"
"What is the max speed?","200 mph","Performance specs","easy","performance"
```

```bash
python scripts/opik/dataset_management.py add-from-csv \
  --dataset-id dataset_automotive_qa_1234567890 \
  --file testcases.csv
```

### Method 3: Via REST API

```bash
curl -X POST http://localhost:8001/datasets/create \
  -H "Content-Type: application/json" \
  -d {
    "name": "Automotive Q&A",
    "description": "Automotive test cases",
    "version": "1.0.0",
    "domain": "automotive",
    "tags": ["test", "v1"]
  }

# Response:
{
  "status": "success",
  "dataset_id": "dataset_automotive_qa_1234567890"
}

# Then add test cases:
curl -X POST http://localhost:8001/datasets/dataset_automotive_qa_1234567890/test-cases \
  -H "Content-Type: application/json" \
  -d {
    "question": "What is engine displacement?",
    "ground_truth_answer": "5.0L",
    "difficulty_level": "medium",
    "category": "engine"
  }
```

---

## 📊 Evaluation Process Detailed

### Exact Match Score

```
Predicted: "The max is 5.0L"
Ground Truth: "The maximum engine displacement is 5.0L"

Comparison (case-insensitive, trimmed):
"the max is 5.0l" == "the maximum engine displacement is 5.0l"
Result: 0.0 (No exact match)

But if prediction was: "The maximum engine displacement is 5.0L"
"the maximum engine displacement is 5.0l" == "the maximum engine displacement is 5.0l"
Result: 1.0 (Perfect match!)
```

### Semantic Similarity (Token Overlap)

```
Predicted: "The max is 5.0L"
Tokens: {the, max, is, 5.0l}

Ground Truth: "The maximum engine displacement is 5.0L"
Tokens: {the, maximum, engine, displacement, is, 5.0l}

Intersection (common tokens): {the, is, 5.0l} = 3 tokens
Union (all unique tokens): {the, max, is, 5.0l, maximum, engine, displacement} = 7 tokens

Jaccard Similarity = Intersection / Union = 3 / 7 = 0.43 (43%)
```

### Overall Score

```
Score = (Exact Match + Semantic Similarity) / 2
      = (0.0 + 0.43) / 2
      = 0.215

Pass Threshold = 0.5
Result: FAIL ✗ (0.215 < 0.5)
```

---

## 📈 Batch Evaluation

Evaluate entire dataset against RAG system:

```bash
# Via CLI
python scripts/opik/dataset_management.py evaluate-dataset \
  --dataset-id dataset_automotive_qa_1234567890

# Output:
Evaluating dataset: dataset_automotive_qa_1234567890
Processing 50 test cases...

Progress: 50/50 [████████████████] 100%

EVALUATION RESULTS:
═══════════════════════════════════════════════════
Total Test Cases: 50
Passed: 42 (84%)
Failed: 8 (16%)
Average Score: 0.82

By Difficulty:
  Easy (15 cases):     14 passed (93%)
  Medium (25 cases):   22 passed (88%)
  Hard (10 cases):     6 passed (60%)

By Category:
  Engine (12):        11 passed (92%)
  Safety (15):        12 passed (80%)
  Performance (23):   19 passed (83%)

Summary Report: evaluation_result_1234567890.json
```

---

## 🎯 Dataset's Role Summary

| When | What Happens | Dataset Role |
|------|-------------|--------------|
| **User enters query** | Frontend sends to backend | Dataset waits (ready) |
| **RAG processes** | Retrieval + LLM generation | Dataset inactive |
| **Answer generated** | RAG produces output | Dataset evaluates |
| **Evaluation phase** | Compare output vs ground truth | Dataset provides test cases |
| **Metrics calculated** | Accuracy/similarity scores | Dataset provides expected answer |
| **Results returned** | User sees answer + evaluation | Dataset comparison complete |

**In Short**: 
- 🔵 **Before Query**: Dataset stores test cases (expected Q&A pairs)
- 🔵 **During Query**: RAG engine generates answers
- 🟢 **After Query**: Dataset evaluates how good the answer is

---

## 📁 Files Involved

| File | Purpose |
|------|---------|
| `src/backend/services/dataset_service.py` | Manages datasets (create, store, retrieve) |
| `src/backend/services/dataset_evaluation.py` | Evaluates RAG output vs ground truth |
| `scripts/opik/dataset_management.py` | CLI for dataset operations |
| `data/datasets/` | Local storage for test cases |
| `src/backend/main.py` | REST API endpoints for datasets |

---

## ✅ Quick Checklist

- [ ] Understand dataset stores Q&A pairs (test cases)
- [ ] Know datasets located in `data/datasets/` 
- [ ] Can create dataset via CLI or API
- [ ] Can add test cases from CSV or manually
- [ ] Understand evaluation metrics (exact match, semantic similarity)
- [ ] Know dataset is optional (query works without it)
- [ ] Can check dataset details with: `python scripts/opik/dataset_management.py get-dataset --dataset-id <id>`

---

Now you understand how datasets work! Any specific part you want me to explain further? 🎯
