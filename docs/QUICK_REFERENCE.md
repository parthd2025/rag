# 🎯 Enhanced Opik Integration - Quick Reference Card

## ⚡ TL;DR - What Changed

Your Opik traces went from this:
```
RAG Query → Simple input/output
```

To this:
```
rag_query_complete
├─ query_preprocessing (enrichment)
├─ document_retrieval (vector search)
├─ document_reranking (filtering)
├─ context_building (assembly)
└─ llm_generation (tokens + cost)
```

**5 nested spans with detailed metrics at each step!**

---

## 🚀 Quick Start (60 seconds)

```bash
# 1. Restart server
uvicorn backend.main:app --reload --port 8000

# 2. Make a query (any method works)

# 3. Check Opik
# → https://www.comet.com/opik
# → Project: "rag-system"
# → Click any trace to see 5 nested spans
```

---

## 📊 What Each Span Tracks

| Span | Duration | What It Shows |
|------|----------|---------------|
| **query_preprocessing** | ~0.001s | Query enhancement, term expansion |
| **document_retrieval** | ~0.1s | Chunks found, similarity scores, doc names |
| **document_reranking** | ~0.003s | Filtering results, confidence boost |
| **context_building** | ~0.001s | Context assembly, truncation |
| **llm_generation** | ~1.2s | Tokens (in/out), cost, answer |

---

## 💰 Metrics You Get

### Performance
- Time breakdown per component
- Total processing time
- Tokens per second

### Quality  
- Confidence scores (0-1)
- Similarity scores (0-1)
- Documents matched

### Resources
- Tokens: Input, Output, Total
- Estimated cost per query
- Context utilization

---

## 📁 Files Created

```
backend/services/
  └─ chat_service_enhanced.py  ⭐ Main implementation

Documentation/
  ├─ ENHANCED_OPIK_README.md          Quick start
  ├─ IMPLEMENTATION_COMPLETE.md       Full summary
  ├─ ENHANCED_OPIK_GUIDE.md           Detailed guide
  └─ BEFORE_AFTER_COMPARISON.md       Examples

Scripts/
  ├─ test_enhanced_opik.py            Test script
  ├─ quick_start_opik.py              Setup helper
  └─ final_verification.py            Verify install
```

---

## ✅ Verify It's Working

### In Server Logs
```
INFO: Enhanced chat service initialized
INFO: ENHANCED_CHAT: Processing query with trace: xyz...
```

### In Opik Dashboard
- Project name: "rag-system"
- Trace name: "rag_query_complete"
- 5 nested spans visible
- JSON input/output everywhere
- Tokens, costs, metrics shown

---

## 🐛 Quick Troubleshooting

**Issue:** Still shows "RAG Query"
```bash
# Restart the server completely
# Make a NEW query (not cached)
```

**Issue:** No nested spans
```bash
# Click on the trace to expand it
# Look for "rag_query_complete" traces
```

**Issue:** Opik not configured
```bash
opik configure
# Or set: OPIK_API_KEY, OPIK_WORKSPACE
```

---

## 🎓 Understanding Traces

```
Trace = Complete request
  ├─ Span = Individual step
  │   ├─ Input = Parameters
  │   ├─ Output = Results + Metrics
  │   └─ Tags = For filtering
  └─ Metadata = Additional context
```

---

## 📖 Key Documentation

| Read This If... | File |
|----------------|------|
| Quick overview | `ENHANCED_OPIK_README.md` |
| Complete details | `IMPLEMENTATION_COMPLETE.md` |
| How to customize | `ENHANCED_OPIK_GUIDE.md` |
| See examples | `BEFORE_AFTER_COMPARISON.md` |

---

## 🎯 Common Use Cases

### Debug Failed Query
1. Go to Opik dashboard
2. Filter by status = "failed"
3. Click trace to see which span failed
4. View input that caused error
5. Fix and redeploy

### Optimize Performance
1. Sort traces by duration
2. Click slowest trace
3. See which span takes most time
4. Optimize that component
5. Compare before/after

### Monitor Costs
1. Filter traces by date range
2. Group by user_id (optional)
3. Sum estimated_cost_usd
4. Track daily/monthly trends
5. Set alerts if needed

### Track Quality
1. Filter by confidence score
2. Find low confidence queries
3. Check similarity scores
4. Review retrieved documents
5. Improve retrieval strategy

---

## 💡 Pro Tips

1. **Monitor dashboard daily** to catch issues early
2. **Set up alerts** for errors or slow queries
3. **Track costs** to stay within budget
4. **Compare A/B tests** using tags
5. **Add user_id** to track per-user metrics

---

## 🔧 Customization

### Add Custom Metadata
```python
# In chat_service_enhanced.py
metadata={
    "environment": "production",
    "version": "2.0",
    "custom_field": "value"
}
```

### Add Custom Tags
```python
tags=["rag", "production", "v2", "experiment_a"]
```

### Track User Context
```python
result = await enhanced_service.process_query_enhanced(
    query="...",
    user_id="user_123"  # Shows in trace metadata
)
```

---

## 📈 Success Metrics

Your implementation is successful if:

✅ Traces named "rag_query_complete" appear
✅ 5 nested spans per trace
✅ Rich JSON at each level  
✅ Token counts visible
✅ Cost estimates shown
✅ Performance metrics tracked
✅ Document names displayed
✅ Similarity scores shown

---

## 🎉 Bottom Line

**Before:** Black box processing, hard to debug

**After:** Complete visibility, easy debugging, actionable insights

**Just like the professional LLM apps you wanted!** 🚀

---

## 📞 Quick Commands

```bash
# Start server
uvicorn backend.main:app --reload --port 8000

# Test integration
python test_enhanced_opik.py

# Verify setup
python final_verification.py

# View summary
python quick_start_opik.py

# Check Opik
# https://www.comet.com/opik
```

---

**That's everything you need to know!** 🎯

Read the full docs for deep dives, but this quick reference covers 90% of what you'll need.
