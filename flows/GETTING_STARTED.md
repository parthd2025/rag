# Getting Started - Your First RAG Project

Welcome! This guide will help you understand and use your RAG project step by step.

## 🎯 What You'll Learn

By the end of this guide, you'll understand:
- What RAG is
- How your project works
- How to use it
- What each file does

---

## 📖 Step 1: Understand What RAG Is

**RAG = Retrieval-Augmented Generation**

Think of it like this:
1. You have documents (PDFs)
2. You want to ask questions about them
3. RAG finds the relevant parts
4. AI answers using those parts

**Simple Example:**
```
You: "What is machine learning?"
RAG: 
  1. Searches your PDFs for "machine learning" content
  2. Finds relevant paragraphs
  3. Sends them + your question to AI
  4. AI answers based on YOUR documents
```

---

## 🏗️ Step 2: Understand Your Project Structure

Your project has 4 main Python files:

```
main.py           ← You run this (command line interface)
rag_system.py     ← The "brain" that coordinates everything
pdf_processor.py  ← Reads PDFs and splits them
vector_store.py   ← Stores and searches text chunks
```

**How they work together:**
```
main.py → calls → rag_system.py → uses → pdf_processor.py
                                      → vector_store.py
```

---

## 🚀 Step 3: Set Up (One Time)

### 3.1 Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `sentence-transformers` - For creating embeddings (FREE, local)
- `chromadb` - For storing vectors
- `google-generativeai` - For AI answers (FREE tier)
- `PyPDF2` - For reading PDFs

### 3.2 Get API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Get a free API key
3. Create `.env` file in project folder:
   ```
   GEMINI_API_KEY=your_key_here
   ```

---

## 📝 Step 4: Use Your RAG System

### Load a PDF
```bash
python main.py load my_document.pdf
```

**What happens:**
1. PDF text is extracted
2. Text is split into chunks (1000 chars each)
3. Each chunk becomes a vector (384 numbers)
4. Vectors are saved to database
5. ✅ PDF is now searchable!

### Ask a Question
```bash
python main.py query "What is the main topic?"
```

**What happens:**
1. Your question becomes a vector
2. System finds 3 most similar chunks
3. Context + question sent to AI
4. AI generates answer
5. ✅ Answer displayed!

### Other Commands
```bash
# See all loaded documents
python main.py list

# Clear everything
python main.py clear
```

---

## 🧠 Step 5: Understand the Flow

### When Loading a PDF:

```
PDF File
  ↓
Extract Text (pdf_processor.py)
  ↓
Split into Chunks (pdf_processor.py)
  ↓
Create Embeddings (rag_system.py)
  ↓
Store in Database (vector_store.py)
  ↓
✅ Ready to query!
```

### When Asking a Question:

```
Your Question
  ↓
Create Question Embedding (rag_system.py)
  ↓
Search for Similar Chunks (vector_store.py)
  ↓
Get Top 3 Chunks
  ↓
Build Prompt with Context (rag_system.py)
  ↓
Send to Gemini AI (rag_system.py)
  ↓
✅ Get Answer!
```

---

## 📚 Step 6: Learn More

Now that you understand the basics:

1. **Read the code** - Each file has comments explaining what it does
2. **Try different PDFs** - Load various documents
3. **Experiment** - Try different questions
4. **Read detailed guides:**
   - `PROJECT_GUIDE.md` - Complete explanation
   - `FLOW_DIAGRAMS.md` - Visual diagrams
   - `QUICK_REFERENCE.md` - Command reference

---

## 🎓 Key Concepts (Simplified)

### Embeddings
- Text → Numbers (384 numbers)
- Similar text = Similar numbers
- Allows "smart" search (not just keywords)

### Chunking
- Long text → Small pieces
- Each piece = 1000 characters
- Overlap = 200 characters (keeps context)

### Vector Database (ChromaDB)
- Stores all your chunks as vectors
- Can find similar vectors quickly
- Saves to disk (persists between sessions)

### Similarity Search
- Compares question vector with chunk vectors
- Finds most similar chunks
- Returns top 3 (or more with `--top-k`)

---

## 💡 Tips for Success

1. **Start simple** - Load one PDF, ask simple questions
2. **Read error messages** - They usually tell you what's wrong
3. **Check your API key** - Make sure `.env` file exists
4. **Be patient** - First run downloads model (~80MB)
5. **Experiment** - Try different questions and PDFs

---

## ❓ Common First-Time Issues

**"GEMINI_API_KEY not found"**
- Create `.env` file with your API key

**"No text extracted from PDF"**
- PDF might be scanned (image-based)
- Try a text-based PDF

**Slow first run**
- Normal! Model downloads first time (~80MB)
- Subsequent runs are faster

**"No documents loaded"**
- Load a PDF first with `python main.py load file.pdf`

---

## 🎉 You're Ready!

You now understand:
- ✅ What RAG is
- ✅ How to set up the project
- ✅ How to use it
- ✅ Basic concepts

**Next Steps:**
1. Load a PDF
2. Ask some questions
3. Read `PROJECT_GUIDE.md` for deeper understanding
4. Explore the code!

Happy learning! 🚀

