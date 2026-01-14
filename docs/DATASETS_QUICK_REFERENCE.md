# 🚀 OPIK Datasets - Quick Reference Card

**Print this out or bookmark it!**

---

## REST API Quick Calls

### Create Dataset
```bash
curl -X POST http://localhost:8000/datasets/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Dataset Name","description":"Description"}'
```

### Add Test Case
```bash
curl -X POST http://localhost:8000/datasets/{DATASET_ID}/test-cases \
  -H "Content-Type: application/json" \
  -d '{"question":"Q?","ground_truth_answer":"A.","difficulty_level":"medium"}'
```

### Batch Add Test Cases
```bash
curl -X POST http://localhost:8000/datasets/{DATASET_ID}/test-cases/batch \
  -H "Content-Type: application/json" \
  -d '{"test_cases":[{"question":"Q1?","ground_truth_answer":"A1."},{"question":"Q2?","ground_truth_answer":"A2."}]}'
```

### List Datasets
```bash
curl http://localhost:8000/datasets
```

### Get Dataset Details
```bash
curl http://localhost:8000/datasets/{DATASET_ID}
```

### Evaluate Dataset
```bash
curl -X POST http://localhost:8000/datasets/{DATASET_ID}/evaluate \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"{DATASET_ID}","metrics":["exact_match","semantic_similarity"]}'
```

### Export Dataset
```bash
curl "http://localhost:8000/datasets/{DATASET_ID}/export?format=json" > exported.json
```

### Update Status
```bash
curl -X PUT "http://localhost:8000/datasets/{DATASET_ID}/status?status=active"
```

### Sync to OPIK
```bash
curl -X POST http://localhost:8000/datasets/{DATASET_ID}/sync-opik
```

---

## CLI Quick Commands

```bash
# Create
python scripts/opik/dataset_management.py create-dataset --name "Name" --description "Desc"

# Add test case
python scripts/opik/dataset_management.py add-test-case --dataset-id {ID} --question "Q?" --answer "A."

# List
python scripts/opik/dataset_management.py list-datasets

# Get details
python scripts/opik/dataset_management.py get-dataset --dataset-id {ID}

# Add from CSV
python scripts/opik/dataset_management.py add-from-csv --dataset-id {ID} --file data.csv

# Export
python scripts/opik/dataset_management.py export-dataset --dataset-id {ID} --output data.json

# Import
python scripts/opik/dataset_management.py import-dataset --file data.json --name "Name" --description "Desc"

# Update status
python scripts/opik/dataset_management.py update-status --dataset-id {ID} --status active

# Sync to OPIK
python scripts/opik/dataset_management.py sync-to-opik --dataset-id {ID}

# Generate sample
python scripts/opik/dataset_management.py generate-sample --name "Sample" --description "Demo" --count 5

# Show template
python scripts/opik/dataset_management.py show-template
```

---

## Python API Quick Examples

```python
from src.backend.services.dataset_service import DatasetService
from src.backend.services.dataset_evaluation import DatasetEvaluator

# Initialize
service = DatasetService()

# Create
ds_id = service.create_dataset("Name", "Description")

# Add test case
tc_id = service.add_test_case(ds_id, "Q?", "A.")

# Add multiple
service.add_test_cases_batch(ds_id, [
    {"question": "Q1?", "ground_truth_answer": "A1."},
    {"question": "Q2?", "ground_truth_answer": "A2."}
])

# Get
metadata = service.get_dataset(ds_id)
test_cases = service.get_test_cases(ds_id)
stats = service.get_statistics(ds_id)

# List
all_datasets = service.list_datasets()

# Update
service.update_dataset_status(ds_id, "active")

# Export
data = service.export_dataset(ds_id)

# Evaluate
evaluator = DatasetEvaluator(service)
result = evaluator.evaluate_dataset(ds_id, rag_engine)
print(f"Accuracy: {result.accuracy}%")

# Sync
opik_id = service.sync_to_opik(ds_id)
```

---

## CSV Format

```csv
question,ground_truth_answer,difficulty_level,category,context
"Q1?","Answer 1",easy,general,"Context 1"
"Q2?","Answer 2",medium,technical,"Context 2"
"Q3?","Answer 3",hard,explanation,"Context 3"
```

---

## JSON Format

```json
{
  "test_cases": [
    {
      "question": "Q?",
      "ground_truth_answer": "A.",
      "difficulty_level": "medium",
      "category": "general"
    }
  ]
}
```

---

## Key Concepts

| Term | Meaning |
|------|---------|
| Dataset | Collection of test cases |
| Test Case | Q&A pair with ground truth |
| Evaluation | Score RAG answers vs ground truth |
| Metric | How to measure answer quality |
| Accuracy | % of test cases passing |
| Status | Draft/Active/Archived/Deprecated |

---

## Statuses

| Status | Use | Description |
|--------|-----|-------------|
| draft | Development | Under creation/testing |
| active | Production | Ready for evaluation |
| archived | Historical | Older version kept for ref |
| deprecated | Legacy | No longer recommended |

---

## Difficulty Levels

| Level | Use | Examples |
|-------|-----|----------|
| easy | Simple | Factual, direct questions |
| medium | Standard | Common scenarios |
| hard | Complex | Multi-step, analytical |

---

## Evaluation Metrics

| Metric | Range | Meaning |
|--------|-------|---------|
| exact_match | 0.0-1.0 | Exact string match |
| semantic_similarity | 0.0-1.0 | Token overlap |
| accuracy | 0-100% | Pass rate |

---

## File Locations

| Item | Path |
|------|------|
| Datasets | `data/datasets/` |
| CLI Tool | `scripts/opik/dataset_management.py` |
| Services | `src/backend/services/dataset_*.py` |
| Docs | `docs/DATASETS_*.md` |
| API | `http://localhost:8000/docs` |

---

## Common Workflows

### Workflow 1: Create & Evaluate
```bash
# 1. Create
ID=$(python scripts/opik/dataset_management.py create-dataset --name "Test" | grep dataset | awk '{print $NF}')

# 2. Add data
python scripts/opik/dataset_management.py add-from-csv --dataset-id $ID --file data.csv

# 3. Evaluate via REST
curl -X POST http://localhost:8000/datasets/$ID/evaluate \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"'$ID'","metrics":["exact_match"]}'
```

### Workflow 2: Import & Export
```bash
# 1. Import from file
ID=$(python scripts/opik/dataset_management.py import-dataset --file backup.json --name "Restored" | grep dataset_restored | awk '{print $NF}')

# 2. Make changes (add/edit test cases)

# 3. Export
python scripts/opik/dataset_management.py export-dataset --dataset-id $ID --output backup_new.json
```

### Workflow 3: Sync to Cloud
```bash
# 1. Create locally
ID=$(python scripts/opik/dataset_management.py create-dataset --name "Cloud Ready" | grep dataset | awk '{print $NF}')

# 2. Add data
python scripts/opik/dataset_management.py add-test-case --dataset-id $ID --question "Q?" --answer "A."

# 3. Sync to OPIK
python scripts/opik/dataset_management.py sync-to-opik --dataset-id $ID
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Dataset not found | Use `list-datasets` to find correct ID |
| CSV parse error | Check CSV has `question` and `ground_truth_answer` |
| Evaluation fails | Ensure RAG engine is running |
| OPIK sync fails | Check OPIK connection/config |
| Port in use | Backend may not be running |

---

## Response Examples

### Create Response
```json
{
  "status": "success",
  "dataset_id": "dataset_name_1234567890",
  "message": "Dataset created successfully"
}
```

### Evaluate Response
```json
{
  "status": "success",
  "evaluation": {
    "test_case_count": 10,
    "passed": 9,
    "failed": 1,
    "accuracy": 90.0,
    "metrics": {...}
  }
}
```

---

## Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /datasets/create | Create |
| GET | /datasets | List |
| GET | /datasets/{id} | Get |
| POST | /datasets/{id}/test-cases | Add |
| POST | /datasets/{id}/test-cases/batch | Batch |
| POST | /datasets/{id}/evaluate | Evaluate |
| GET | /datasets/{id}/export | Export |
| PUT | /datasets/{id}/status | Update |
| POST | /datasets/{id}/sync-opik | Sync |

---

## Help & Links

| Resource | Link |
|----------|------|
| API Docs | `http://localhost:8000/docs` |
| Quick Start | `docs/DATASETS_QUICKSTART.md` |
| Full Guide | `docs/DATASETS_IMPLEMENTATION.md` |
| Summary | `docs/DATASETS_SUMMARY.md` |
| CLI Help | `python scripts/opik/dataset_management.py --help` |

---

## Quick Tips

💡 **Tip 1**: Use CLI for one-off operations, REST API for automation  
💡 **Tip 2**: CSV is best for bulk import, REST API for single adds  
💡 **Tip 3**: Always set status to "active" before evaluation  
💡 **Tip 4**: Export datasets regularly for backup  
💡 **Tip 5**: Use OPIK sync for team collaboration  

---

## Next Steps

→ Create your first dataset  
→ Add test cases  
→ Run evaluation  
→ Review results  
→ Iterate & improve  

---

**Print or bookmark this page! 🔖**

For full details, see `docs/DATASETS_IMPLEMENTATION.md`
