# Glossary - Technical Terms Explained

Simple explanations of technical terms used in this RAG project.

---

## A

### API (Application Programming Interface)
- **What:** A way for programs to talk to each other
- **In this project:** Used to communicate with Google Gemini AI
- **Example:** Your code asks Gemini a question, Gemini sends back an answer

### API Key
- **What:** A password that lets you use an API
- **In this project:** Your Gemini API key in `.env` file
- **Why needed:** Google needs to know it's you using their service

---

## C

### Chunk
- **What:** A small piece of text from a larger document
- **In this project:** ~1000 characters of text
- **Why:** Easier to search and process than entire documents
- **Example:** A 10-page PDF becomes ~50 chunks

### Chunking
- **What:** The process of splitting text into smaller pieces
- **In this project:** Done by `pdf_processor.py`
- **Settings:** 1000 chars per chunk, 200 char overlap

### ChromaDB
- **What:** A database designed for storing vectors
- **In this project:** Stores all your PDF chunks and their embeddings
- **Features:** Fast search, persistent storage
- **Location:** `chroma_db/` folder

### CLI (Command Line Interface)
- **What:** A way to interact with a program using text commands
- **In this project:** `main.py` provides the CLI
- **Example:** `python main.py load document.pdf`

### Cosine Similarity
- **What:** A way to measure how similar two vectors are
- **Range:** 0.0 (different) to 1.0 (identical)
- **In this project:** Used to find chunks similar to your question
- **Example:** 0.92 = 92% similar (very similar!)

---

## E

### Embedding
- **What:** Text converted to a list of numbers (vector)
- **In this project:** 384 numbers per chunk
- **Why:** Computers can compare numbers, not words
- **Example:** "Machine learning" → [0.23, -0.45, 0.67, ..., 0.12]

### Embedding Model
- **What:** A program that converts text to embeddings
- **In this project:** `all-MiniLM-L6-v2` (Sentence Transformers)
- **Features:** FREE, runs on your computer
- **Size:** ~80MB (downloads once)

---

## G

### Gemini
- **What:** Google's AI language model
- **In this project:** Generates answers to your questions
- **Model:** `gemini-2.0-flash` (free tier)
- **Purpose:** Takes context + question, returns answer

---

## L

### LLM (Large Language Model)
- **What:** An AI that understands and generates text
- **In this project:** Google Gemini
- **Examples:** ChatGPT, Gemini, Claude
- **Purpose:** Generates human-like text

---

## P

### PDF (Portable Document Format)
- **What:** A file format for documents
- **In this project:** Your input files
- **Processing:** Text is extracted page by page

### Prompt
- **What:** Instructions and context given to an AI
- **In this project:** Context chunks + your question
- **Example:** "Context: [chunks]... Question: What is ML?"

### PyPDF2
- **What:** A Python library for reading PDFs
- **In this project:** Extracts text from PDF files
- **Function:** `extract_text_from_pdf()`

---

## R

### RAG (Retrieval-Augmented Generation)
- **What:** A technique that combines document search with AI
- **Process:** Retrieve relevant docs → Augment question → Generate answer
- **Benefit:** AI answers based on YOUR documents, not general knowledge

### Retrieval
- **What:** Finding relevant information
- **In this project:** Finding chunks similar to your question
- **Method:** Vector similarity search

---

## S

### Sentence Transformers
- **What:** A library for creating text embeddings
- **In this project:** Converts text to vectors
- **Model:** `all-MiniLM-L6-v2`
- **Cost:** FREE (runs locally)

### Similarity Search
- **What:** Finding items similar to a query
- **In this project:** Finding chunks similar to your question
- **Method:** Compare vectors using cosine similarity

---

## V

### Vector
- **What:** A list of numbers representing something
- **In this project:** Text converted to 384 numbers
- **Example:** [0.23, -0.45, 0.67, ..., 0.12]

### Vector Database
- **What:** A database optimized for storing and searching vectors
- **In this project:** ChromaDB
- **Purpose:** Fast similarity search across many vectors

### Vector Store
- **What:** The component that manages vector storage
- **In this project:** `vector_store.py` class
- **Functions:** Add documents, search, clear

---

## Common Phrases

### "Top-K"
- **What:** The number of best results to return
- **In this project:** Default is 3 (top 3 most similar chunks)
- **Usage:** `--top-k 5` to get top 5 results

### "Persistent Storage"
- **What:** Data that survives program restarts
- **In this project:** ChromaDB saves to disk
- **Benefit:** Don't need to reload PDFs every time

### "Local Model"
- **What:** A model that runs on your computer
- **In this project:** Sentence Transformers (embeddings)
- **Benefit:** No API calls, works offline

### "API Call"
- **What:** Sending a request to an external service
- **In this project:** Sending prompt to Gemini API
- **Cost:** Uses your API quota (free tier available)

---

## Quick Reference

| Term | Simple Meaning | In This Project |
|------|---------------|-----------------|
| **Chunk** | Small text piece | ~1000 characters |
| **Embedding** | Text as numbers | 384 numbers |
| **Vector** | List of numbers | Same as embedding |
| **Similarity** | How alike two things are | 0.0 to 1.0 |
| **RAG** | Search + AI | Find docs, then answer |
| **CLI** | Text commands | `python main.py ...` |
| **API** | Service interface | Google Gemini |
| **Database** | Data storage | ChromaDB |

---

*This glossary helps you understand the technical terms used throughout the project!*

