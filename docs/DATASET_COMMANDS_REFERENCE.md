# 🚀 Dataset Commands Quick Reference

## Viewing & Checking Datasets

### 1. List All Datasets
```bash
python scripts/opik/dataset_management.py list-datasets
```
**Shows**: All datasets with ID, name, version, status, test case count

### 2. View Specific Dataset Details
```bash
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id dataset_automotive_qa_1234567890
```
**Shows**: Full metadata, statistics, first 5 test cases

### 3. View Dataset File Structure
```bash
# See where datasets are stored
ls -la data/datasets/

# View specific dataset files
cat data/datasets/dataset_automotive_qa_1234567890/metadata.json
cat data/datasets/dataset_automotive_qa_1234567890/testcases.json
```

### 4. Check Dataset Statistics
```bash
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id dataset_automotive_qa_1234567890
# Shows: total_test_cases, by_difficulty, by_category
```

---

## Creating Datasets

### Create Empty Dataset
```bash
python scripts/opik/dataset_management.py create-dataset \
  --name "Automotive Test" \
  --description "Test cases for automotive QA" \
  --domain automotive \
  --tags test v1
```

**Output**: 
```
✓ Dataset created successfully: dataset_automotive_test_1234567890
```

---

## Adding Test Cases

### Add Single Test Case
```bash
python scripts/opik/dataset_management.py add-test-case \
  --dataset-id dataset_automotive_test_1234567890 \
  --question "What is the maximum engine displacement?" \
  --answer "The maximum engine displacement is 5.0L" \
  --context "Engine specifications document" \
  --difficulty medium \
  --category engine
```

### Add Multiple Test Cases from CSV
```bash
# File: testcases.csv
# question,ground_truth_answer,context,difficulty_level,category
# "What is the engine displacement?","5.0L","Engine specs","medium","engine"
# "How does regenerative braking work?","Recovers kinetic energy...","Braking docs","hard","safety"

python scripts/opik/dataset_management.py add-from-csv \
  --dataset-id dataset_automotive_test_1234567890 \
  --file testcases.csv
```

---

## Data Storage & Retrieval

### Storage Locations
```
data/datasets/
├── dataset_automotive_test_1234567890/
│   ├── metadata.json          ← Dataset info
│   └── testcases.json         ← All test cases
└── dataset_general_qa_9876543210/
    ├── metadata.json
    └── testcases.json
```

### Manually Check Data
```bash
# View metadata
cat data/datasets/dataset_automotive_test_1234567890/metadata.json

# View test cases (formatted)
python -m json.tool data/datasets/dataset_automotive_test_1234567890/testcases.json

# Count test cases
python -c "import json; f=open('data/datasets/dataset_automotive_test_1234567890/testcases.json'); print(len(json.load(f)))"
```

---

## Evaluation & Testing

### Evaluate Single Query Against Dataset
```bash
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the maximum engine displacement?",
    "dataset_id": "dataset_automotive_test_1234567890",
    "test_case_id": "tc_001"
  }'
```

**Response**:
```json
{
  "answer": "The maximum engine displacement is 5.0L",
  "sources": ["engine_specs.pdf"],
  "evaluation": {
    "test_case_id": "tc_001",
    "passed": true,
    "score": 0.95,
    "metrics": {
      "exact_match": 0.8,
      "semantic_similarity": 1.0,
      "overall_score": 0.9
    }
  }
}
```

### Batch Evaluate Entire Dataset
```bash
python scripts/opik/dataset_management.py evaluate-dataset \
  --dataset-id dataset_automotive_test_1234567890
```

**Output**:
```
Evaluation Results for dataset_automotive_test_1234567890
─────────────────────────────────────────────────────────
Total: 50 test cases
Passed: 42 (84%)
Failed: 8 (16%)
Average Score: 0.82

By Difficulty:
  Easy: 14/15 passed (93%)
  Medium: 22/25 passed (88%)
  Hard: 6/10 passed (60%)
```

---

## Import/Export

### Export Dataset
```bash
# Export as JSON
python scripts/opik/dataset_management.py export-dataset \
  --dataset-id dataset_automotive_test_1234567890 \
  --output exported_dataset.json \
  --format json

# Export as CSV
python scripts/opik/dataset_management.py export-dataset \
  --dataset-id dataset_automotive_test_1234567890 \
  --output exported_dataset.csv \
  --format csv
```

### Import Dataset from File
```bash
python scripts/opik/dataset_management.py import-dataset \
  --file exported_dataset.json \
  --name "Imported Dataset" \
  --description "Dataset imported from file" \
  --version 1.0.0
```

---

## Management Operations

### Update Dataset Status
```bash
python scripts/opik/dataset_management.py update-status \
  --dataset-id dataset_automotive_test_1234567890 \
  --status archived
# Status options: active, archived, deprecated
```

### Sync to OPIK Cloud (Optional)
```bash
python scripts/opik/dataset_management.py sync-to-opik \
  --dataset-id dataset_automotive_test_1234567890
```

### Generate Sample Dataset
```bash
python scripts/opik/dataset_management.py generate-sample \
  --name "Sample Dataset" \
  --description "Auto-generated sample" \
  --count 10
```

### Show Dataset Template
```bash
python scripts/opik/dataset_management.py show-template
```

**Output**:
```json
{
  "id": "tc_001",
  "question": "Your question here?",
  "ground_truth_answer": "Expected answer here",
  "context": "Optional context/reference",
  "difficulty_level": "easy|medium|hard",
  "category": "category_name",
  "expected_sources": ["source1.pdf", "source2.pdf"],
  "metadata": {
    "custom_field": "custom_value"
  }
}
```

---

## Programmatic Usage (Python)

### Load and Use Dataset Service
```python
from src.backend.services.dataset_service import DatasetService
from src.backend.services.dataset_evaluation import DatasetEvaluator

# Initialize
dataset_service = DatasetService()
evaluator = DatasetEvaluator(dataset_service)

# List datasets
datasets = dataset_service.get_all_datasets()
for ds in datasets:
    print(f"Dataset: {ds.name} ({len(dataset_service.get_test_cases(ds.id))} test cases)")

# Get specific dataset
dataset = dataset_service.get_dataset("dataset_automotive_test_1234567890")
print(f"Dataset: {dataset.name}, Version: {dataset.version}")

# Get test cases
test_cases = dataset_service.get_test_cases("dataset_automotive_test_1234567890")
for tc in test_cases:
    print(f"Q: {tc.question}")
    print(f"A: {tc.ground_truth_answer}")

# Evaluate
result = evaluator.evaluate_dataset("dataset_automotive_test_1234567890", rag_engine)
print(f"Passed: {result.passed_count}/{result.total_test_cases}")
```

---

## What Gets Stored (Data Structure)

### Test Case Example
```json
{
  "id": "tc_001",
  "question": "What is the maximum engine displacement?",
  "ground_truth_answer": "The maximum engine displacement is 5.0L",
  "context": "Engine specifications from manual",
  "difficulty_level": "medium",
  "category": "engine",
  "expected_sources": ["engine_manual.pdf"],
  "metadata": {
    "date_added": "2025-01-07",
    "author": "admin"
  }
}
```

### Dataset Metadata Example
```json
{
  "id": "dataset_automotive_test_1234567890",
  "name": "Automotive Test Dataset",
  "description": "Test cases for automotive QA system",
  "version": "1.0.0",
  "status": "active",
  "domain": "automotive",
  "tags": ["test", "v1"],
  "test_case_count": 50,
  "created_at": "2025-01-07T10:30:00",
  "updated_at": "2025-01-07T14:00:00"
}
```

---

## Flow When Query Fired in Streamlit

```
1. USER TYPES QUERY
   Query: "What is the maximum engine displacement?"

2. BACKEND RECEIVES (FastAPI)
   POST /api/search
   {
     "query": "...",
     "dataset_id": "dataset_automotive_test_1234567890"  [optional]
   }

3. RAG ENGINE PROCESSES
   • Search FAISS index
   • Send to LLM with context
   • Get answer

4. DATASET EVALUATION [if dataset_id provided]
   • Load test case
   • Compare RAG output with ground_truth_answer
   • Calculate metrics

5. RETURN RESULTS
   {
     "answer": "...",
     "sources": [...],
     "evaluation": {
       "score": 0.95,
       "metrics": {...}
     }
   }

6. STREAMLIT DISPLAYS
   Answer + Evaluation scores
```

---

## Dataset Schema

### What Data Each Entry Has

```
┌─ Test Case
├─ id: unique identifier
├─ question: the query/question
├─ ground_truth_answer: expected correct answer
├─ context: supporting information
├─ difficulty_level: easy/medium/hard
├─ category: topic category
├─ expected_sources: source documents
└─ metadata: additional custom data

┌─ Dataset
├─ id: unique dataset identifier
├─ name: display name
├─ description: dataset purpose
├─ version: version number
├─ status: active/archived/deprecated
├─ domain: domain/category
├─ tags: classification tags
├─ test_case_count: number of test cases
├─ created_at: creation timestamp
└─ updated_at: last updated timestamp
```

---

## Common Scenarios

### Scenario 1: Check if Dataset Exists
```bash
python scripts/opik/dataset_management.py list-datasets | grep "automotive"
```

### Scenario 2: Get Test Case Count
```bash
python scripts/opik/dataset_management.py get-dataset --dataset-id <id> | grep "Test Cases"
```

### Scenario 3: Backup Dataset
```bash
python scripts/opik/dataset_management.py export-dataset \
  --dataset-id <id> \
  --output backup_$(date +%Y%m%d).json
```

### Scenario 4: Run Full Evaluation
```bash
python scripts/opik/dataset_management.py evaluate-dataset \
  --dataset-id <id> > evaluation_report.txt
```

### Scenario 5: Create Multiple Test Cases
```bash
# Create CSV with multiple rows
# Then import all at once
python scripts/opik/dataset_management.py add-from-csv \
  --dataset-id <id> \
  --file bulk_testcases.csv
```

---

## Troubleshooting

### Dataset Not Found
```bash
# Check all datasets
python scripts/opik/dataset_management.py list-datasets

# Verify dataset ID is correct
# Format: dataset_<name>_<timestamp>
```

### Test Cases Not Showing
```bash
# Check file exists
ls data/datasets/<dataset_id>/testcases.json

# Validate JSON format
python -m json.tool data/datasets/<dataset_id>/testcases.json
```

### Evaluation Not Working
```bash
# Verify RAG engine is running
curl http://localhost:8001/health

# Check dataset has test cases
python scripts/opik/dataset_management.py get-dataset --dataset-id <id>
```

---

## Key Points

✅ Datasets stored in: `data/datasets/`  
✅ Each dataset has: `metadata.json` + `testcases.json`  
✅ Test cases contain: Q&A pairs with expected answers  
✅ Evaluation optional when firing query  
✅ Scores calculated: exact match + semantic similarity  
✅ All operations via CLI: `python scripts/opik/dataset_management.py`  

---

Run `python scripts/opik/dataset_management.py --help` for full command reference!
