# Complete RAG Project Guide for Beginners

## 🤔 What is RAG?

**RAG** stands for **Retrieval-Augmented Generation**. Think of it as giving an AI assistant a "memory" of your documents so it can answer questions about them.

### Simple Analogy:
Imagine you have a huge library of books, and someone asks you a question. Instead of reading every book from scratch, you:
1. **Search** for the most relevant pages (Retrieval)
2. **Read** those specific pages (Context)
3. **Answer** the question based on what you found (Generation)

That's exactly what RAG does!

---

## 📊 High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM OVERVIEW                          │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: LOADING A PDF (One-time setup)
═══════════════════════════════════════════════════════════════════

PDF File
   │
   ▼
[Extract Text] ──→ Full Text Document
   │
   ▼
[Split into Chunks] ──→ [Chunk 1, Chunk 2, Chunk 3, ...]
   │                        (1000 chars each, 200 overlap)
   ▼
[Generate Embeddings] ──→ [Vector 1, Vector 2, Vector 3, ...]
   │                        (384 numbers representing meaning)
   ▼
[Store in Database] ──→ ChromaDB (Persistent Storage)
                         ✓ Saved to disk
                         ✓ Available for future queries


PHASE 2: ASKING A QUESTION (Query time)
═══════════════════════════════════════════════════════════════════

Your Question
   │
   ▼
[Generate Question Embedding] ──→ Question Vector
   │
   ▼
[Search Similar Chunks] ──→ Find Top 3 Most Similar Chunks
   │                          (using cosine similarity)
   ▼
[Retrieve Context] ──→ Relevant Text Chunks
   │
   ▼
[Build Prompt] ──→ Context + Question
   │
   ▼
[Send to AI (Gemini)] ──→ Generate Answer
   │
   ▼
Final Answer
```

---

## 🏗️ Project Structure Explained

### File-by-File Breakdown

```
RAG Project/
│
├── main.py              ← Entry point (CLI interface)
├── rag_system.py        ← Main brain (orchestrates everything)
├── pdf_processor.py     ← Handles PDF reading and chunking
├── vector_store.py      ← Manages vector database (ChromaDB)
├── requirements.txt     ← Python packages needed
├── .env                 ← Your API key (create this!)
└── chroma_db/           ← Database storage (auto-created)
```

---

## 📝 Detailed Component Explanation

### 1. `main.py` - The Command Line Interface

**What it does:** This is how you interact with the system.

**Key Functions:**
- `load <pdf_path>` - Load a PDF file
- `query <question>` - Ask a question
- `list` - See all loaded documents
- `clear` - Delete all stored data

**How it works:**
```python
# When you run: python main.py load document.pdf
# It creates a RAGSystem object and calls rag.load_pdf("document.pdf")
```

---

### 2. `rag_system.py` - The Main Orchestrator

**What it does:** This is the "brain" that coordinates everything.

**Key Components:**

#### A. Initialization (`__init__`)
```python
# Loads two models:
1. Sentence Transformer (for embeddings) - FREE, runs on your computer
2. Google Gemini API (for answering) - FREE tier available
```

#### B. Loading PDFs (`load_pdf`)
```
Step 1: Extract text from PDF
Step 2: Split into chunks (1000 chars, 200 overlap)
Step 3: Convert chunks to vectors (embeddings)
Step 4: Store in ChromaDB
```

#### C. Querying (`query`)
```
Step 1: Convert question to vector
Step 2: Find similar chunks in database
Step 3: Build prompt with context
Step 4: Send to Gemini AI
Step 5: Return answer
```

---

### 3. `pdf_processor.py` - PDF Handler

**What it does:** Reads PDFs and splits text into manageable pieces.

#### `extract_text_from_pdf()`
- Opens PDF file
- Reads each page
- Extracts all text
- Returns as one big string

#### `chunk_text()`
- Takes long text
- Splits into smaller pieces (1000 characters)
- Adds overlap (200 chars) so context isn't lost
- Returns list of chunks

**Why chunking?**
- AI models have token limits
- Smaller pieces are easier to search
- Overlap preserves context at boundaries

**Example:**
```
Original: "This is a very long document with lots of information..."
Chunk 1: "This is a very long document with lots of information about..."
Chunk 2: "...information about machine learning and artificial intelligence..."
         ↑ Overlap (200 chars)
```

---

### 4. `vector_store.py` - The Database

**What it does:** Stores and searches text chunks using vectors.

**Key Concepts:**

#### What are Embeddings/Vectors?
- Text converted to numbers (e.g., 384 numbers)
- Similar text = similar numbers
- Allows mathematical comparison

**Example:**
```
"Machine learning" → [0.23, -0.45, 0.67, ..., 0.12] (384 numbers)
"AI algorithms"   → [0.25, -0.43, 0.65, ..., 0.11] (similar numbers!)
"Cooking recipes" → [0.89, 0.12, -0.34, ..., -0.56] (very different!)
```

#### ChromaDB Features:
- **Persistent:** Saves to disk (survives restarts)
- **Fast Search:** Finds similar vectors quickly
- **Automatic:** Handles storage, indexing, retrieval

**Key Methods:**
- `add_document()` - Store chunks and embeddings
- `search()` - Find similar chunks
- `clear()` - Delete everything
- `get_document_list()` - List all documents

---

## 🔄 Complete Data Flow

### Scenario: Loading a PDF

```
1. User runs: python main.py load research.pdf

2. main.py creates RAGSystem object
   └─> Loads embedding model (Sentence Transformer)
   └─> Connects to Gemini API
   └─> Initializes VectorStore (ChromaDB)

3. RAGSystem.load_pdf("research.pdf")
   └─> pdf_processor.extract_text_from_pdf()
       └─> Reads PDF page by page
       └─> Returns: "Full text content..."
   
   └─> pdf_processor.chunk_text()
       └─> Splits into chunks
       └─> Returns: ["Chunk 1...", "Chunk 2...", ...]
   
   └─> embedder.encode(chunks)
       └─> Converts each chunk to vector
       └─> Returns: [[0.23, -0.45, ...], [0.34, 0.12, ...], ...]
   
   └─> vector_store.add_document()
       └─> Saves to ChromaDB
       └─> Data persists to chroma_db/ folder

4. Success! PDF is now searchable
```

### Scenario: Asking a Question

```
1. User runs: python main.py query "What is machine learning?"

2. RAGSystem.query("What is machine learning?")
   └─> embedder.encode(question)
       └─> Converts question to vector
       └─> Returns: [0.25, -0.43, 0.65, ...]
   
   └─> vector_store.search(query_vector, top_k=3)
       └─> ChromaDB finds 3 most similar chunks
       └─> Returns: [
            ("Machine learning is...", 0.89, "research.pdf"),
            ("ML algorithms...", 0.85, "research.pdf"),
            ("AI and ML...", 0.82, "research.pdf")
           ]
   
   └─> Build prompt:
       """
       Context from documents:
       [From research.pdf]
       Machine learning is...
       
       [From research.pdf]
       ML algorithms...
       
       Question: What is machine learning?
       """
   
   └─> model.generate_content(prompt)
       └─> Sends to Google Gemini API
       └─> Returns: "Machine learning is a subset of artificial intelligence..."
   
3. Answer displayed to user
```

---

## 🧠 Key Concepts Explained

### 1. Embeddings (Vector Representations)

**What:** Converting text to numbers that capture meaning.

**Why:** Computers can't understand words, but they're great at math!

**How it works:**
- Model trained on millions of texts
- Learns that similar words have similar numbers
- "Dog" and "Puppy" → similar vectors
- "Dog" and "Pizza" → very different vectors

**In this project:**
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- FREE, runs on your computer
- No API calls needed

---

### 2. Similarity Search

**What:** Finding text chunks that are "similar" to your question.

**How:**
- Convert question to vector
- Compare with all stored chunk vectors
- Use **cosine similarity** (measures angle between vectors)
- Return top-k most similar

**Cosine Similarity:**
```
Similar vectors (pointing same direction) = High similarity (close to 1.0)
Different vectors (pointing different ways) = Low similarity (close to 0.0)
```

---

### 3. RAG Pipeline

**Traditional AI:**
```
Question → AI → Answer (may hallucinate, no source)
```

**RAG:**
```
Question → Search Documents → Find Relevant Context → AI + Context → Answer (grounded in documents)
```

**Benefits:**
- ✅ Answers based on YOUR documents
- ✅ Can cite sources
- ✅ Less hallucination
- ✅ Up-to-date information

---

## 🛠️ Technologies Used

### 1. Sentence Transformers
- **What:** Library for creating embeddings
- **Model:** `all-MiniLM-L6-v2`
- **Cost:** FREE (runs locally)
- **Size:** ~80MB (downloads once)

### 2. ChromaDB
- **What:** Vector database
- **Purpose:** Store and search embeddings
- **Features:** Persistent, fast, easy to use
- **Storage:** `chroma_db/` folder

### 3. Google Gemini API
- **What:** Large Language Model (LLM)
- **Model:** `gemini-2.0-flash`
- **Cost:** FREE tier available
- **Purpose:** Generate answers from context

### 4. PyPDF2
- **What:** PDF reading library
- **Purpose:** Extract text from PDF files

---

## 📈 Step-by-Step: Your First RAG Query

### Step 1: Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
GEMINI_API_KEY=your_key_here
```

### Step 2: Load a PDF
```bash
python main.py load my_document.pdf
```

**What happens behind the scenes:**
1. PDF text extracted
2. Split into ~50 chunks (depends on PDF size)
3. Each chunk converted to 384-number vector
4. All vectors saved to ChromaDB
5. Data persists to `chroma_db/` folder

### Step 3: Ask a Question
```bash
python main.py query "What is the main topic?"
```

**What happens behind the scenes:**
1. Question converted to vector
2. System searches for 3 most similar chunks
3. Context + question sent to Gemini
4. Gemini generates answer
5. Answer returned to you

---

## 🎯 Understanding the Code Flow

### When you run `python main.py load document.pdf`:

```python
# main.py
def main():
    rag = RAGSystem()  # ← Initializes models
    
    rag.load_pdf("document.pdf")  # ← Processes PDF
```

```python
# rag_system.py
def load_pdf(self, pdf_path):
    # Step 1: Extract text
    text = extract_text_from_pdf(pdf_path)  # ← pdf_processor.py
    
    # Step 2: Chunk text
    chunks = chunk_text(text)  # ← pdf_processor.py
    
    # Step 3: Create embeddings
    embeddings = self.embedder.encode(chunks)  # ← Sentence Transformer
    
    # Step 4: Store
    self.vector_store.add_document(chunks, embeddings)  # ← vector_store.py
```

### When you run `python main.py query "question"`:

```python
# rag_system.py
def query(self, question):
    # Step 1: Convert question to vector
    query_embedding = self.embedder.encode(question)
    
    # Step 2: Search for similar chunks
    results = self.vector_store.search(query_embedding)  # ← vector_store.py
    
    # Step 3: Build prompt with context
    context = "\n\n".join([chunk for chunk, score, doc in results])
    prompt = f"Context: {context}\nQuestion: {question}"
    
    # Step 4: Get answer from AI
    answer = self.model.generate_content(prompt)  # ← Google Gemini
    
    return answer.text
```

---

## 🔍 Deep Dive: How Similarity Search Works

### Example:

**Stored Chunks:**
```
Chunk 1: "Machine learning is a subset of AI"
Chunk 2: "Python is a programming language"
Chunk 3: "Deep learning uses neural networks"
```

**Your Question:**
```
"What is machine learning?"
```

**Process:**

1. **Convert to vectors:**
   ```
   Question: [0.25, -0.43, 0.65, ..., 0.12]
   Chunk 1:  [0.23, -0.45, 0.67, ..., 0.11]  ← Very similar!
   Chunk 2:  [0.89, 0.12, -0.34, ..., -0.56] ← Different
   Chunk 3:  [0.28, -0.41, 0.63, ..., 0.15]  ← Similar
   ```

2. **Calculate similarity:**
   ```
   Question vs Chunk 1: 0.92 (92% similar) ← Top match!
   Question vs Chunk 3: 0.78 (78% similar)
   Question vs Chunk 2: 0.15 (15% similar)
   ```

3. **Retrieve top 3:**
   ```
   Returns: [Chunk 1, Chunk 3, Chunk 2]
   ```

4. **Send to AI:**
   ```
   Context: "Machine learning is a subset of AI..."
   Question: "What is machine learning?"
   ```

5. **AI generates answer based on context**

---

## 💡 Common Questions

### Q: Why not just search for keywords?
**A:** Vector search understands **meaning**, not just words. 
- Keyword: "car" won't find "automobile"
- Vector: "car" and "automobile" have similar vectors!

### Q: Why chunk text instead of using whole document?
**A:** 
- AI models have token limits
- Smaller chunks = more precise retrieval
- Can find specific sections, not just entire documents

### Q: What if the answer isn't in the PDF?
**A:** The AI will say "The context doesn't contain enough information" instead of making things up.

### Q: How does it remember between sessions?
**A:** ChromaDB saves to `chroma_db/` folder. Data persists automatically!

### Q: Is this really free?
**A:** 
- Embeddings: ✅ FREE (runs on your computer)
- ChromaDB: ✅ FREE (local database)
- Gemini API: ✅ FREE tier available (check Google's limits)

---

## 🚀 Next Steps to Learn

1. **Try different PDFs** - Load various documents and ask questions
2. **Experiment with top_k** - Try `--top-k 1` vs `--top-k 10`
3. **Read the code** - Each file is well-commented
4. **Modify chunk sizes** - See how it affects results
5. **Add more documents** - Load multiple PDFs and query across them

---

## 📚 Key Python Concepts Used

### Classes and Objects
```python
rag = RAGSystem()  # Create an object
rag.load_pdf()     # Call a method
```

### Lists and Tuples
```python
chunks = ["chunk1", "chunk2"]  # List
result = (text, score, doc)    # Tuple
```

### Functions
```python
def extract_text_from_pdf(pdf_path):
    # Do something
    return text
```

### Libraries/Modules
```python
import PyPDF2  # External library
from pdf_processor import extract_text_from_pdf  # Your own module
```

---

## 🎓 Summary

**RAG = Retrieval + Augmentation + Generation**

1. **Retrieval:** Find relevant text chunks
2. **Augmentation:** Add context to your question
3. **Generation:** AI generates answer from context

**Your project does this by:**
- Converting text to numbers (embeddings)
- Storing in a searchable database (ChromaDB)
- Finding similar content (cosine similarity)
- Asking AI to answer with context (Gemini)

**The result:** An AI that can answer questions about YOUR documents!

---

*Happy learning! 🎉*

