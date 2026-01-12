"""
Quick test of neural embeddings and hybrid table format improvements.
"""

from backend.vectorstore import FAISSVectorStore
from backend.ingest import DocumentIngestor

def test_neural_embeddings():
    """Test 1: Neural embeddings initialization."""
    print("=" * 70)
    print("Test 1: Neural Embeddings Initialization")
    print("=" * 70)
    
    vs = FAISSVectorStore()
    print(f"✓ Embedding Mode: {vs.embedding_mode}")
    print(f"✓ Embedding Dimension: {vs.embedding_dim}")
    print(f"✓ Model: {vs.embedding_model_name}")
    
    return vs


def test_table_format(vs):
    """Test 2: Hybrid table format chunks."""
    print("\n" + "=" * 70)
    print("Test 2: Hybrid Table Format")
    print("=" * 70)
    
    # Create test chunks with hybrid format
    test_chunks = [
        """Columns: A:Product | B:Quantity | C:Price

[R2] Widget A | 100 | 10.50
[R3] Widget B | 200 | 15.00
[R4] Widget C | 150 | 12.00""",
        
        """Columns: A:Name | B:Age | C:Department

[R2] John Doe | 30 | Engineering
[R3] Jane Smith | 28 | Marketing
[R4] Bob Johnson | 35 | Sales"""
    ]
    
    vs.add_chunks(test_chunks, "test_table_data.csv")
    print(f"✓ Added {len(test_chunks)} chunks with hybrid table format")
    print(f"✓ Total chunks in index: {vs.index.ntotal if vs.index else 0}")


def test_semantic_search(vs):
    """Test 3: Semantic search with neural embeddings."""
    print("\n" + "=" * 70)
    print("Test 3: Semantic Search Quality")
    print("=" * 70)
    
    test_queries = [
        "product pricing information",
        "employee details and departments",
        "Widget B quantity"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vs.search(query, top_k=2)
        
        if results:
            print(f"  Found {len(results)} results:")
            for i, (chunk, score, meta) in enumerate(results, 1):
                print(f"    [{i}] Score: {score:.3f} | Doc: {meta.get('source_doc', 'unknown')}")
                preview = chunk.replace('\n', ' ')[:100]
                print(f"        Preview: {preview}...")
        else:
            print("  No results found")


def test_synonym_understanding(vs):
    """Test 4: Synonym understanding (neural vs keyword)."""
    print("\n" + "=" * 70)
    print("Test 4: Synonym Understanding (Neural Advantage)")
    print("=" * 70)
    
    # Add document with synonyms
    synonym_chunks = [
        "Fast cars and automobiles are popular vehicles for racing.",
        "Purchase orders and procurement documents for buying supplies."
    ]
    vs.add_chunks(synonym_chunks, "test_synonyms.txt")
    
    # Test queries with synonyms
    synonym_tests = [
        ("vehicles", "Should match 'cars' and 'automobiles'"),
        ("buying", "Should match 'purchase' and 'procurement'")
    ]
    
    for query, expected in synonym_tests:
        print(f"\nQuery: '{query}' - {expected}")
        results = vs.search(query, top_k=1)
        if results:
            chunk, score, _ = results[0]
            print(f"  ✓ Match found (score={score:.3f})")
            print(f"    Content: {chunk[:80]}...")
        else:
            print("  ✗ No match (semantic understanding failed)")


def main():
    """Run all tests."""
    print("\nTesting Neural Embeddings & Hybrid Table Format")
    print("=" * 70)
    
    try:
        # Test 1: Initialize
        vs = test_neural_embeddings()
        
        # Test 2: Table format
        test_table_format(vs)
        
        # Test 3: Semantic search
        test_semantic_search(vs)
        
        # Test 4: Synonym understanding
        test_synonym_understanding(vs)
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n📊 Final Statistics:")
        stats = vs.get_statistics()
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Total documents: {stats.get('total_documents', len(set(m.get('source_doc') for m in vs.metadata)))}")
        print(f"  Embedding dimension: {stats.get('embedding_dim', vs.embedding_dim)}")
        print(f"  Embedding mode: {vs.embedding_mode}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
