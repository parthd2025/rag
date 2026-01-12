"""
HOW OPIK WORKS - Practical Demo
================================

This shows the exact flow when a user queries your RAG system.

NOTE: This is a documentation file showing the conceptual flow.
      For actual working code, see test_opik_integration.py
"""

def show_flow():
    """Demonstrate how Opik tracks your RAG queries"""
    
    print("""
================================================================================
                        HOW OPIK WORKS WITH YOUR RAG SYSTEM
================================================================================

SCENARIO: User asks "What are the key features of M2 chipset?"

STEP 1: USER ACTION
-------------------
- User types question in Streamlit UI
- Question: "What are the key features of M2 chipset?"

STEP 2: OPIK STARTS TRACKING ⏱️
-------------------------------
- Creates unique Trace ID: 019b9d46-ee12-729d-862b-e3c53d08c8bd
- Records start time: 2026-01-08 16:33:50
- Captures input: {"query": "What are the key features...", "top_k": 5}

STEP 3: CHAT SERVICE (@track decorator)
---------------------------------------
File: backend/services/chat_service.py

The @track() decorator automatically wraps your function:

    @track(
        name="RAG Query",
        project_name="rag-system", 
        tags=["chat", "retrieval"]
    )
    async def process_query(query, top_k=5, temperature=0.7):
        # Your code runs normally...
        results = rag_engine.retrieve_context(query, top_k=top_k)
        answer = rag_engine.answer_query(query)
        return response

STEP 4: DOCUMENT RETRIEVAL (nested @track)
------------------------------------------
File: backend/rag_engine.py

    @track(
        name="Document Retrieval",
        project_name="rag-system",
        tags=["retrieval", "vectorstore"]
    )
    def retrieve_context(question, top_k=5):
        # Search FAISS index
        results = vector_store.search(question, top_k=top_k)
        return results

Opik Records:
- Duration: 0.3 seconds
- Retrieved: 5 documents
- Top match: m2_chipset.pdf (score: 0.89)
- 2nd match: tech_specs.pdf (score: 0.82)

STEP 5: ANSWER GENERATION (nested @track)
-----------------------------------------
File: backend/rag_engine.py

    @track(
        name="Answer Query",
        project_name="rag-system",
        tags=["generation", "llm"]
    )
    def answer_query(question):
        # Get context and call LLM
        results = vector_store.search(question, top_k=5)
        answer = llm_engine.generate(prompt)
        return answer

Opik Records:
- Duration: 0.8 seconds
- Model: llama-3.3-70b-versatile
- Input tokens: ~800
- Output tokens: ~150
- Cost: $0.0012

STEP 6: DATA SENT TO OPIK SERVER
---------------------------------
- Endpoint: http://localhost:8080/api/v1/traces
- Storage: ClickHouse (metrics), MySQL (metadata), MinIO (payloads)

STEP 7: USER SEES ANSWER
-------------------------
- Total time: 1.1 seconds
- User gets answer in Streamlit
- Meanwhile, trace is saved in Opik!

================================================================================
                        WHAT YOU SEE IN OPIK UI
================================================================================
Open: http://localhost:5173

PROJECT VIEW: rag-system
├─ All queries listed with timestamps
├─ Status indicators (✓ success / ✗ failed)
└─ Duration for each query

TRACE DETAIL (Click on a query):
================================

Trace ID: 019b9d46-ee12-729d-862b-e3c53d08c8bd
Duration: 1.1 seconds
Status: ✓ Success

INPUT:
  query: "What are the key features of M2 chipset?"
  top_k: 5
  temperature: 0.7

EXECUTION TIMELINE:
  │
  ├── 📄 Document Retrieval (0.3s)
  │   ├─ Retrieved: 5 chunks
  │   ├─ Top source: m2_chipset.pdf (score: 0.89)
  │   └─ 2nd source: tech_specs.pdf (score: 0.82)
  │
  └── 🤖 Answer Query (0.8s)
      ├─ Model: llama-3.3-70b-versatile
      ├─ Tokens: 800 input, 150 output
      └─ Cost: $0.0012

OUTPUT:
  answer: "The M2 chipset features 20 billion transistors..."
  sources: ["m2_chipset.pdf", "tech_specs.pdf"]
  confidence: 0.85

TIMELINE VISUALIZATION (Gantt Chart):
=====================================

0.0s  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  1.1s
      │                                                  │
      │  Document Retrieval                             │
      ├──────────────┤                                  │
      │              │  Answer Query                    │
      │              ├───────────────────────┤          │
      │                                                  │
      └──────────────────────────────────────────────────┘
         RAG Query (Total)

================================================================================
                                ANALYTICS
================================================================================

PERFORMANCE METRICS:
  ✓ Average query time: 1.2s
  ✓ P95 latency: 2.1s
  ✓ Retrieval time: 0.3s avg
  ✓ Generation time: 0.8s avg

QUALITY METRICS:
  ✓ Average confidence: 0.82
  ✓ Document relevance scores
  ✓ Success rate: 98%

COST TRACKING:
  ✓ Tokens per query: ~950
  ✓ Cost per query: ~$0.0012
  ✓ Daily API costs
  ✓ Monthly projections

USAGE PATTERNS:
  ✓ Queries per day
  ✓ Peak hours
  ✓ Popular questions
  ✓ User behavior

================================================================================
                            DEBUGGING EXAMPLE
================================================================================

PROBLEM: User says "System gave wrong answer about M2 price"

SOLUTION USING OPIK:

1. Ask user for timestamp
2. Find their trace in Opik UI
3. Click on trace to see details
4. Check which documents were retrieved
   → See: Retrieved wrong_specs.pdf instead of pricing.pdf
5. Check relevance scores
   → See: Low score (0.45) indicates poor match
6. Identify root cause
   → Document metadata needs improvement
7. Fix: Update document metadata with better keywords
8. Test: Run new query and compare traces
9. Verify: New trace shows correct document retrieved

================================================================================
                                SUMMARY
================================================================================

WHAT HAPPENS: 
Every time someone uses your RAG system, Opik automatically records 
everything without any manual logging needed.

WHERE STORED: 
Local Docker containers at http://localhost:5173

WHAT YOU SEE: 
Complete trace with timing, inputs, outputs, and metrics for every step.

HOW TO USE: 
1. Open Opik UI (http://localhost:5173)
2. View traces in rag-system project
3. Click any trace to see details
4. Analyze performance and debug issues

COST: 
Free - runs locally on your machine

SETUP NEEDED: 
✅ Already done! Just use your app normally.

================================================================================

Next: Run your Streamlit app and watch traces appear in real-time!

Command: streamlit run frontend/app.py
Then open: http://localhost:5173

================================================================================
""")

if __name__ == "__main__":
    show_flow()
