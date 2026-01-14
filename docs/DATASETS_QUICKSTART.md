# Quick Start: OPIK Datasets

**Get started with dataset management in 5 minutes!**

---

## Setup (First Time Only)

No additional setup needed! The dataset service is automatically initialized when the backend starts.

---

## Quick Examples

### 1️⃣ Create Your First Dataset (REST API)

```bash
curl -X POST http://localhost:8000/datasets/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Dataset",
    "description": "Test dataset for evaluation",
    "domain": "general"
  }'
```

**Response:**
```json
{
  "status": "success",
  "dataset_id": "dataset_my_first_dataset_1234567890",
  "message": "Dataset 'My First Dataset' created successfully"
}
```

Save the `dataset_id` for next steps!

---

### 2️⃣ Add Test Cases

#### Method 1: One at a Time (REST API)

```bash
curl -X POST http://localhost:8000/datasets/{dataset_id}/test-cases \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "ground_truth_answer": "The main topic is about...",
    "difficulty_level": "medium",
    "category": "general"
  }'
```

#### Method 2: Batch Add (REST API)

```bash
curl -X POST http://localhost:8000/datasets/{dataset_id}/test-cases/batch \
  -H "Content-Type: application/json" \
  -d '{
    "test_cases": [
      {
        "question": "Question 1?",
        "ground_truth_answer": "Answer 1."
      },
      {
        "question": "Question 2?",
        "ground_truth_answer": "Answer 2."
      }
    ]
  }'
```

#### Method 3: From CSV File (CLI)

Create `my_tests.csv`:
```csv
question,ground_truth_answer,difficulty_level,category
"What is X?","X is...",easy,general
"Explain Y?","Y means...",medium,explanation
"How does Z work?","Z works by...",hard,technical
```

Then:
```bash
python scripts/opik/dataset_management.py add-from-csv \
  --dataset-id "dataset_my_first_dataset_xxx" \
  --file "my_tests.csv"
```

---

### 3️⃣ View Dataset

```bash
# CLI method
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id "dataset_my_first_dataset_xxx"

# REST API method
curl http://localhost:8000/datasets/dataset_my_first_dataset_xxx
```

---

### 4️⃣ Evaluate Dataset Against RAG

```bash
curl -X POST http://localhost:8000/datasets/{dataset_id}/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_my_first_dataset_xxx",
    "metrics": ["exact_match", "semantic_similarity"]
  }'
```

**Response includes:**
- Total test cases
- Passed/failed count
- Accuracy percentage
- Per-test-case results

---

### 5️⃣ Export Dataset

```bash
# Export as JSON
curl -X GET "http://localhost:8000/datasets/{dataset_id}/export?format=json" \
  > exported_dataset.json

# Or via CLI
python scripts/opik/dataset_management.py export-dataset \
  --dataset-id "dataset_xxx" \
  --output "backup.json"
```

---

## CLI Quick Reference

```bash
# Create dataset
python scripts/opik/dataset_management.py create-dataset \
  --name "My Dataset" \
  --description "Description here"

# Add test case
python scripts/opik/dataset_management.py add-test-case \
  --dataset-id "dataset_xxx" \
  --question "Q?" \
  --answer "A."

# List all datasets
python scripts/opik/dataset_management.py list-datasets

# Get details
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id "dataset_xxx"

# Add from CSV
python scripts/opik/dataset_management.py add-from-csv \
  --dataset-id "dataset_xxx" \
  --file "data.csv"

# Export
python scripts/opik/dataset_management.py export-dataset \
  --dataset-id "dataset_xxx" \
  --output "data.json"

# Import
python scripts/opik/dataset_management.py import-dataset \
  --file "data.json" \
  --name "Imported" \
  --description "From file"

# Update status
python scripts/opik/dataset_management.py update-status \
  --dataset-id "dataset_xxx" \
  --status "active"

# Generate sample
python scripts/opik/dataset_management.py generate-sample \
  --name "Sample" \
  --description "Sample data" \
  --count 5

# Show template
python scripts/opik/dataset_management.py show-template
```

---

## Sample Workflow

```bash
# 1. Create dataset
DATASET_ID=$(python scripts/opik/dataset_management.py create-dataset \
  --name "AutoTest" \
  --description "Automotive Q&A test" \
  --domain "automotive" \
  | grep "dataset_" | awk '{print $NF}')

# 2. Add test data from CSV
python scripts/opik/dataset_management.py add-from-csv \
  --dataset-id "$DATASET_ID" \
  --file "automotive_qa.csv"

# 3. View dataset
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id "$DATASET_ID"

# 4. Evaluate (via REST API)
curl -X POST "http://localhost:8000/datasets/$DATASET_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"'$DATASET_ID'","metrics":["exact_match","semantic_similarity"]}'

# 5. Export results
python scripts/opik/dataset_management.py export-dataset \
  --dataset-id "$DATASET_ID" \
  --output "results_${DATASET_ID}.json"
```

---

## Python API Quick Example

```python
from src.backend.services.dataset_service import DatasetService
from src.backend.services.dataset_evaluation import DatasetEvaluator

# Initialize
service = DatasetService()
evaluator = DatasetEvaluator(service)

# Create dataset
ds_id = service.create_dataset(
    name="Python Example",
    description="Created from Python code"
)

# Add test cases
service.add_test_case(
    dataset_id=ds_id,
    question="What is X?",
    ground_truth_answer="X is..."
)

# Get dataset
metadata = service.get_dataset(ds_id)
test_cases = service.get_test_cases(ds_id)

# View statistics
stats = service.get_statistics(ds_id)
print(f"Total test cases: {stats['total_test_cases']}")
print(f"Difficulty: {stats['difficulty_distribution']}")

# Evaluate (if RAG engine available)
# result = evaluator.evaluate_dataset(ds_id, rag_engine)
# print(f"Accuracy: {result.accuracy}%")
```

---

## Test Data Templates

### CSV Format
```csv
question,ground_truth_answer,difficulty_level,category,context
"What is X?","X is defined as...",easy,definition,"Context about X"
"How does Y work?","Y works by...",medium,mechanism,"More details"
"Compare A and B?","A and B differ in...",hard,comparison,"Background info"
```

### JSON Format
```json
{
  "test_cases": [
    {
      "question": "What is X?",
      "ground_truth_answer": "X is...",
      "difficulty_level": "easy",
      "category": "definition"
    },
    {
      "question": "How does Y work?",
      "ground_truth_answer": "Y works by...",
      "difficulty_level": "medium",
      "category": "mechanism"
    }
  ]
}
```

---

## Status Codes

| Status | Meaning |
|--------|---------|
| `draft` | Not yet ready for evaluation |
| `active` | Ready for use and evaluation |
| `archived` | Old version, kept for reference |
| `deprecated` | No longer recommended |

---

## Common Tasks

### Check All Datasets
```bash
python scripts/opik/dataset_management.py list-datasets
```

### Get Dataset Statistics
```bash
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id "dataset_xxx"
```

### Update Status to Active
```bash
python scripts/opik/dataset_management.py update-status \
  --dataset-id "dataset_xxx" \
  --status "active"
```

### Sync to OPIK Cloud
```bash
python scripts/opik/dataset_management.py sync-to-opik \
  --dataset-id "dataset_xxx"
```

### Generate Test Data for Demo
```bash
python scripts/opik/dataset_management.py generate-sample \
  --name "Demo Dataset" \
  --description "Sample for demonstration" \
  --count 10
```

---

## Next Steps

1. ✅ **Create your first dataset** - Start with the examples above
2. ✅ **Add test cases** - From CSV or one by one
3. ✅ **Evaluate your RAG** - See how well it performs
4. 📊 **Analyze results** - Export and review metrics
5. 🔄 **Iterate & improve** - Create new datasets, refine evaluation

Then explore the next OPIK feature: **Experiments** (coming soon)!

---

## Need Help?

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Full Guide**: See `docs/DATASETS_IMPLEMENTATION.md`
- **Code**: `src/backend/services/dataset_*.py`
- **Examples**: Check the CLI code in `scripts/opik/dataset_management.py`

---

**Happy evaluating! 🚀**
