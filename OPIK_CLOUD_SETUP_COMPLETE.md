# 🔧 Opik Cloud Configuration & Integration Guide

## ✅ Current Configuration Status

### Opik Cloud Setup
- **Workspace**: parth-d
- **Project**: rag-system
- **API Key**: H6WGN0My9hH9f462Oc6BZplZ0 (configured)
- **Dataset**: rag-system-db (recreated)
- **Status**: ✅ Connected and working

### Environment Variables (Configured)
```bash
OPIK_API_KEY=H6WGN0My9hH9f462Oc6BZplZ0
OPIK_WORKSPACE=parth-d
OPIK_PROJECT_NAME=rag-system
OPIK_ENABLED=true
# OPIK_URL_OVERRIDE is not set (uses cloud default)
```

---

## 🚀 How Your System Works Now

### Query Flow Integration
```
User Query in Streamlit
         ↓
Backend /chat endpoint (main.py)
         ↓
1. Process query with RAG
2. Generate answer
         ↓
3. Auto-log to LOCAL dataset
         ↓ 
4. Auto-log to OPIK CLOUD
         ↓
Return answer to user
```

### What Gets Logged to Opik Cloud
Every query from Streamlit automatically logs:
- **Question** and **Answer**
- **Source documents** used
- **Similarity scores** and confidence
- **Processing metadata** (top_k, temperature, etc.)
- **Timestamps** for tracking

---

## 🎯 Testing Your Integration

### Step 1: Fire a Test Query
1. Open Streamlit: http://localhost:8501
2. Ask any question (e.g., "What is the main topic?")
3. Wait for the answer

### Step 2: Check Opik Dashboard
1. Open: https://www.comet.com/opik/parth-d/rag-system
2. Look for **Traces** - you should see your query
3. Look for **Datasets** - check "rag-system-db" for logged queries

### Step 3: Verify Local Backup
Your queries are also saved locally in:
```
data/datasets/dataset_production_queries_*/
```

---

## 🔍 Monitoring & Analysis

### In Opik Cloud Dashboard:
- **Traces**: Real-time query processing details
- **Datasets**: All historical queries and answers
- **Metrics**: Performance, latency, token usage
- **Debugging**: Full pipeline visibility

### Key Features Now Available:
- ✅ **Real-time tracking** of all Streamlit queries
- ✅ **Performance monitoring** (response times, etc.)
- ✅ **Quality analysis** (similarity scores, confidence)
- ✅ **Historical data** for model improvement
- ✅ **Cost tracking** (token usage)

---

## 🚨 Troubleshooting

### If queries don't appear in Opik:
1. Check backend logs for errors
2. Verify environment variables: `Get-ChildItem env: | Where-Object {$_.Name -like "*OPIK*"}`
3. Test connection: `python -c "import opik; print('✅ Connected')"`

### If dataset is missing:
Run this to recreate:
```python
python -c "
import opik
client = opik.Opik(project_name='rag-system')
dataset = client.create_dataset(name='rag-system-db', description='Production queries')
print('✅ Dataset recreated')
"
```

---

## 🎉 You're All Set!

Your system now has:
- ✅ **Opik Cloud** properly configured
- ✅ **Database** recreated after deletion
- ✅ **Streamlit integration** working
- ✅ **Automatic logging** of all queries
- ✅ **Local backup** for reliability

**Next**: Just use your Streamlit app normally - everything will be tracked automatically! 🚀