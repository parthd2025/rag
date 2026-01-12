# Opik Integration - Next Steps

## ✅ What's Been Done:

### 1. Opik Server Setup
- ✅ Docker containers running (8 services)
- ✅ UI accessible at http://localhost:5173
- ✅ API running on http://localhost:8080
- ✅ Python SDK installed and configured

### 2. Code Integration
- ✅ Added Opik tracking to `backend/services/chat_service.py`
  - `process_query()` method tracked
- ✅ Added Opik tracking to `backend/rag_engine.py`
  - `retrieve_context()` method tracked
  - `answer_query()` method tracked
- ✅ Graceful fallback if Opik not available

### 3. Package Installation
- ✅ `opik` installed
- ✅ `langchain` and `langchain-community` installed

## 🚀 What's Next:

### 1. Test the Integration
```powershell
# Run the test script
cd D:\RAG
python test_opik_integration.py
```

This will:
- Initialize your RAG system
- Run 3 test queries
- Each query will be traced in Opik
- Show performance metrics

### 2. View Traces in Opik UI
1. Open http://localhost:5173 in your browser
2. Look for the "rag-system" project
3. Click on traces to see:
   - Complete execution timeline
   - Input/output at each step
   - Duration of each operation
   - Retrieval and generation metrics

### 3. Use in Production

Your existing Streamlit app will now automatically track queries! Just run:
```powershell
streamlit run frontend/app.py
```

Every query will be traced with:
- 📊 User question
- 🔍 Document retrieval (which docs, scores)
- 🤖 LLM generation (model, tokens, time)
- ✅ Final answer and sources

### 4. Monitor Performance

In Opik UI, you can:
- **Compare queries** - See which perform better
- **Identify bottlenecks** - Find slow operations
- **Track costs** - Monitor LLM token usage
- **Debug issues** - Full trace with inputs/outputs
- **A/B test** - Compare different models or parameters

### 5. Advanced: Add More Tracking

You can add tracking to other functions:

```python
from opik import track

@track(
    name="Custom Operation",
    project_name="rag-system",
    tags=["custom"]
)
def your_function(param):
    # your code
    return result
```

## 📋 Commands Reference

```powershell
# Start Opik
cd D:\RAG\opik
.\opik.ps1

# Stop Opik
cd D:\RAG\opik
.\opik.ps1 --stop

# Check status
docker ps --filter "name=opik"

# Test integration
cd D:\RAG
python test_opik_integration.py

# Run your app (with tracing)
streamlit run frontend/app.py
```

## 🎯 Current Status

- ✅ Opik server: **RUNNING**
- ✅ SDK: **INSTALLED**
- ✅ Code: **INTEGRATED**
- ⏭️  Next: **TEST IT!**

## 📖 Documentation

- Integration examples: `opik_integration_example.py`
- Flow diagram: `docs/opik_workflow.html`
- Setup guide: `docs/OPIK_SETUP.md`
- Quick commands: `opik_commands.txt`
