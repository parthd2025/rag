# 📌 Dataset Overview - Simple Explanation

## Your Question Answered

> **"How to check the dataset and which entries are getting stored in and how? If I fire a query in streamlit then what will be the dataset role in the whole process?"**

---

## 🎯 Quick Summary

### What is Dataset?
A **collection of test cases** (question-answer pairs with expected answers)

### Where is it Stored?
`data/datasets/` folder with JSON files

### What Gets Stored?
- Questions
- Expected/correct answers
- Context/reference info
- Difficulty level (easy/medium/hard)
- Category/topic
- Source documents

### Dataset's Role When You Fire Query:

```
Query in Streamlit
        ↓
    RAG Engine generates answer
        ↓
[OPTIONAL] Dataset evaluates: "Is the RAG answer correct?"
        ↓
Returns evaluation score (0-100%)
```

---

## 📊 How to Check Dataset

### Option 1: Via Command (Easiest)
```bash
# See all datasets
python scripts/opik/dataset_management.py list-datasets

# See details of one dataset
python scripts/opik/dataset_management.py get-dataset --dataset-id <id>
```

### Option 2: View Files Directly
```bash
# See storage location
ls data\datasets\

# View metadata
type data\datasets\dataset_xyz\metadata.json

# View test cases
python -m json.tool data\datasets\dataset_xyz\testcases.json
```

### Option 3: Use Python
```python
from src.backend.services.dataset_service import DatasetService

service = DatasetService()
datasets = service.get_all_datasets()
for ds in datasets:
    test_cases = service.get_test_cases(ds.id)
    print(f"{ds.name}: {len(test_cases)} test cases")
```

---

## 📈 Example: Real Data Stored

### Dataset 1: Automotive Q&A
```
Stored Location: data/datasets/dataset_automotive_qa_1704871200123/

Test Cases (Examples):
1. Q: "What is the maximum engine displacement?"
   A: "The maximum engine displacement is 5.0L"
   Difficulty: easy
   Category: engine

2. Q: "How does regenerative braking work?"
   A: "Regenerative braking recovers kinetic energy..."
   Difficulty: hard
   Category: safety

3. Q: "What is transmission fluid capacity?"
   A: "The transmission fluid capacity is 8.5 quarts"
   Difficulty: medium
   Category: transmission

Total: 50 test cases
```

---

## 🔄 Query Flow with Dataset Role

### When User Fires Query in Streamlit:

**Step 1: User Enters Query**
```
Streamlit: "What is the maximum engine displacement?"
```

**Step 2: Backend Processes (RAG Engine)**
```
1. Search FAISS index for relevant documents
2. Send query + context to LLM (Groq)
3. Get answer: "The max is 5.0L"
```

**Step 3: Dataset Evaluates (If Provided)**
```
Load test case from dataset:
  Question: "What is the maximum engine displacement?"
  Ground Truth: "The maximum engine displacement is 5.0L"

Compare:
  RAG Answer: "The max is 5.0L"
  Ground Truth: "The maximum engine displacement is 5.0L"

Calculate Score:
  Exact Match: 80%
  Semantic Similarity: 100%
  Overall: 90%
  
Result: PASS ✓
```

**Step 4: Return to Streamlit**
```
{
  "answer": "The max is 5.0L",
  "evaluation": {
    "passed": true,
    "score": 0.90,
    "metrics": {
      "exact_match": 0.8,
      "semantic_similarity": 1.0
    }
  }
}
```

**Step 5: Display in UI**
```
┌─────────────────────────────┐
│ Answer: The max is 5.0L     │
│ ✓ Correct (Score: 90%)      │
│                             │
│ Exact Match: 80%            │
│ Semantic Sim: 100%          │
└─────────────────────────────┘
```

---

## 💾 What Exactly Gets Stored

### Per Test Case
```
id                    → Unique identifier
question              → The question
ground_truth_answer   → Expected answer
context              → Reference information
difficulty_level     → easy/medium/hard
category             → Topic/subject
expected_sources     → Source documents
metadata             → Custom data (date, author, etc.)
```

### Per Dataset
```
id                   → Unique dataset ID
name                 → Dataset name
description          → What it's for
version              → Version number
status               → active/archived/deprecated
domain               → Domain/category
tags                 → Classification tags
test_case_count      → How many test cases
created_at           → Creation date
updated_at           → Last update date
```

---

## 🗂️ Storage Structure

```
data/datasets/                          ← All datasets here
│
├── dataset_automotive_qa_1704871200123/
│   ├── metadata.json                   ← Dataset info
│   └── testcases.json                  ← All test cases
│
├── dataset_general_qa_1704871500456/
│   ├── metadata.json
│   └── testcases.json
│
└── dataset_safety_1704872000789/
    ├── metadata.json
    └── testcases.json
```

---

## 🎮 Dataset's Role in Query Process

| Phase | What Happens | Dataset Role |
|-------|-------------|--------------|
| **Before Query** | User enters question | Waits (ready for evaluation) |
| **RAG Processing** | Engine retrieves docs + LLM generates | Inactive |
| **After Answer** | RAG produces output | **ACTIVE** - Evaluates output |
| **Evaluation** | Scores calculated | **Provides ground truth** |
| **Result** | User sees answer + score | Comparison complete |

**Key Point**: Dataset is **optional**. Query works without it, but with dataset you get evaluation scores showing if answer is correct.

---

## ✨ Key Features

✅ **Easy to Check**: Single CLI command shows everything  
✅ **Well Organized**: Stored in dedicated `data/datasets/` folder  
✅ **Versioned**: Each dataset has version number  
✅ **Categorized**: Questions grouped by difficulty and category  
✅ **Flexible**: Can add from CLI, CSV, or API  
✅ **Evaluates**: Automatically scores RAG output  
✅ **Optional**: Works with or without dataset  

---

## 🚀 Common Tasks

### Check if Dataset Exists
```bash
python scripts/opik/dataset_management.py list-datasets
```

### See What's in a Dataset
```bash
python scripts/opik/dataset_management.py get-dataset --dataset-id <id>
```

### Add Test Cases
```bash
python scripts/opik/dataset_management.py add-test-case \
  --dataset-id <id> \
  --question "Q?" \
  --answer "A."
```

### Evaluate Entire Dataset
```bash
python scripts/opik/dataset_management.py evaluate-dataset \
  --dataset-id <id>
```

---

## 📚 Related Documentation

- [DATASET_QUERY_FLOW.md](DATASET_QUERY_FLOW.md) - Detailed flow explanation
- [DATASET_COMMANDS_REFERENCE.md](DATASET_COMMANDS_REFERENCE.md) - All commands
- [DATASET_HOW_TO_CHECK.md](DATASET_HOW_TO_CHECK.md) - Visual guide to checking datasets
- [DATASETS_IMPLEMENTATION.md](DATASETS_IMPLEMENTATION.md) - Implementation details

---

## ❓ FAQ

**Q: Is dataset required?**  
A: No, it's optional. Queries work without it.

**Q: Can I fire query without dataset?**  
A: Yes, you'll get answer but no evaluation score.

**Q: What does evaluation score mean?**  
A: How similar RAG output is to expected answer (0-100%).

**Q: Where is data stored?**  
A: `data/datasets/` folder with JSON files.

**Q: How many entries can I store?**  
A: Unlimited. Limited only by disk space.

**Q: Can I export dataset?**  
A: Yes, to JSON or CSV format.

**Q: Can I import dataset?**  
A: Yes, from JSON or CSV files.

**Q: Does evaluation slow down queries?**  
A: Slightly (optional, disabled by default).

---

## 🎯 Bottom Line

**Dataset's Role in RAG Query Process:**

1. **Stores**: Test cases with questions and expected answers
2. **Located**: `data/datasets/` folder
3. **Usage**: Optional evaluation of RAG output
4. **Evaluation**: Scores how accurate RAG answer is
5. **Query Flow**: Query → RAG generates → Dataset evaluates → Return score

That's it! Simple as that! 🎉

---

For more details, see:
- [DATASET_QUERY_FLOW.md](DATASET_QUERY_FLOW.md) for detailed flow
- [DATASET_COMMANDS_REFERENCE.md](DATASET_COMMANDS_REFERENCE.md) for all commands
- [DATASET_HOW_TO_CHECK.md](DATASET_HOW_TO_CHECK.md) for how to view entries
