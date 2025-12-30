"""
Specific check for M2 document embedding coverage
"""
import sys
import os
import json
sys.path.append('backend')

from backend.config import settings
from backend.vectorstore import FAISSVectorStore

def check_m2_embedding_coverage():
    """Specifically check M2 document chunks in embeddings"""
    
    print("🎯 === M2 Document Embedding Coverage Check ===")
    
    try:
        # Load metadata
        with open(settings.METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Find M2-related chunks
        m2_chunks = []
        total_chunks = len(metadata)
        
        print(f"📊 Total chunks in metadata: {total_chunks}")
        
        # Analyze all chunks for M2 content
        for i, meta in enumerate(metadata):
            doc_name = meta.get('document', '')
            
            # Check if this is M2-related
            is_m2_doc = False
            if any(term in doc_name.lower() for term in ['m2', 'mileage', 'miles']):
                is_m2_doc = True
            
            # Also check chunk content if available
            chunk_text = meta.get('text', '')
            has_m2_content = any(term in chunk_text.lower() for term in ['m2', 'mileage'])
            
            if is_m2_doc or has_m2_content:
                m2_chunks.append({
                    'index': i,
                    'document': doc_name,
                    'is_m2_doc': is_m2_doc,
                    'has_m2_content': has_m2_content,
                    'preview': chunk_text[:100] if chunk_text else 'No text preview'
                })
        
        print(f"🎯 M2-related chunks found: {len(m2_chunks)}")
        
        if m2_chunks:
            print("\\n📋 M2 Chunk Details:")
            for chunk_info in m2_chunks[:10]:  # Show first 10
                print(f"   Chunk {chunk_info['index']}:")
                print(f"      Document: {chunk_info['document']}")
                print(f"      M2 Doc: {chunk_info['is_m2_doc']}")
                print(f"      M2 Content: {chunk_info['has_m2_content']}")
                print(f"      Preview: {chunk_info['preview']}...")
                print()
        
        # Test search specifically for M2 content
        print("🔍 Testing M2-specific searches...")
        
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        
        m2_test_queries = [
            "M2",
            "m2", 
            "mileage",
            "MindBowser Mileages",
            "M2 benefits",
            "travel allowance M2"
        ]
        
        for query in m2_test_queries:
            print(f"\\n   Query: '{query}'")
            try:
                results = vector_store.search(query, top_k=10)
                
                if results:
                    print(f"      Found {len(results)} results")
                    
                    # Count M2-specific results
                    m2_results = 0
                    for chunk, score, meta in results:
                        doc_name = meta.get('document', '')
                        if any(term in doc_name.lower() for term in ['m2', 'mileage']) or \
                           any(term in chunk.lower() for term in ['m2', 'mileage']):
                            m2_results += 1
                    
                    print(f"      M2-specific results: {m2_results}/{len(results)}")
                    
                    # Show top M2 result if found
                    for chunk, score, meta in results[:3]:
                        doc_name = meta.get('document', '')
                        if any(term in doc_name.lower() for term in ['m2', 'mileage']):
                            print(f"      ✅ M2 Result: {doc_name} (score: {score:.3f})")
                            print(f"         Preview: {chunk[:100]}...")
                            break
                    else:
                        print(f"      ❌ No M2 documents in top 3 results")
                        print("      Top results from:")
                        for chunk, score, meta in results[:3]:
                            doc_name = meta.get('document', '')
                            print(f"         - {doc_name} (score: {score:.3f})")
                else:
                    print(f"      ❌ No results found")
                    
            except Exception as e:
                print(f"      ❌ Search error: {e}")
        
        # Summary
        print(f"\\n📊 === M2 Coverage Summary ===")
        print(f"Total chunks: {total_chunks}")
        print(f"M2-related chunks: {len(m2_chunks)}")
        print(f"Coverage: {len(m2_chunks)/total_chunks*100:.1f}%")
        
        if len(m2_chunks) == 0:
            print("⚠️  WARNING: No M2 chunks found in embeddings!")
            print("   This explains why M2 queries aren't working")
            print("   Action needed: Re-ingest the M2 document")
        elif len(m2_chunks) < 5:
            print("⚠️  WARNING: Very few M2 chunks found")
            print("   M2 document may not be properly chunked")
        else:
            print("✅ M2 chunks found in embeddings")
            print("   Issue may be with search/retrieval logic")
            
    except Exception as e:
        print(f"❌ Error checking M2 coverage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_m2_embedding_coverage()