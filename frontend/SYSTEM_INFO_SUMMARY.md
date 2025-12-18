# System Information Display - Implementation Summary

## Overview
Added comprehensive system information display above the process flow, showing which model and services are being used.

## Components Added

### 1. System Info Component
**File**: `frontend/components/system_info.py`

Two main functions:
- `render_system_info()` - Displays LLM model, embedding model, and configuration
- `render_api_services()` - Shows available API endpoints and services

### 2. Backend Config Endpoint
**File**: `backend/main.py` (new endpoint)

Added `/config` GET endpoint that returns:
- LLM Model name and provider
- Embedding model
- Chunk size and overlap settings
- Temperature and max tokens
- Top-K value

## Visual Display

### System Information Section
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🤖 LLM Model:     llama-3.3-70b-versatile [GROQ]                   │
│ 🔗 Embedding:     all-MiniLM-L6-v2                                 │
│ ⚙️  Configuration: Chunk: 1000 | Temp: 0.7                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Features**:
- Purple gradient background
- Clean, modern styling
- Shows model and provider separately
- Displays key configuration values

### API Services Section
```
┌─────────────────────────────────────────────────────────────────────┐
│ 📡 API Services:                                                    │
│   📤 Upload    💬 Chat    📚 Documents    ❓ Quiz    🔍 Health      │
└─────────────────────────────────────────────────────────────────────┘
```

**Features**:
- Red-pink gradient background
- Badge-style service indicators
- Shows all available operations

## Display Location

```
┌─────────────────────────────────────────────────────────────────┐
│ 💬 RAG Chatbot              [Process Flow - Top Right]          │
│ Ask questions about your documents...                            │
│                                                                 │
│ ─────────────────────────────────────────────────────────────  │
│ 🤖 LLM Model: llama-3.3-70b-versatile [GROQ]                  │ <- NEW
│ 🔗 Embedding: all-MiniLM-L6-v2                                │ <- NEW
│ ⚙️  Configuration: Chunk: 1000 | Temp: 0.7                    │ <- NEW
│ ─────────────────────────────────────────────────────────────  │ <- NEW
│ 📡 API Services:                                              │ <- NEW
│    📤 Upload  💬 Chat  📚 Documents  ❓ Quiz  🔍 Health        │ <- NEW
│ ─────────────────────────────────────────────────────────────  │ <- NEW
│                                                                 │
│ [Sidebar] [Main Chat Area]                                     │
```

## Information Displayed

### LLM Information
- **Model Name**: From `LLM_MODEL` environment variable
  - Default: `llama-3.3-70b-versatile`
- **Provider**: From `LLM_PROVIDER` environment variable
  - Default: `groq`
  - Can be: `groq` or `gemini`

### Embedding Model
- **Model Name**: From `EMBEDDING_MODEL` environment variable
  - Default: `all-MiniLM-L6-v2`

### Configuration
- **Chunk Size**: From `CHUNK_SIZE` (default: 1000)
- **Chunk Overlap**: From `CHUNK_OVERLAP` (default: 200)
- **Temperature**: From `TEMPERATURE` (default: 0.7)
- **Max Tokens**: From `MAX_TOKENS` (default: 512)
- **Top-K**: From `TOP_K` (default: 8)

### Available API Services
- **📤 Upload** - Document upload endpoint
- **💬 Chat** - Chat/Query endpoint
- **📚 Documents** - Document listing endpoint
- **❓ Quiz** - Question generation endpoint
- **🔍 Health** - Health check endpoint

## Configuration Sources

The system information is fetched in this order:
1. **Primary**: From `/config` API endpoint (fetches from backend `settings`)
2. **Fallback**: From environment variables (.env file)
3. **Final Fallback**: Hardcoded defaults

## Technical Details

### System Info Component
- Fetches configuration via HTTP GET request
- Graceful error handling with fallback to environment variables
- CSS styling for gradient backgrounds and badges
- Responsive flexbox layout

### Backend Endpoint
```python
@app.get("/config")
async def get_config() -> dict:
    """Get system configuration endpoint."""
    return {
        "llm_model": settings.LLM_MODEL,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL,
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "temperature": settings.TEMPERATURE,
        "max_tokens": settings.MAX_TOKENS,
        "top_k": settings.TOP_K
    }
```

## Files Modified

1. **Created**: `frontend/components/system_info.py`
   - System configuration display component
   - API services badge display

2. **Updated**: `frontend/app.py`
   - Added imports for system_info component
   - Added system info rendering after process flow

3. **Updated**: `backend/main.py`
   - Added `/config` endpoint to expose configuration

## User Benefits

✅ **Transparency** - Users know exactly which model and services are running
✅ **Troubleshooting** - Easy to verify configuration
✅ **Information Rich** - Displays key parameters at a glance
✅ **Professional** - Polished UI with gradient styling
✅ **Always Available** - Information updated on every page load
