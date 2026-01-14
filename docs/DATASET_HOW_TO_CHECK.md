# 👁️ How to Check Dataset Entries - Visual Guide

## 🔍 Three Ways to View Dataset Entries

---

## Method 1: Using CLI Command (Easiest)

### View All Datasets
```bash
cd d:\RAG
python scripts/opik/dataset_management.py list-datasets
```

**Example Output:**
```
Datasets:
═══════════════════════════════════════════════════════════

1. ID: dataset_automotive_qa_1704871200123
   Name: Automotive Q&A
   Description: Test cases for automotive questions
   Version: 1.0.0
   Status: active
   Domain: automotive
   Tags: test, production, v1
   Test Cases: 50
   Created: 2025-01-10T09:30:00
   Updated: 2025-01-10T14:45:00

2. ID: dataset_general_qa_1704871500456
   Name: General Knowledge
   Description: General Q&A test dataset
   Version: 1.0.0
   Status: active
   Domain: general
   Tags: baseline
   Test Cases: 100
   Created: 2025-01-08T10:00:00
   Updated: 2025-01-09T16:20:00

3. ID: dataset_safety_1704872000789
   Name: Safety Guidelines
   Description: Safety-related QA
   Version: 2.0.0
   Status: active
   Domain: safety
   Tags: critical, v2
   Test Cases: 25
   Created: 2025-01-05T12:00:00
   Updated: 2025-01-10T11:30:00
```

---

### View Specific Dataset Details
```bash
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id dataset_automotive_qa_1704871200123
```

**Example Output:**
```
=== Dataset: Automotive Q&A ===
ID: dataset_automotive_qa_1704871200123
Description: Test cases for automotive questions
Version: 1.0.0
Status: active
Domain: automotive
Tags: test, production, v1
Test Cases: 50
Created: 2025-01-10T09:30:00
Updated: 2025-01-10T14:45:00

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
    "transmission": 10,
    "safety": 15,
    "performance": 13
  },
  "average_score": 0.87
}

--- First 5 Test Cases ---

1. Q: What is the maximum engine displacement?
   A: The maximum engine displacement is 5.0L
   Difficulty: easy, Category: engine
   Sources: [engine_manual.pdf]

2. Q: How does regenerative braking work?
   A: Regenerative braking recovers kinetic energy by...
   Difficulty: hard, Category: safety
   Sources: [braking_system.pdf, electrical_manual.pdf]

3. Q: What is the transmission fluid capacity?
   A: The transmission fluid capacity is 8.5 quarts
   Difficulty: medium, Category: transmission
   Sources: [transmission_manual.pdf]

4. Q: Explain the traction control system
   A: Traction control prevents wheel slippage by using sensors...
   Difficulty: hard, Category: safety
   Sources: [safety_manual.pdf]

5. Q: What is the recommended oil viscosity?
   A: The recommended oil viscosity is 5W-30
   Difficulty: easy, Category: engine
   Sources: [maintenance_guide.pdf]
```

---

## Method 2: View Raw Files Directly

### Navigate to Dataset Storage
```bash
cd d:\RAG\data\datasets
ls -la
```

**Directory Structure:**
```
data/datasets/
├── dataset_automotive_qa_1704871200123/
│   ├── metadata.json              (Dataset info)
│   └── testcases.json             (All test cases)
├── dataset_general_qa_1704871500456/
│   ├── metadata.json
│   └── testcases.json
└── dataset_safety_1704872000789/
    ├── metadata.json
    └── testcases.json
```

### View Metadata File
```bash
type data\datasets\dataset_automotive_qa_1704871200123\metadata.json
```

**Output (Formatted):**
```json
{
  "id": "dataset_automotive_qa_1704871200123",
  "name": "Automotive Q&A",
  "description": "Test cases for automotive questions",
  "version": "1.0.0",
  "status": "active",
  "domain": "automotive",
  "tags": ["test", "production", "v1"],
  "test_case_count": 50,
  "created_at": "2025-01-10T09:30:00",
  "updated_at": "2025-01-10T14:45:00"
}
```

### View Test Cases File
```bash
# View all test cases (pretty printed)
python -m json.tool data\datasets\dataset_automotive_qa_1704871200123\testcases.json | more
```

**Output (First 3 Test Cases):**
```json
[
  {
    "id": "tc_001",
    "question": "What is the maximum engine displacement?",
    "ground_truth_answer": "The maximum engine displacement is 5.0L",
    "context": "Engine specifications document",
    "difficulty_level": "easy",
    "category": "engine",
    "expected_sources": ["engine_manual.pdf"],
    "metadata": {
      "date_added": "2025-01-10",
      "author": "admin"
    }
  },
  {
    "id": "tc_002",
    "question": "How does regenerative braking work?",
    "ground_truth_answer": "Regenerative braking recovers kinetic energy by converting it to electrical energy that charges the battery",
    "context": "Advanced braking systems documentation",
    "difficulty_level": "hard",
    "category": "safety",
    "expected_sources": ["braking_system.pdf", "electrical_manual.pdf"],
    "metadata": {
      "date_added": "2025-01-10",
      "author": "tech_expert"
    }
  },
  {
    "id": "tc_003",
    "question": "What is the transmission fluid capacity?",
    "ground_truth_answer": "The transmission fluid capacity is 8.5 quarts",
    "context": "Transmission specifications",
    "difficulty_level": "medium",
    "category": "transmission",
    "expected_sources": ["transmission_manual.pdf"],
    "metadata": {
      "date_added": "2025-01-10",
      "author": "admin"
    }
  }
]
```

### Count Test Cases
```bash
python -c "import json; f=open('data/datasets/dataset_automotive_qa_1704871200123/testcases.json'); data=json.load(f); print(f'Total test cases: {len(data)}')"
```

**Output:**
```
Total test cases: 50
```

---

## Method 3: Programmatic Access (Python)

### Read Dataset with Python
```python
from src.backend.services.dataset_service import DatasetService
import json

# Initialize service
dataset_service = DatasetService()

# Get all datasets
print("All Datasets:")
print("═" * 50)
for dataset in dataset_service.get_all_datasets():
    print(f"Name: {dataset.name}")
    print(f"ID: {dataset.id}")
    print(f"Version: {dataset.version}")
    print(f"Test Cases: {len(dataset_service.get_test_cases(dataset.id))}")
    print()

# Get specific dataset
dataset_id = "dataset_automotive_qa_1704871200123"
dataset = dataset_service.get_dataset(dataset_id)

print(f"\nDataset Details: {dataset.name}")
print("═" * 50)
print(f"Description: {dataset.description}")
print(f"Domain: {dataset.domain}")
print(f"Tags: {', '.join(dataset.tags)}")

# Get test cases
test_cases = dataset_service.get_test_cases(dataset_id)
print(f"\nTotal Test Cases: {len(test_cases)}")
print("═" * 50)

# Print first 5
for idx, tc in enumerate(test_cases[:5], 1):
    print(f"\n{idx}. Question: {tc.question}")
    print(f"   Answer: {tc.ground_truth_answer}")
    print(f"   Difficulty: {tc.difficulty_level}")
    print(f"   Category: {tc.category}")

# Get statistics
stats = dataset_service.get_statistics(dataset_id)
print(f"\nStatistics:")
print("═" * 50)
print(json.dumps(stats, indent=2))
```

**Output:**
```
All Datasets:
==================================================
Name: Automotive Q&A
ID: dataset_automotive_qa_1704871200123
Version: 1.0.0
Test Cases: 50

Name: General Knowledge
ID: dataset_general_qa_1704871500456
Version: 1.0.0
Test Cases: 100

Name: Safety Guidelines
ID: dataset_safety_1704872000789
Version: 2.0.0
Test Cases: 25


Dataset Details: Automotive Q&A
==================================================
Description: Test cases for automotive questions
Domain: automotive
Tags: test, production, v1

Total Test Cases: 50
==================================================

1. Question: What is the maximum engine displacement?
   Answer: The maximum engine displacement is 5.0L
   Difficulty: easy
   Category: engine

2. Question: How does regenerative braking work?
   Answer: Regenerative braking recovers kinetic energy...
   Difficulty: hard
   Category: safety

3. Question: What is the transmission fluid capacity?
   Answer: The transmission fluid capacity is 8.5 quarts
   Difficulty: medium
   Category: transmission

4. Question: Explain the traction control system
   Answer: Traction control prevents wheel slippage...
   Difficulty: hard
   Category: safety

5. Question: What is the recommended oil viscosity?
   Answer: The recommended oil viscosity is 5W-30
   Difficulty: easy
   Category: engine

Statistics:
==================================================
{
  "total_test_cases": 50,
  "by_difficulty": {
    "easy": 15,
    "medium": 25,
    "hard": 10
  },
  "by_category": {
    "engine": 12,
    "transmission": 10,
    "safety": 15,
    "performance": 13
  },
  "average_score": 0.87
}
```

---

## 📊 Data Stored Per Entry

### Complete Test Case Structure
```
Every test case contains:
┌─────────────────────────────────┐
│ id                              │  Unique test case ID
├─────────────────────────────────┤
│ question                        │  The question to ask
├─────────────────────────────────┤
│ ground_truth_answer             │  Expected correct answer
├─────────────────────────────────┤
│ context                         │  Reference information
├─────────────────────────────────┤
│ difficulty_level                │  easy / medium / hard
├─────────────────────────────────┤
│ category                        │  Topic category
├─────────────────────────────────┤
│ expected_sources                │  Source documents
├─────────────────────────────────┤
│ metadata                        │  Custom data
│   ├─ date_added                 │  When added
│   ├─ author                     │  Who added it
│   └─ custom_field (optional)    │  Any custom data
└─────────────────────────────────┘
```

---

## 🔄 How Data Flows When Query is Fired

### Step-by-Step with Data

```
1. USER ENTERS QUERY IN STREAMLIT
   ┌────────────────────────────────┐
   │ Question: "What is max          │
   │ engine displacement?"           │
   └────────────────────────────────┘
                 ↓

2. BACKEND RECEIVES QUERY
   ┌────────────────────────────────┐
   │ POST /api/search               │
   │ {                              │
   │   "query": "What is max...",   │
   │   "dataset_id": "dataset_..." │
   │ }                              │
   └────────────────────────────────┘
                 ↓

3. RAG ENGINE PROCESSES
   ┌────────────────────────────────┐
   │ • Search FAISS index           │
   │ • Find relevant documents      │
   │ • Send to LLM with context     │
   │ • Get answer                   │
   └────────────────────────────────┘
                 ↓
         RAG Output: "The max is 5.0L"
                 ↓

4. DATASET PROVIDES TEST CASE
   ┌────────────────────────────────┐
   │ From data/datasets/            │
   │ Load: testcases.json           │
   │                                │
   │ Ground Truth:                  │
   │ "The maximum engine            │
   │  displacement is 5.0L"         │
   └────────────────────────────────┘
                 ↓

5. EVALUATE & COMPARE
   ┌────────────────────────────────┐
   │ RAG Output:  "The max is 5.0L" │
   │ GT Answer:   "The maximum      │
   │               engine           │
   │               displacement     │
   │               is 5.0L"         │
   │                                │
   │ Exact Match: 80%               │
   │ Semantic Sim: 100%             │
   │ Overall: 90%                   │
   │ Status: PASS ✓                 │
   └────────────────────────────────┘
                 ↓

6. RETURN TO STREAMLIT
   ┌────────────────────────────────┐
   │ {                              │
   │   "answer": "The max is 5.0L",│
   │   "sources": ["..."],          │
   │   "evaluation": {              │
   │     "score": 0.90,             │
   │     "passed": true,            │
   │     "metrics": {...}           │
   │   }                            │
   │ }                              │
   └────────────────────────────────┘
```

---

## 🎯 Quick Commands Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **List all datasets** | `python scripts/opik/dataset_management.py list-datasets` |
| **See dataset details** | `python scripts/opik/dataset_management.py get-dataset --dataset-id <id>` |
| **View metadata file** | `type data\datasets\<dataset_id>\metadata.json` |
| **View test cases** | `python -m json.tool data\datasets\<dataset_id>\testcases.json` |
| **Count test cases** | `python -c "import json; print(len(json.load(open('...'))))"` |
| **View first 10 cases** | `python -m json.tool ... \| head -100` |
| **Search in test cases** | `python -m json.tool ... \| grep "question"` |

---

## 📁 File Locations

**All datasets stored in:**
```
d:\RAG\data\datasets\
```

**Each dataset has:**
```
dataset_<name>_<timestamp>/
├── metadata.json          ← Dataset info (1-5 KB)
└── testcases.json         ← All test cases (varies by size)
```

---

## ✅ What You Can See

- ✅ Dataset ID, name, version
- ✅ Number of test cases
- ✅ Status (active/archived)
- ✅ Domain and tags
- ✅ Creation/update timestamps
- ✅ All questions in dataset
- ✅ All ground truth answers
- ✅ Difficulty levels
- ✅ Categories
- ✅ Source documents
- ✅ Custom metadata
- ✅ Statistics (by difficulty, category)

---

## 🚀 Best Practice

```bash
# 1. List all datasets
python scripts/opik/dataset_management.py list-datasets

# 2. Get details of one
python scripts/opik/dataset_management.py get-dataset --dataset-id <id>

# 3. View raw files if needed
type data\datasets\<id>\metadata.json
python -m json.tool data\datasets\<id>\testcases.json
```

That's it! You now know how to check everything in the dataset! 🎉
