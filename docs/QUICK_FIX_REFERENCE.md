# ⚡ Quick Reference: Query Auto-Logging

## The Issue You Reported
```
OPIK Screenshot showed:
- Dataset: Rag-system-db
- Items: 1 of 1 (no new queries appearing)

Expected: Queries from Streamlit should appear in OPIK
Actual: They weren't being logged
```

## The Fix I Implemented
```
Added automatic query logging to /chat endpoint

Now EVERY query from Streamlit:
1. Gets saved to: data/datasets/production_queries/
2. Gets sent to OPIK: parth-d/rag-system-db
3. Appears in OPIK dashboard in ~10 seconds
```

## What Changed
```
File: src/backend/main.py

✨ Added Step 5: Auto-save query to local dataset
✨ Added Step 5B: Auto-log query to OPIK Cloud

That's it! Simple & effective.
```

---

## 3-Step Verification

### Step 1: Restart Backend ⭐ DO THIS FIRST
```bash
# In terminal with uvicorn:
Ctrl+C

# Then restart:
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001
```

### Step 2: Fire Test Query
```
1. Go to Streamlit: http://localhost:8501
2. Ask any question
3. Wait for answer
```

### Step 3: Verify in OPIK
```
1. Go to: https://www.comet.com/opik
2. Navigate: Datasets > rag-system-db > Items
3. See your new query ✅ (wait ~10 seconds if needed)
```

---

## What You'll See in Logs

```
After restart, when you fire a query:

INFO: CHAT STEP 5: Auto-logging query to local dataset...
INFO: CHAT STEP 5 COMPLETE: Query logged to local dataset
INFO: CHAT STEP 5B: Auto-logging query to OPIK Cloud...
INFO: CHAT STEP 5B COMPLETE: Query logged to OPIK Cloud
```

---

## Local Verification

```bash
# Check if dataset folder created:
ls data\datasets\

# Should show: production_queries

# View your queries:
python -m json.tool data\datasets\production_queries\testcases.json
```

---

## Expected OPIK Result

### Before:
```
Rag-system-db
└── Items: 1 of 1
```

### After Your First Query:
```
Rag-system-db
└── Items: 1 of 2 ✨ (NEW!)
    ├── Old setup item
    └── Your query today
```

---

## If It Doesn't Work

### Check Logs First
```
Look for error messages with "CHAT STEP 5"
in the backend terminal
```

### Did you restart?
```
❌ If no → Restart backend first!
✅ If yes → Check logs for errors
```

### Check Environment
```bash
echo $OPIK_WORKSPACE    # Should show: parth-d
echo $OPIK_ENABLED      # Should be: true (or missing)
```

---

## File Locations

| What | Where |
|------|-------|
| Code changed | `src/backend/main.py` |
| Local queries stored | `data/datasets/production_queries/` |
| OPIK Cloud | `parth-d/rag-system-db` |
| This guide | `docs/QUERY_LOGGING_SUMMARY.md` |
| Detailed explanation | `docs/OPIK_QUERY_TRACKING_ISSUE.md` |
| Implementation details | `docs/OPIK_AUTO_LOGGING_IMPLEMENTATION.md` |

---

## Commands Reference

```bash
# Restart backend
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001

# View stored queries
python -m json.tool data\datasets\production_queries\testcases.json

# List datasets
python scripts/opik/dataset_management.py list-datasets

# Get production queries
python scripts/opik/dataset_management.py get-dataset \
  --dataset-id production_queries
```

---

## Success Criteria ✅

- [ ] Backend restarted
- [ ] Test query fired in Streamlit
- [ ] Logs show "CHAT STEP 5 COMPLETE"
- [ ] `data/datasets/production_queries/` folder exists
- [ ] `testcases.json` contains your query
- [ ] OPIK shows new item in dataset (after 10 seconds)

---

## TL;DR

**Problem:** Queries not logging to OPIK  
**Cause:** No auto-logging code in backend  
**Solution:** Added auto-logging to `/chat` endpoint  
**Action:** Restart backend + fire test query  
**Result:** Queries appear in OPIK within 10 seconds ✨

---

**You're 1 step away:** Just restart the backend! 🚀
