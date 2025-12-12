# Quick Reference Guide

## 🚀 Common Commands

```bash
# Load a PDF
python main.py load path/to/document.pdf

# Ask a question
python main.py query "Your question here"

# Ask with more context (top 5 chunks)
python main.py query "Your question" --top-k 5

# List all loaded documents
python main.py list

# Clear all documents
python main.py clear
```

---

## 📚 File Overview

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | CLI interface | Entry point, command parsing |
| `rag_system.py` | Main orchestrator | `load_pdf()`, `query()`, `list_documents()` |
| `pdf_processor.py` | PDF handling | `extract_text_from_pdf()`, `chunk_text()` |
| `vector_store.py` | Database | `add_document()`, `search()`, `clear()` |

---

## 🔑 Key Concepts

### Embeddings
- **What:** Text converted to numbers (384 numbers per chunk)
- **Model:** `all-MiniLM-L6-v2` (FREE, local)
- **Purpose:** Enable similarity search

### Chunking
- **Size:** 1000 characters per chunk
- **Overlap:** 200 characters between chunks
- **Why:** Break large documents into searchable pieces

### Similarity Search
- **Method:** Cosine similarity
- **Returns:** Top-k most similar chunks
- **Default:** top_k=3

### Vector Database
- **Tool:** ChromaDB
- **Storage:** `chroma_db/` folder
- **Persistence:** Data saved automatically

---

## 🔄 Typical Workflow

```
1. Load PDF
   python main.py load document.pdf

2. Ask Questions
   python main.py query "What is the main topic?"
   python main.py query "Summarize key points"

3. Check Documents
   python main.py list

4. Clear (optional)
   python main.py clear
```

---

## 🛠️ Setup Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Get Gemini API key: https://makersuite.google.com/app/apikey
- [ ] Create `.env` file with: `GEMINI_API_KEY=your_key_here`
- [ ] Test with: `python main.py load test.pdf`

---

## 📖 Learn More

- **Complete Guide:** See `PROJECT_GUIDE.md`
- **Flow Diagrams:** See `FLOW_DIAGRAMS.md`
- **Original README:** See `README.md`

---

## ❓ Troubleshooting

**Error: GEMINI_API_KEY not found**
→ Create `.env` file with your API key

**Error: No text extracted from PDF**
→ PDF might be scanned/image-based (needs OCR)

**Slow first run**
→ Embedding model downloads (~80MB) - only happens once

**No relevant results**
→ Try increasing `--top-k` value (e.g., `--top-k 10`)

---

## 💡 Tips

- Load multiple PDFs to search across documents
- Use descriptive questions for better results
- Higher `--top-k` = more context but slower
- Data persists between sessions automatically
- Clear database when starting fresh

