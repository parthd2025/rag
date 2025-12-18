# Frontend Components Documentation

## 📦 Components Overview

This folder contains reusable Streamlit components for the RAG Chatbot application.

---

## 🧩 Available Components

### 1. Process Flow Component
**File**: `process_flow.py`

A visual horizontal indicator showing the status of sequential operations.

**Functions**:
- `render_process_flow(processes)` - Renders the flow diagram
- `initialize_process_flow(processes)` - Sets up initial state
- `update_process_status(name, status)` - Updates process status
- `get_process_flow()` - Retrieves current flow state

**Status Values**:
- `pending` - Not started (grey circle ◯)
- `processing` - In progress (yellow spinning ⟳)
- `success` - Completed (green checkmark ✓)
- `error` - Failed (red X ✕)

**Usage**:
```python
from components.process_flow import (
    render_process_flow,
    initialize_process_flow,
    update_process_status,
    get_process_flow
)

# Initialize
initialize_process_flow(["Upload", "Process", "Index", "Ready"])

# Display
render_process_flow(get_process_flow())

# Update
update_process_status("Upload", "processing")
```

**Documentation**: See [PROCESS_FLOW_SUMMARY.md](../PROCESS_FLOW_SUMMARY.md)

---

### 2. System Information Component
**File**: `system_info.py`

Displays system configuration and available API services.

**Functions**:
- `get_system_config()` - Fetches configuration from API or env vars
- `render_system_info()` - Displays model, provider, and configuration
- `render_api_services()` - Displays available services

**Information Displayed**:
- LLM Model name and provider
- Embedding model
- Configuration parameters (chunk size, temperature, etc.)
- Available API services

**Usage**:
```python
from components.system_info import (
    render_system_info,
    render_api_services
)

# Display configuration
render_system_info()

# Display services
render_api_services()
```

**Configuration Sources**:
1. Primary: `/config` API endpoint (2-second timeout)
2. Fallback: Environment variables (.env)
3. Final: Hardcoded defaults

**Documentation**: See [SYSTEM_INFO_SUMMARY.md](../SYSTEM_INFO_SUMMARY.md)

---

### 3. Chat UI Component
**File**: `chat_ui.py`

(Original chat interface component)

---

## 🎨 Styling Reference

### Process Flow
- Pending: Grey (#e0e0e0)
- Processing: Yellow (#fff3cd) with animation
- Success: Green (#d4edda)
- Error: Red (#f8d7da)

### System Information
- Background: Purple gradient (#667eea → #764ba2)
- Text: White
- Rounded corners: 8px

### API Services
- Background: Red-pink gradient (#f093fb → #f5576c)
- Badges: Semi-transparent white backgrounds
- Rounded corners: 12px for badges

---

## 🔄 Data Flow

```
app.py (Main Application)
    ↓
components/ (This folder)
    ├─ process_flow.py      (Status indicator)
    ├─ system_info.py       (Configuration display)
    └─ chat_ui.py           (Chat interface)
    ↓
backend/ (API Endpoints)
    ├─ /health             (Health check)
    ├─ /config             (System configuration) ← NEW
    ├─ /upload             (Document upload)
    ├─ /chat               (Chat queries)
    ├─ /quiz               (Question generation)
    └─ /documents          (Document listing)
```

---

## 📋 Configuration Reference

### Environment Variables (used by system_info component)
```
LLM_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TEMPERATURE=0.7
MAX_TOKENS=512
TOP_K=8
```

### API Endpoint (/config)
```json
{
  "llm_model": "llama-3.3-70b-versatile",
  "llm_provider": "groq",
  "embedding_model": "all-MiniLM-L6-v2",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "temperature": 0.7,
  "max_tokens": 512,
  "top_k": 8
}
```

---

## 🚀 Usage Examples

### Process Flow Example
```python
from components.process_flow import *

# Initialize at app start
initialize_process_flow(["Upload", "Process", "Index", "Ready"])

# In your main layout
with st.columns([0.6, 0.4])[1]:
    render_process_flow(get_process_flow())

# Update during operations
update_process_status("Upload", "processing")
try:
    # ... do upload ...
    update_process_status("Upload", "success")
    update_process_status("Process", "processing")
except Exception as e:
    update_process_status("Upload", "error")
```

### System Info Example
```python
from components.system_info import render_system_info, render_api_services

# Display configuration and services
st.markdown("---")
render_system_info()
render_api_services()
st.markdown("---")
```

---

## 🔧 Customization

### Process Flow
Customize process names:
```python
initialize_process_flow(["Validate", "Convert", "Store", "Cache"])
```

Customize colors in `process_flow.py` CSS section.

### System Information
Customize colors in `system_info.py` CSS sections:
- `.system-info-container` - Main panel
- `.api-services-container` - Services panel

---

## 🐛 Troubleshooting

### Process Flow Not Displaying
1. Check that `initialize_process_flow()` was called
2. Check browser console for errors (F12)
3. Verify Streamlit version compatibility

### System Info Not Showing
1. Ensure backend is running
2. Check `/config` endpoint: `curl http://localhost:8001/config`
3. Verify environment variables are set
4. Check browser console for network errors

### Styling Not Applied
1. Clear browser cache (Ctrl+Shift+Del)
2. Restart Streamlit app
3. Check that HTML unsafe rendering is enabled (it is by default)

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [PROCESS_FLOW_SUMMARY.md](../PROCESS_FLOW_SUMMARY.md) | Process flow component docs |
| [SYSTEM_INFO_SUMMARY.md](../SYSTEM_INFO_SUMMARY.md) | System info component docs |
| [DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) | Master documentation index |
| [VISUAL_LAYOUT_DIAGRAM.md](../VISUAL_LAYOUT_DIAGRAM.md) | Visual layout guide |
| [UI_LAYOUT_REFERENCE.md](../UI_LAYOUT_REFERENCE.md) | UI reference guide |
| [FEATURE_COMPLETE.md](../FEATURE_COMPLETE.md) | Feature completion summary |

---

## ✅ Quality Checklist

- [x] Components are reusable
- [x] Error handling included
- [x] Graceful fallbacks
- [x] Documentation complete
- [x] Styling polished
- [x] Production ready

---

## 🔗 Related Files

- **Main App**: `../app.py`
- **Process Flow Docs**: `../PROCESS_FLOW_SUMMARY.md`
- **System Info Docs**: `../SYSTEM_INFO_SUMMARY.md`
- **Backend Config**: `../../backend/config.py`
- **Backend Main**: `../../backend/main.py`

---

## 📞 Support

For issues or questions:
1. Check the relevant documentation file
2. Review component code comments
3. Check browser console for errors
4. Verify backend is running and responsive

---

*Last Updated: December 18, 2025*
*Status: Production Ready ✅*
