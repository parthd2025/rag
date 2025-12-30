"""
Verify that all 396 chunks are properly embedded in the vector store
"""
import sys
import os
import json
import numpy as np
sys.path.append('backend')

from backend.config import settings
from backend.vectorstore import FAISSVectorStore

def verify_embedding_coverage():
    """Check if all chunks are properly embedded"""
    
    print("🔍 === Verifying Embedding Coverage ===")
    
    try:
        # Initialize vector store
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        
        # Check metadata file
        print("\n1. Checking metadata file...")
        if os.path.exists(settings.METADATA_PATH):
            with open(settings.METADATA_PATH, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"   📊 Metadata entries: {len(metadata)}")
            
            # Show document breakdown
            doc_counts = {}
            for meta in metadata:
                doc_name = meta.get('document', 'Unknown')
                doc_counts[doc_name] = doc_counts.get(doc_name, 0) + 1
            
            print("   📋 Document breakdown:")
            for doc, count in doc_counts.items():
                print(f"      - {doc}: {count} chunks")
        else:
            print("   ❌ No metadata file found!")
            return
        
        # Check FAISS index
        print("\n2. Checking FAISS index...")
        if os.path.exists(settings.INDEX_PATH):
            # Try to load the index
            try:
                vector_store._load_index()
                if hasattr(vector_store, 'index') and vector_store.index is not None:
                    index_size = vector_store.index.ntotal
                    print(f"   📊 FAISS index entries: {index_size}")
                    
                    # Check if counts match
                    if index_size == len(metadata):
                        print("   ✅ Metadata and index counts match!")
                    else:
                        print(f"   ⚠️  Mismatch! Metadata: {len(metadata)}, Index: {index_size}")
                        
                    # Get embedding dimension
                    if index_size > 0:
                        embedding_dim = vector_store.index.d
                        print(f"   📊 Embedding dimension: {embedding_dim}")
                else:
                    print("   ❌ Could not load FAISS index!")
            except Exception as e:
                print(f"   ❌ Error loading index: {e}")
        else:
            print("   ❌ No FAISS index file found!")
            return
        
        # Test search functionality
        print("\n3. Testing search functionality...")
        try:
            test_queries = [
                "mindbowser",
                "M2 mileage", 
                "employee benefits"
            ]
            
            for query in test_queries:
                results = vector_store.search(query, top_k=5)
                print(f"   🔍 Query '{query}': {len(results)} results")
                
                if results:
                    # Show top result details
                    chunk, score, metadata_item = results[0]
                    doc_name = metadata_item.get('document', 'Unknown')
                    print(f"      - Top result: {doc_name} (score: {score:.3f})")
                    print(f"      - Preview: {chunk[:100]}...")
                else:
                    print(f"      - ❌ No results for '{query}'")
                    
        except Exception as e:
            print(f"   ❌ Search test failed: {e}")
        
        # Check for missing or corrupted embeddings
        print("\n4. Checking embedding integrity...")
        try:
            # Sample a few embeddings to check for corruption
            sample_indices = [0, len(metadata)//2, len(metadata)-1] if len(metadata) > 2 else [0]
            
            for idx in sample_indices:
                if idx < len(metadata):
                    # Try to get embedding vector
                    if hasattr(vector_store, 'index') and vector_store.index:
                        try:
                            # Reconstruct vector (if supported)
                            vector = vector_store.index.reconstruct(idx)
                            if vector is not None and len(vector) > 0:
                                print(f"   ✅ Embedding {idx}: Valid ({len(vector)} dimensions)")
                                # Check if vector has reasonable values
                                if np.any(np.isnan(vector)) or np.any(np.isinf(vector)):
                                    print(f"      ⚠️  Warning: NaN or Inf values detected")
                            else:
                                print(f"   ❌ Embedding {idx}: Empty or invalid")
                        except Exception as e:
                            print(f"   ⚠️  Could not reconstruct embedding {idx}: {e}")
                            
        except Exception as e:
            print(f"   ⚠️  Embedding integrity check failed: {e}")
        
        # Summary
        print(f"\n📊 === Summary ===")
        print(f"Expected chunks: 396 (from UI)")
        print(f"Metadata entries: {len(metadata)}")
        print(f"FAISS index entries: {index_size if 'index_size' in locals() else 'Unknown'}")
        
        if 'index_size' in locals() and index_size == 396 and len(metadata) == 396:
            print("✅ All 396 chunks appear to be properly embedded!")
        else:
            print("⚠️  There may be missing or misaligned embeddings")
            print("\n🔧 Recommended actions:")
            print("1. Run re-ingestion script to rebuild index")
            print("2. Check for corrupted files")
            print("3. Verify embedding model compatibility")
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_embedding_coverage()