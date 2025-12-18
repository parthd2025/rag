# RAG Chatbot - Complete UI Layout Reference

## Full Page Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          💬 RAG Chatbot                                      │
│   Ask questions about your uploaded documents...    [Process Flow Display]   │
│                                                                              │
│   ────────────────────────────────────────────────────────────────────────  │
│   🤖 LLM Model:     llama-3.3-70b-versatile [GROQ]                         │  <- NEW
│   🔗 Embedding:     all-MiniLM-L6-v2                                       │  <- NEW
│   ⚙️  Configuration: Chunk: 1000 | Temp: 0.7                               │  <- NEW
│   ────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│   📡 API Services:                                                          │  <- NEW
│      📤 Upload    💬 Chat    📚 Documents    ❓ Quiz    🔍 Health          │  <- NEW
│                                                                              │
│   ────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│   ✅ Connected to API                                                       │
│                                                                              │
│   ┌───────────────────────────────┬─────────────────────────────────────┐   │
│   │ 📁 UPLOAD DOCUMENTS           │  💭 ASK A QUESTION          [Clear] │   │
│   ├───────────────────────────────┼─────────────────────────────────────┤   │
│   │ [Choose files...             ] │                                     │   │
│   │ [📤 Upload]                   │  [Previous chat messages display]    │   │
│   │                               │                                     │   │
│   │ 📊 Document Count: 5          │                                     │   │
│   │ [🗑️  Clear All Documents]      │  [Chat input area...]               │   │
│   │                               │                                     │   │
│   │ ⚙️  SETTINGS                   │                                     │   │
│   │ Context Chunks: [====5====]   │                                     │   │
│   │                               │                                     │   │
│   │ 💡 SUGGESTED QUESTIONS         │                                     │   │
│   │ Number: [====5====]           │                                     │   │
│   │ [Generate Questions]           │                                     │   │
│   └───────────────────────────────┴─────────────────────────────────────┘   │
│                                                                              │
│  RAG Chatbot - Powered by FAISS, Sentence Transformers, and Groq           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Process Flow Display (Top Right)

```
Upload◯ → Process◯ → Index◯ → Ready◯    (Initial state)

Upload⟳ → Process◯ → Index◯ → Ready◯    (During upload)

Upload✓ → Process✓ → Index✓ → Ready✓    (Success)

Upload✕ → Process✕ → Index◯ → Ready◯    (Error)
```

## System Information Display (NEW)

### Section 1: Model & Configuration
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 LLM Model:     llama-3.3-70b-versatile [GROQ]           │
│ 🔗 Embedding:     all-MiniLM-L6-v2                         │
│ ⚙️  Configuration: Chunk: 1000 | Temp: 0.7                 │
└─────────────────────────────────────────────────────────────┘
```

**Content**:
- **LLM Model**: Large Language Model being used
- **Provider**: API provider (GROQ, Gemini, etc.)
- **Embedding Model**: Model for document embeddings
- **Chunk Size**: Size of text chunks for processing
- **Temperature**: LLM creativity parameter

### Section 2: Available Services
```
┌─────────────────────────────────────────────────────────────┐
│ 📡 API Services:                                            │
│    📤 Upload    💬 Chat    📚 Documents    ❓ Quiz    🔍 Health
└─────────────────────────────────────────────────────────────┘
```

**Services**:
- 📤 **Upload**: Document upload endpoint
- 💬 **Chat**: Query/chat endpoint
- 📚 **Documents**: Document management
- ❓ **Quiz**: Question generation
- 🔍 **Health**: API health status

## Information Sources

### From Backend API (`/config` endpoint)
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

### From Environment Variables (.env)
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

## Color Scheme

### System Info Section (Purple)
```
Background: Linear gradient from #667eea to #764ba2
Text: White
Labels: Semi-transparent white (0.8)
Values: Solid white with semi-transparent background
```

### API Services Section (Red-Pink)
```
Background: Linear gradient from #f093fb to #f5576c
Text: White
Badges: Semi-transparent white background
```

### Process Flow Section
```
Pending: Grey (#e0e0e0)
Processing: Yellow (#fff3cd) with animation
Success: Green (#d4edda)
Error: Red (#f8d7da)
```

## User Experience Flow

1. **Page Load**
   - System fetches configuration from `/config` endpoint
   - Information displays immediately below title
   - Process flow shows all steps as pending

2. **User Uploads Files**
   - Upload button clicked → Upload status changes to "processing"
   - Backend processes files
   - Progress: Upload ✓ → Process ✓ → Index ✓ → Ready ✓

3. **User Asks Questions**
   - Chat interface ready
   - System info always visible for reference
   - Configuration parameters shown for transparency

4. **Error Handling**
   - If API unreachable: Falls back to environment variables
   - If config endpoint fails: Shows default values
   - Process flow turns red if operations fail

## Benefits

✨ **Transparency**: Users see exact configuration
📊 **Information**: Complete system overview at a glance
🔧 **Debugging**: Easy to verify correct setup
🎨 **Professional**: Modern, polished appearance
♿ **Accessibility**: Clear labels and indicators
📱 **Responsive**: Works on different screen sizes
