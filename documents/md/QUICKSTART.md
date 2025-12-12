# RAG Chatbot - Quick Start Guide (5 Minutes)

## 🎯 Goal
Get the RAG chatbot running in 5 minutes with minimal setup.

## ⏱️ Step-by-Step (Windows PowerShell/Command Prompt)

### 1. Install Dependencies (2 minutes)

```powershell
# Navigate to project root
cd d:\RAG

# Install all required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi uvicorn sentence-transformers faiss-cpu ...
```

### 2. Download a Model (Skip or ~3 minutes)

**Option A: Quick Start WITHOUT Model** ⚡
- The app will start fine without a model
- Responses will show an error message
- Once you add a model, it will work immediately

**Option B: Download a Model Now** 📥
1. Download this file: [Mistral-7B-Instruct Q4](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf) (~4.8GB)
2. Move to: `d:\RAG\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf`

### 3. Start Backend (PowerShell)

```powershell
cd d:\RAG\backend
python main.py
```

**Expected output:**
```
Initializing RAG components...
Loading model from models/mistral-7b-instruct-v0.2.Q4_K_M.gguf...
Model loaded successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ Backend is running! Keep this terminal open.

### 4. Start Frontend (New Terminal/PowerShell)

```powershell
cd d:\RAG\frontend
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.
  
  Local URL: http://localhost:8501
```

✅ Click the URL or open http://localhost:8501

---

## 🚀 Using the Chatbot

### Upload Documents

1. In the left sidebar, click **"Choose files to upload"**
2. Select PDF, DOCX, TXT, or Markdown files
3. Click **"📤 Upload Documents"**
4. Wait for "✅ Uploaded X file(s)"

### Ask Questions

1. Type your question: "What is the main topic?"
2. Click **"Send"**
3. Get your answer with sources

### View Sources

Click **"📚 View Sources"** below each answer to see the document chunks that were used.

---

## ❓ Troubleshooting

### Issue: "Cannot connect to API"
- Check that backend is running (Terminal 1)
- Backend should show: `INFO: Uvicorn running on http://0.0.0.0:8000`
- If not running, go back to Step 3

### Issue: "Error: Model not loaded"
- This is normal if you skipped downloading the model in Step 2
- Download the model (4.8GB) and restart backend
- Alternatively, the app can use HuggingFace models (slower, but requires less setup)

### Issue: Dependencies installation fails
```powershell
# Try upgrading pip first
python -m pip install --upgrade pip

# Then retry
pip install -r requirements.txt
```

### Issue: Port already in use (8000 or 8501)
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Stop that process in Task Manager, or change port:
# Edit backend/main.py, last line: port=8001
# Edit frontend/app.py, search for 8501, change to 8502
```

---

## 📚 Next Steps

Once working, check these guides:

1. **Full Configuration**: See [SETUP.md](SETUP.md) for detailed options
2. **API Reference**: See [API_DOCS.md](API_DOCS.md) to integrate with other apps
3. **Optimize Performance**: See SETUP.md → "Performance Benchmarks"

---

## 🎓 Understanding the Components

```
You (Browser)
    ↓
Streamlit Frontend (http://localhost:8501)
    ↓ (makes API requests)
FastAPI Backend (http://localhost:8000)
    ├→ Document Ingestor (extracts text from PDFs, DOCX, etc.)
    ├→ Vector Store (FAISS - stores document embeddings)
    ├→ Embeddings (Sentence Transformers - converts text to vectors)
    └→ LLM Engine (Mistral-7B - generates answers)
```

**Data Flow:**
```
Upload Document → Extract Text → Create Embeddings → Store in FAISS
Question → Search Similar Embeddings → Retrieve Context → 
Send to LLM → Generate Answer → Return to User
```

---

## 💡 Pro Tips

1. **Batch Upload:** Upload multiple documents at once
2. **Adjust Context:** Use slider in sidebar to change how many document chunks are considered
3. **Temperature Control:** Lower temperature = more focused answers, Higher = more creative
4. **Clear & Restart:** Use "🗑️ Clear All Documents" to reset everything
5. **API Access:** The backend is a full REST API - use `curl` or any language to query it

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| Full Setup Guide | [SETUP.md](SETUP.md) |
| API Documentation | [API_DOCS.md](API_DOCS.md) |
| Model Downloads | [Mistral-7B](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) |
| Sentence Transformers | [Models](https://www.sbert.net/docs/pretrained_models.html) |

---

## ✅ Success Checklist

- [ ] Installed Python 3.10+
- [ ] Ran `pip install -r requirements.txt`
- [ ] Backend running at http://localhost:8000 ✅
- [ ] Frontend running at http://localhost:8501 ✅
- [ ] Uploaded a test document
- [ ] Asked a question and got an answer
- [ ] Viewed sources for the answer

**Everything working? 🎉 You're done!**

---

**Questions?** Check [SETUP.md](SETUP.md) Troubleshooting section.
