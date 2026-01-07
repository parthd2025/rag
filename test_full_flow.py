"""
Test the complete flow: Excel ingestion, hybrid format, neural embeddings, and search.
"""
import sys
sys.path.insert(0, 'D:\\RAG')

from backend.ingest import DocumentIngestor
from backend.vectorstore import FAISSVectorStore

print("=" * 80)
print("FULL SYSTEM TEST: Neural Embeddings + Hybrid Table Format")
print("=" * 80)

# Initialize
print("\n[1] Initializing systems...")
ingestor = DocumentIngestor(chunk_size=800, chunk_overlap=100)
vs = FAISSVectorStore()
print(f"    Embedding mode: {vs.embedding_mode}")
print(f"    Embedding dim: {vs.embedding_dim}")

# Ingest Excel file
print("\n[2] Ingesting Excel file with hybrid format...")
file_path = "backend/data/documents/test_sample.xlsx"
text = ingestor._extract_excel(file_path)
chunks = ingestor._chunk_text(text)
print(f"    Created {len(chunks)} chunks")

# Show sample chunks
print("\n[3] Sample chunks (showing hybrid format):")
for i, chunk in enumerate(chunks[:2], 1):
    print(f"\n    Chunk {i}:")
    preview = chunk[:200].replace('\n', '\n    ')
    print(f"    {preview}...")

# Add to vector store
print("\n[4] Adding chunks to vector store with neural embeddings...")
vs.add_chunks(chunks, "test_sample.xlsx")
print(f"    Total chunks in index: {vs.index.ntotal}")

# Test semantic search
print("\n[5] Testing semantic search queries:")
test_queries = [
    ("products with high quantities", "Should find Widget B with 200 units"),
    ("engineering employees", "Should find John and Alice from Engineering dept"),
    ("row 3 in products sheet", "Should find Widget C data"),
    ("salaries above 70000", "Should find high-salary employees")
]

for query, expected in test_queries:
    print(f"\n    Query: '{query}'")
    print(f"    Expected: {expected}")
    results = vs.search(query, top_k=2)
    
    if results:
        chunk, score, meta = results[0]
        print(f"    Found: score={score:.3f}")
        preview = chunk.replace('\n', ' ')[:100]
        print(f"    Preview: {preview}...")
    else:
        print(f"    No results!")

print("\n" + "=" * 80)
print("TEST COMPLETE!")
print("=" * 80)
print(f"\nFinal Stats:")
print(f"  Chunks indexed: {len(vs.chunks)}")
print(f"  Embedding mode: {vs.embedding_mode}")
print(f"  Embedding dimension: {vs.embedding_dim}")
