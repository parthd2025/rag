# OPIK Datasets Implementation Guide

**Status**: ✅ FULLY IMPLEMENTED  
**Date**: January 14, 2026  
**Component**: OPIK Datasets for RAG Evaluation

---

## Overview

The **Datasets** feature has been fully implemented to provide comprehensive test data management and automated evaluation capabilities for your RAG system. This is the first of four planned advanced OPIK features.

---

## What is OPIK Datasets?

OPIK Datasets enable you to:
- **Store benchmark data** - Create and manage test question-answer pairs
- **Track ground truth** - Store expected/ground truth answers for comparison
- **Evaluate RAG output** - Automatically test RAG responses against datasets
- **Regression testing** - Ensure consistent quality across updates
- **Version control** - Track multiple versions of test datasets
- **Sync to cloud** - Upload datasets to OPIK cloud for centralized management

---

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│          Dataset Management System                   │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │ Dataset Service  │◄────►│ Dataset Evaluator│    │
│  │                  │      │                  │    │
│  │ - CRUD ops       │      │ - Compare output │    │
│  │ - Storage        │      │ - Calculate score│    │
│  │ - Versioning     │      │ - Track metrics  │    │
│  └──────────────────┘      └──────────────────┘    │
│           ▲                                          │
│           │                                          │
│  ┌────────┴──────────┐      ┌──────────────────┐   │
│  │ Dataset Utils     │      │  Test Cases      │   │
│  │                   │      │                  │   │
│  │ - Validation      │      │ - Questions      │   │
│  │ - CSV/JSON parse  │      │ - Ground truth   │   │
│  │ - Format convert  │      │ - Metadata       │   │
│  └───────────────────┘      └──────────────────┘   │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │         FastAPI Endpoints                     │   │
│  │ (REST API for dataset management)            │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### File Structure

```
src/backend/services/
├── dataset_service.py          # Main dataset management
├── dataset_evaluation.py        # Evaluation framework
├── dataset_utils.py             # Utility functions
└── __init__.py

scripts/opik/
└── dataset_management.py        # CLI tool

data/
└── datasets/                    # Local storage
    ├── dataset_xxx/
    │   ├── metadata.json
    │   └── testcases.json
    └── dataset_yyy/
        ├── metadata.json
        └── testcases.json
```

---

## Core Data Models

### DatasetMetadata
```python
{
    "id": "dataset_automotive_test_1234567890",
    "name": "Automotive Q&A Dataset",
    "description": "Test dataset for automotive domain",
    "version": "1.0.0",
    "status": "active",  # draft, active, archived, deprecated
    "created_by": "system",
    "created_at": "2026-01-14T10:30:00",
    "updated_at": "2026-01-14T10:30:00",
    "test_case_count": 50,
    "tags": ["automotive", "production", "v1"],
    "domain": "automotive",
    "source": "internal",
    "evaluation_metrics": {},
    "opik_dataset_id": "opik_xyz123"  # OPIK cloud ID
}
```

### TestCase
```python
{
    "id": "tc_dataset_xxx_1234567890",
    "question": "What is the maintenance interval for Oil changes?",
    "ground_truth_answer": "Oil changes should be performed every 5,000 to 7,500 miles or every 6 months.",
    "context": "Optional context from source documents",
    "expected_sources": ["maintenance_manual.pdf", "service_guide.pdf"],
    "difficulty_level": "medium",  # easy, medium, hard
    "category": "maintenance",
    "metadata": {...},
    "created_at": "2026-01-14T10:30:00"
}
```

### EvaluationResult
```python
{
    "dataset_id": "dataset_xxx",
    "evaluation_timestamp": "2026-01-14T10:30:00",
    "test_case_count": 50,
    "passed": 45,
    "failed": 5,
    "accuracy": 90.0,  # percentage
    "metrics": {
        "accuracy_percent": 90.0,
        "pass_rate": 0.9,
        "fail_rate": 0.1
    },
    "details": [...]  # Per-test-case results
}
```

---

## REST API Endpoints

### Create Dataset
```
POST /datasets/create
Content-Type: application/json

{
    "name": "My Test Dataset",
    "description": "Dataset for evaluation",
    "version": "1.0.0",
    "domain": "automotive",
    "tags": ["test", "v1"]
}

Response (201):
{
    "status": "success",
    "dataset_id": "dataset_my_test_dataset_1234567890",
    "message": "Dataset 'My Test Dataset' created successfully"
}
```

### List Datasets
```
GET /datasets?status_filter=active

Response (200):
{
    "status": "success",
    "count": 3,
    "datasets": [
        {
            "id": "dataset_xxx",
            "name": "Dataset 1",
            "version": "1.0.0",
            "status": "active",
            "test_case_count": 50,
            ...
        },
        ...
    ]
}
```

### Get Dataset Details
```
GET /datasets/{dataset_id}

Response (200):
{
    "status": "success",
    "metadata": {...},
    "test_case_count": 50,
    "statistics": {
        "total_test_cases": 50,
        "difficulty_distribution": {
            "easy": 15,
            "medium": 25,
            "hard": 10
        },
        "category_distribution": {...},
        "created_at": "...",
        "updated_at": "..."
    }
}
```

### Add Test Case
```
POST /datasets/{dataset_id}/test-cases
Content-Type: application/json

{
    "question": "What maintenance is needed?",
    "ground_truth_answer": "Regular maintenance includes...",
    "context": "Optional context",
    "expected_sources": ["manual.pdf"],
    "difficulty_level": "medium",
    "category": "maintenance",
    "metadata": {}
}

Response (200):
{
    "status": "success",
    "dataset_id": "dataset_xxx",
    "message": "Test case added successfully",
    "data": {
        "test_case_id": "tc_dataset_xxx_1234567890"
    }
}
```

### Add Multiple Test Cases (Batch)
```
POST /datasets/{dataset_id}/test-cases/batch
Content-Type: application/json

{
    "test_cases": [
        {
            "question": "Q1?",
            "ground_truth_answer": "A1."
        },
        {
            "question": "Q2?",
            "ground_truth_answer": "A2."
        }
    ]
}

Response (200):
{
    "status": "success",
    "dataset_id": "dataset_xxx",
    "message": "Added 2 test cases successfully",
    "data": {
        "test_case_count": 2
    }
}
```

### Evaluate Dataset
```
POST /datasets/{dataset_id}/evaluate
Content-Type: application/json

{
    "dataset_id": "dataset_xxx",
    "metrics": ["exact_match", "semantic_similarity"]
}

Response (200):
{
    "status": "success",
    "dataset_id": "dataset_xxx",
    "evaluation": {
        "dataset_id": "dataset_xxx",
        "test_case_count": 50,
        "passed": 45,
        "failed": 5,
        "accuracy": 90.0,
        "metrics": {
            "accuracy_percent": 90.0,
            "pass_rate": 0.9,
            "fail_rate": 0.1
        },
        "details": [...]
    }
}
```

### Export Dataset
```
GET /datasets/{dataset_id}/export?format=json

Response (200):
{
    "status": "success",
    "dataset_id": "dataset_xxx",
    "format": "json",
    "data": {
        "metadata": {...},
        "test_cases": [...]
    }
}
```

### Update Dataset Status
```
PUT /datasets/{dataset_id}/status?status=active

Response (200):
{
    "status": "success",
    "dataset_id": "dataset_xxx",
    "message": "Dataset status updated to active"
}
```

### Sync to OPIK Cloud
```
POST /datasets/{dataset_id}/sync-opik

Response (200):
{
    "status": "success",
    "dataset_id": "dataset_xxx",
    "message": "Dataset synced to OPIK successfully",
    "data": {
        "opik_dataset_id": "opik_xyz123"
    }
}
```

---

## CLI Usage

The dataset management CLI provides command-line access to all dataset operations.

### Create Dataset
```bash
python scripts/opik/dataset_management.py create-dataset \
    --name "Automotive QA" \
    --description "Test dataset for automotive" \
    --version "1.0.0" \
    --domain "automotive" \
    --tags "test" "production"
```

### Add Test Case
```bash
python scripts/opik/dataset_management.py add-test-case \
    --dataset-id "dataset_automotive_qa_xxx" \
    --question "What is the oil change interval?" \
    --answer "Every 5,000 to 7,500 miles" \
    --difficulty "medium" \
    --category "maintenance"
```

### Add Multiple Test Cases from CSV
```bash
python scripts/opik/dataset_management.py add-from-csv \
    --dataset-id "dataset_xxx" \
    --file "testcases.csv"
```

CSV format required:
```
question,ground_truth_answer,difficulty_level,category
"Q1?","A1.",medium,general
"Q2?","A2.",easy,summary
```

### List All Datasets
```bash
python scripts/opik/dataset_management.py list-datasets
```

### Get Dataset Details
```bash
python scripts/opik/dataset_management.py get-dataset \
    --dataset-id "dataset_xxx"
```

### Export Dataset
```bash
python scripts/opik/dataset_management.py export-dataset \
    --dataset-id "dataset_xxx" \
    --output "exported_dataset.json" \
    --format "json"
```

### Import Dataset from File
```bash
python scripts/opik/dataset_management.py import-dataset \
    --file "mydata.json" \
    --name "Imported Dataset" \
    --description "Imported from file"
```

### Update Dataset Status
```bash
python scripts/opik/dataset_management.py update-status \
    --dataset-id "dataset_xxx" \
    --status "active"  # draft, active, archived, deprecated
```

### Sync to OPIK Cloud
```bash
python scripts/opik/dataset_management.py sync-to-opik \
    --dataset-id "dataset_xxx"
```

### Generate Sample Dataset
```bash
python scripts/opik/dataset_management.py generate-sample \
    --name "Sample Dataset" \
    --description "Sample for testing" \
    --count 5
```

### Show Test Case Template
```bash
python scripts/opik/dataset_management.py show-template
```

---

## Python API Usage

### Create and Manage Datasets
```python
from src.backend.services.dataset_service import DatasetService, DatasetStatus

# Initialize service
dataset_service = DatasetService(storage_path="data/datasets")

# Create dataset
dataset_id = dataset_service.create_dataset(
    name="My Dataset",
    description="Test dataset",
    version="1.0.0",
    domain="automotive"
)

# Add test cases
tc_id = dataset_service.add_test_case(
    dataset_id=dataset_id,
    question="What is the topic?",
    ground_truth_answer="The topic is...",
    difficulty_level="medium",
    category="general"
)

# Add multiple test cases
test_cases_data = [
    {
        "question": "Q1?",
        "ground_truth_answer": "A1.",
        "difficulty_level": "easy"
    },
    {
        "question": "Q2?",
        "ground_truth_answer": "A2.",
        "difficulty_level": "hard"
    }
]
tc_ids = dataset_service.add_test_cases_batch(dataset_id, test_cases_data)

# Get dataset
metadata = dataset_service.get_dataset(dataset_id)
test_cases = dataset_service.get_test_cases(dataset_id)

# Update status
dataset_service.update_dataset_status(dataset_id, DatasetStatus.ACTIVE)

# List datasets
all_datasets = dataset_service.list_datasets()
active_only = dataset_service.list_datasets(status=DatasetStatus.ACTIVE)

# Export
data = dataset_service.export_dataset(dataset_id, format="json")

# Get statistics
stats = dataset_service.get_statistics(dataset_id)
```

### Evaluate Datasets
```python
from src.backend.services.dataset_evaluation import DatasetEvaluator, EvaluationMetric

# Initialize evaluator
evaluator = DatasetEvaluator(dataset_service)

# Evaluate entire dataset
result = evaluator.evaluate_dataset(
    dataset_id=dataset_id,
    rag_engine=rag_engine,
    metrics=[EvaluationMetric.EXACT_MATCH, EvaluationMetric.SEMANTIC_SIMILARITY]
)

print(f"Accuracy: {result.accuracy}%")
print(f"Passed: {result.passed}/{result.test_case_count}")

# Get summary
summary = evaluator.get_evaluation_summary(dataset_id)

# Export results
exported = evaluator.export_results(dataset_id, format="json")
```

### Utility Functions
```python
from src.backend.services.dataset_utils import DatasetUtils

# Parse CSV
csv_content = open("data.csv").read()
test_cases = DatasetUtils.csv_to_test_cases(csv_content)

# Parse JSON
json_content = open("data.json").read()
test_cases = DatasetUtils.json_to_test_cases(json_content)

# Convert test cases to CSV
csv_output = DatasetUtils.test_cases_to_csv(test_cases)

# Convert to JSON
json_output = DatasetUtils.test_cases_to_json(test_cases)

# Get template
template = DatasetUtils.generate_test_case_template()

# Generate samples
samples = DatasetUtils.generate_sample_dataset(count=5)

# Calculate statistics
stats = DatasetUtils.calculate_statistics(test_cases)

# Validate structure
is_valid, errors = DatasetUtils.validate_dataset_structure(data)
```

---

## Evaluation Metrics

The dataset evaluator calculates the following metrics:

### Exact Match
- Compares predicted answer with ground truth
- Returns 1.0 if exact match (case-insensitive), 0.0 otherwise
- Most strict metric

### Semantic Similarity
- Uses token overlap (Jaccard similarity)
- Returns 0.0-1.0 based on word overlap
- More forgiving than exact match
- Can be extended with embedding-based similarity

### Accuracy
- Percentage of test cases that passed (score >= 0.5)
- Range: 0-100%

### Pass/Fail Rate
- Proportion of passed vs failed test cases
- Used for overall evaluation summary

---

## Data Flow

### Creating and Evaluating a Dataset

```
1. Create Dataset
   └─> DatasetMetadata created
   └─> Directory created in data/datasets/
   └─> metadata.json saved

2. Add Test Cases
   └─> TestCase objects created
   └─> testcases.json updated
   └─> Statistics recalculated

3. Evaluate Dataset
   ├─> For each test case:
   │   ├─> Query RAG system with question
   │   ├─> Get predicted answer
   │   ├─> Compare with ground truth
   │   ├─> Calculate metrics
   │   └─> Record result
   ├─> Aggregate metrics
   ├─> Store evaluation result in memory
   └─> Can export/analyze results

4. Optional: Sync to OPIK Cloud
   └─> Dataset uploaded to OPIK
   └─> OPIK dataset ID stored in metadata
   └─> Available in OPIK UI
```

---

## Storage Structure

### Local Storage
```
data/datasets/
├── dataset_automotive_test_1234567890/
│   ├── metadata.json           # Dataset metadata
│   └── testcases.json          # All test cases
│
├── dataset_general_qa_9876543210/
│   ├── metadata.json
│   └── testcases.json
│
└── ...
```

### OPIK Cloud Storage
- Optional sync to OPIK cloud
- Provides centralized management
- Enables web-based UI
- Automatic versioning and backup

---

## Usage Example: Complete Workflow

```python
from src.backend.services.dataset_service import DatasetService
from src.backend.services.dataset_evaluation import DatasetEvaluator
from src.backend.rag_engine import RAGEngine

# 1. Initialize services
dataset_service = DatasetService()
evaluator = DatasetEvaluator(dataset_service)
rag_engine = RAGEngine(...)

# 2. Create dataset
dataset_id = dataset_service.create_dataset(
    name="Automotive QA Benchmark",
    description="Benchmark dataset for automotive Q&A",
    domain="automotive"
)

# 3. Add test cases
test_cases_data = [
    {
        "question": "What is the recommended tire pressure?",
        "ground_truth_answer": "The recommended tire pressure is 32 PSI",
        "difficulty_level": "easy",
        "category": "maintenance"
    },
    {
        "question": "How often should filters be changed?",
        "ground_truth_answer": "Filters should be changed every 15,000-30,000 miles",
        "difficulty_level": "medium",
        "category": "maintenance"
    },
    # ... more test cases
]

dataset_service.add_test_cases_batch(dataset_id, test_cases_data)

# 4. Evaluate RAG system against dataset
result = evaluator.evaluate_dataset(dataset_id, rag_engine)

# 5. Analyze results
print(f"Accuracy: {result.accuracy}%")
print(f"Passed: {result.passed}/{result.test_case_count}")

# 6. Export dataset for sharing
data = dataset_service.export_dataset(dataset_id)

# 7. Optional: Sync to OPIK cloud
opik_id = dataset_service.sync_to_opik(dataset_id)
```

---

## Next Steps

After implementing Datasets, the next features to implement are:

1. **✅ Datasets** (COMPLETED)
2. **⬜ Experiments** - A/B testing different configurations
3. **⬜ Prompt Library** - Version control for prompts
4. **⬜ Optimization Studio** - Auto-optimize parameters

---

## Configuration

### Environment Variables

```env
# Optional OPIK configuration
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api
OPIK_WORKSPACE=your-workspace
OPIK_PROJECT_NAME=rag-system
OPIK_API_KEY=your-api-key
```

### Settings

Dataset storage location can be configured:
```python
# Default: data/datasets/
dataset_service = DatasetService(storage_path="custom/path")
```

---

## Troubleshooting

### Dataset Not Found
```
Error: Dataset not found: dataset_xxx
→ Use list-datasets to find correct ID
→ Check data/datasets/ directory
```

### Invalid Test Case
```
Error: Field 'question' must be non-empty string
→ Ensure question and ground_truth_answer are provided
→ Both fields must be non-empty strings
```

### OPIK Sync Failed
```
Error: OPIK client not available
→ Check OPIK connection/configuration
→ Verify OPIK_URL_OVERRIDE if using local instance
→ Can proceed without cloud sync
```

### CSV Parse Error
```
Error: CSV missing required columns
→ Ensure CSV has: question, ground_truth_answer
→ Check column headers match exactly
```

---

## Support & Documentation

- **API Docs**: Available at `/docs` (Swagger UI) when backend is running
- **Code**: `src/backend/services/dataset_*.py`
- **CLI**: `scripts/opik/dataset_management.py`
- **Tests**: Add tests in `tests/integration/`

---

## Summary

The **OPIK Datasets** feature is now fully integrated into your RAG system, providing:

✅ Complete dataset CRUD operations  
✅ Test case management with versioning  
✅ Automatic evaluation against RAG outputs  
✅ CSV/JSON import/export  
✅ OPIK cloud integration  
✅ REST API endpoints  
✅ CLI tool for all operations  
✅ Comprehensive statistics and metrics  

Ready for the next feature: **Experiments**!
