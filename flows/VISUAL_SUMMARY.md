# Visual Summary - RAG Project at a Glance

## 🎯 What This Project Does

```
┌─────────────┐
│   You       │
│  (User)     │
└──────┬──────┘
       │
       │ "Load PDF" / "Ask Question"
       │
       ▼
┌─────────────────────────────────────┐
│      RAG SYSTEM                     │
│                                     │
│  📄 PDFs → 🔍 Search → 🤖 AI → 💬 Answer
└─────────────────────────────────────┘
```

---

## 📁 Project Files

```
RAG Project/
│
├── 📘 main.py              ← You run this
├── 🧠 rag_system.py        ← Main brain
├── 📄 pdf_processor.py     ← Reads PDFs
├── 💾 vector_store.py      ← Database
│
├── 📚 Documentation:
│   ├── GETTING_STARTED.md  ← Start here!
│   ├── PROJECT_GUIDE.md    ← Complete guide
│   ├── FLOW_DIAGRAMS.md    ← Visual flows
│   ├── QUICK_REFERENCE.md  ← Commands
│   ├── GLOSSARY.md         ← Terms
│   └── README.md           ← Overview
│
└── 💾 chroma_db/           ← Auto-created (database)
```

---

## 🔄 The Two Main Flows

### Flow 1: Loading a PDF

```
PDF File
   │
   ├─→ Extract Text
   ├─→ Split into Chunks
   ├─→ Convert to Vectors
   └─→ Store in Database
        │
        └─→ ✅ Ready to Query!
```

### Flow 2: Asking a Question

```
Your Question
   │
   ├─→ Convert to Vector
   ├─→ Find Similar Chunks
   ├─→ Build Context
   ├─→ Send to AI
   └─→ ✅ Get Answer!
```

---

## 🧩 Components

```
┌──────────────┐
│  main.py     │  ← Command Interface
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ rag_system.py│  ← Orchestrator
└───┬──────┬───┘
    │      │
    ▼      ▼
┌──────┐ ┌──────────┐
│ PDF  │ │ Vector   │
│ Proc │ │ Store    │
└──────┘ └──────────┘
```

---

## 🛠️ Technologies

```
┌─────────────────────┐
│ Sentence Transformers│  ← Embeddings (FREE, local)
│   all-MiniLM-L6-v2  │
└─────────────────────┘

┌─────────────────────┐
│     ChromaDB        │  ← Vector Database (FREE)
│   (Persistent)      │
└─────────────────────┘

┌─────────────────────┐
│  Google Gemini API  │  ← AI Answers (FREE tier)
│  gemini-2.0-flash   │
└─────────────────────┘

┌─────────────────────┐
│      PyPDF2         │  ← PDF Reader
└─────────────────────┘
```

---

## 📊 Data Flow

```
Text → Chunks → Vectors → Database → Search → Context → AI → Answer
```

**Detailed:**
```
PDF Text
  ↓ (chunking)
["Chunk 1", "Chunk 2", ...]
  ↓ (embedding)
[[0.23, ...], [0.25, ...], ...]
  ↓ (storage)
ChromaDB
  ↓ (query time)
Question → Vector → Search → Top Chunks
  ↓ (generation)
Context + Question → Gemini → Answer
```

---

## 🎓 Key Concepts

### Embeddings
```
Text: "Machine learning"
  ↓
Vector: [0.23, -0.45, 0.67, ..., 0.12]
         ↑ 384 numbers representing meaning
```

### Similarity
```
Question: "What is ML?"
  ↓
Compare with all chunks
  ↓
Find most similar (0.92 = 92% match)
  ↓
Retrieve top 3 chunks
```

### RAG Process
```
1. Retrieve → Find relevant chunks
2. Augment → Add context to question
3. Generate → AI creates answer
```

---

## 🚀 Quick Start

```
1. Setup
   pip install -r requirements.txt
   Create .env with GEMINI_API_KEY

2. Load PDF
   python main.py load document.pdf

3. Ask Question
   python main.py query "Your question?"

4. Done! ✅
```

---

## 📚 Learning Path

```
Start Here:
  ↓
GETTING_STARTED.md
  ↓
PROJECT_GUIDE.md
  ↓
FLOW_DIAGRAMS.md
  ↓
Read the Code!
  ↓
Experiment & Learn
```

---

## 💡 Remember

- **Embeddings** = Text as numbers
- **Chunks** = Small text pieces
- **Similarity** = How alike two things are
- **RAG** = Search + AI
- **ChromaDB** = Stores everything
- **Gemini** = Generates answers

---

*This is your RAG project in a nutshell! 🎉*

