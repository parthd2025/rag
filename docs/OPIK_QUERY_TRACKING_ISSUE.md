# 🔴 OPIK Query Tracking Issue - Diagnosis & Solution

## Problem Summary

**Your queries from Streamlit are NOT being automatically logged to your OPIK dataset.**

In the OPIK screenshot, you see:
- Dataset: `Rag-system-db`
- Only **1 item** visible (should have multiple from your recent queries)
- Status: Showing "1 of 1" items

This means the query-to-OPIK logging is not working.

---

## Root Cause Analysis

### What's Happening Currently:

```
Streamlit Frontend
        ↓ (User fires query)
        ↓
Backend /chat endpoint
        ↓ (Processes query with RAG)
        ↓
RAG Engine generates answer
        ↓
Returns response to Streamlit
        ↓
❌ NO automatic OPIK logging of this query
        ↓
OPIK Dataset remains unchanged
```

### Why This Happens:

The backend has **3 service layers** but NONE are configured to auto-log queries to OPIK:

1. **TrackedRAGService** (/chat endpoint uses this)
   - Purpose: Track query execution in OPIK
   - Status: ⚠️ NOT configured to log query as dataset item
   - Issue: Tracks execution flow but doesn't store query as test case

2. **DatasetService** (data/datasets/)
   - Purpose: Store test cases locally
   - Status: ✅ Works for local storage
   - Issue: Only stores data when explicitly called via API endpoint

3. **DatasetEvaluator** 
   - Purpose: Evaluate RAG output against ground truth
   - Status: ✅ Works when evaluation is requested
   - Issue: Doesn't auto-trigger on every query

### Missing Integration:

```python
# Current flow (in /chat endpoint):
@app.post("/chat")
async def chat(req: QueryRequest):
    result = await tracked_rag_service.process_query(
        query=req.question,
        top_k=current_top_k,
        temperature=current_temperature
    )
    return QueryResponse(answer=result["answer"], sources=result.get("sources", []))

# ❌ MISSING:
# The query/answer pair should ALSO be stored in dataset/OPIK
# Currently: NO code to save query to dataset or OPIK
```

---

## Solution: Add Query Auto-Logging to OPIK

I'll implement automatic logging of every query to OPIK. Here are the options:

### Option 1: **Automatic Local Dataset Storage (Simple)**
Every query is saved as a test case in your local `data/datasets/` folder.

```python
# In /chat endpoint:
response = await tracked_rag_service.process_query(query, ...)

# NEW: Auto-log to local dataset
dataset_service.add_test_case(
    dataset_id="default_queries",
    question=req.question,
    ground_truth_answer=response["answer"],
    sources=response.get("sources", []),
    metadata={"timestamp": datetime.now(), "confidence": ...}
)
```

**Pros:**
- ✅ Simple to implement (5 lines of code)
- ✅ No OPIK Cloud required
- ✅ All queries tracked locally

**Cons:**
- ❌ Doesn't appear in OPIK Cloud immediately
- ❌ Requires separate local dataset management

---

### Option 2: **Direct OPIK Cloud Logging (Recommended)**
Every query is logged directly to OPIK in real-time.

```python
# In /chat endpoint:
response = await tracked_rag_service.process_query(query, ...)

# NEW: Auto-log to OPIK
opik_manager.client.log_item(
    project_name="rag-system",
    dataset_name="rag-system-db",
    data={
        "question": req.question,
        "answer": response["answer"],
        "sources": response.get("sources", []),
        "timestamp": datetime.now()
    }
)
```

**Pros:**
- ✅ Appears in OPIK Cloud immediately (like your screenshot)
- ✅ No local storage needed
- ✅ Seamless integration

**Cons:**
- ❌ Requires OPIK Cloud connection
- ⚠️ Adds slight latency to responses (~100ms)

---

### Option 3: **Hybrid Approach (Best)**
Queries logged to BOTH local dataset AND OPIK Cloud.

```python
# In /chat endpoint:
response = await tracked_rag_service.process_query(query, ...)

# NEW: Log to both
dataset_service.add_test_case(...)  # Local
opik_manager.client.log_item(...)   # OPIK Cloud
```

**Pros:**
- ✅ Backup: Works even if OPIK Cloud is down
- ✅ Local: Can query locally without network
- ✅ OPIK: Real-time tracking in Cloud

---

## Implementation Path

I recommend **Option 3 (Hybrid)** for maximum reliability.

### Step 1: Modify `/chat` endpoint in main.py

Add query logging after getting response:

```python
@app.post("/chat", response_model=QueryResponse)
async def chat(req: QueryRequest) -> QueryResponse:
    """Chat with RAG system - now with auto-logging to OPIK."""
    
    # ... existing validation code ...
    
    # Process query
    result = await tracked_rag_service.process_query(
        query=req.question,
        top_k=current_top_k,
        temperature=current_temperature
    )
    
    # NEW: Auto-log query to datasets
    try:
        # Log to local dataset
        dataset_service.add_test_case(
            dataset_id="default_production_queries",
            question=req.question,
            ground_truth_answer=result["answer"],
            context="\n".join([s.get("chunk_preview", "") for s in result.get("sources", [])]),
            expected_sources=[s.get("document_name") for s in result.get("sources", [])],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "sources_count": len(result.get("sources", [])),
                "response_time": result.get("processing_time", 0)
            }
        )
        logger.info(f"Query logged to local dataset")
    except Exception as e:
        logger.warning(f"Failed to log query to local dataset: {e}")
    
    # Log to OPIK Cloud (if available)
    try:
        opik_manager = get_opik_manager()
        if opik_manager and opik_manager.available:
            opik_manager.client.log_item(
                project_name=opik_manager.config.project_name,
                dataset_name="rag-system-db",
                data={
                    "question": req.question,
                    "answer": result["answer"],
                    "sources": [s.get("document_name") for s in result.get("sources", [])],
                }
            )
            logger.info(f"Query logged to OPIK Cloud")
    except Exception as e:
        logger.warning(f"Failed to log query to OPIK: {e}")
    
    return QueryResponse(answer=result["answer"], sources=result.get("sources", []))
```

### Step 2: Verify OPIK Configuration

Check your environment variables:

```bash
# Should be set to your OPIK workspace
echo $OPIK_WORKSPACE          # Should show: parth-d
echo $OPIK_PROJECT_NAME       # Should show: rag-system
echo $OPIK_API_KEY            # Should be your API key (not shown for security)
```

### Step 3: Create Default Dataset (if needed)

```bash
# Create a dataset to store production queries
python scripts/opik/dataset_management.py create-dataset \
  --name "production-queries" \
  --description "All queries from Streamlit interface" \
  --domain "production"
```

### Step 4: Test the Integration

1. **Fire a query in Streamlit** ✅
2. **Wait 5-10 seconds**
3. **Check OPIK Cloud** → You should see the new item in "Rag-system-db"

---

## Current Issues Preventing Auto-Logging

### Issue 1: No Dataset ID Default
```python
# Current: Requires explicit dataset_id
dataset_service.add_test_case(dataset_id="???", ...)

# Should be: Use default if not provided
dataset_service.add_test_case(dataset_id="default", ...)
```

### Issue 2: OPIK Client Not Exposed
```python
# Current: opik_manager is internal, hard to access
opik_manager = get_opik_manager()  # Private/internal usage

# Should be: Properly exposed for logging
```

### Issue 3: No Query Logging Hook
```python
# Current: /chat endpoint has NO logging hook for queries
@app.post("/chat")
async def chat(req):
    # ... processes query ...
    # ❌ MISSING: dataset_service.add_test_case(...)
    return response

# Should be: Auto-log every query
@app.post("/chat")
async def chat(req):
    response = process_query(req.question)
    log_to_dataset(req.question, response)  # ✅ NEW
    return response
```

---

## Why Only 1 Item in OPIK?

That single item was likely:
1. **Created manually** via CLI or API
2. **Created when you first set up** the dataset
3. **Logged from a test or demo** script

But queries from your Streamlit frontend are **NOT being added** because there's no automatic logging code in the `/chat` endpoint.

---

## Verification Checklist

- [ ] OPIK environment variables are set correctly
- [ ] OPIK Cloud connection is working (check logs)
- [ ] Backend is running with the new logging code
- [ ] Fire a test query in Streamlit
- [ ] Wait 10 seconds
- [ ] Refresh OPIK dashboard
- [ ] See new item in "Rag-system-db" dataset ✅

---

## Quick Reference: Query Flow With Logging

```
┌─────────────────────┐
│  User in Streamlit  │
│  Asks: "What is...?"│
└──────────┬──────────┘
           │ HTTP POST /chat
           ↓
┌─────────────────────────────┐
│   Backend /chat endpoint    │
│   1. Validate engines       │
│   2. Process query (RAG)    │
│   3. Generate answer        │
│   4. ✅ NEW: Log to dataset │  ← ADD THIS
│   5. ✅ NEW: Log to OPIK    │  ← ADD THIS
└──────────┬──────────────────┘
           │
           ├→ Local storage: data/datasets/
           │  (Question + Answer saved)
           │
           └→ OPIK Cloud: parth-d/rag-system-db
              (Appears in dashboard in 10 seconds)
           │
           ↓
┌─────────────────────┐
│    Return Answer    │
│    Show in Streamlit│
└─────────────────────┘
```

---

## Next Steps

**Would you like me to:**

1. ✅ **Implement Option 3 (Hybrid)** → Auto-log to both local dataset and OPIK
2. ✅ **Implement Option 1** → Auto-log only to local dataset
3. ✅ **Implement Option 2** → Auto-log only to OPIK Cloud
4. ✅ **Check your OPIK configuration** → Verify connection and settings
5. ✅ **Debug existing logs** → See why queries aren't being tracked

---

## Related Documentation

- [DATASET_SIMPLE_OVERVIEW.md](DATASET_SIMPLE_OVERVIEW.md) - Basic dataset concepts
- [DATASET_QUERY_FLOW.md](DATASET_QUERY_FLOW.md) - Complete query flow (needs update)
- [OPIK_SETUP_COMPLETE.md](OPIK_SETUP_COMPLETE.md) - OPIK configuration details
- [ENHANCED_OPIK_GUIDE.md](ENHANCED_OPIK_GUIDE.md) - OPIK integration guide

---

**Summary:** Your queries aren't being logged to OPIK because there's no code in the backend to automatically save them. The fix is simple: add 10 lines of code to the `/chat` endpoint to log each query to your dataset/OPIK. 🎯
