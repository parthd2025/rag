import sys
import os
sys.path.append('backend')

from backend.vectorstore import FAISSVectorStore
from backend.rag_engine import RAGEngine
from backend.llm_loader import get_llm_engine
from backend.config import settings
import time

def test_optimized_settings():
    """Test the performance with optimized settings."""
    
    print("=" * 70)
    print("🚀 TESTING OPTIMIZED RAG SETTINGS")
    print("=" * 70)
    
    print("⚙️ CURRENT CONFIGURATION:")
    print(f"   📏 Chunk Size: {settings.CHUNK_SIZE:,} characters")
    print(f"   🔄 Chunk Overlap: {settings.CHUNK_OVERLAP} characters")
    print(f"   📊 Chunking Level: {settings.CHUNKING_LEVEL}")
    print(f"   🔍 Top-K: {settings.TOP_K}")
    print(f"   📝 Context Window: {settings.CONTEXT_WINDOW_SIZE:,} characters")
    print()
    
    try:
        # Initialize system
        vector_store = FAISSVectorStore()
        llm_engine = get_llm_engine()
        rag_engine = RAGEngine(vector_store, llm_engine, top_k=settings.TOP_K)
        
        print(f"✅ RAG system initialized with {vector_store.index.ntotal} chunks")
        print()
        
        # Test questions
        test_questions = [
            "What is retrieval augmented generation?",
            "Explain artificial intelligence research topics",
            "What are machine learning concepts mentioned?"
        ]
        
        print("🧪 PERFORMANCE TEST RESULTS:")
        print("=" * 50)
        
        total_time = 0
        for i, question in enumerate(test_questions, 1):
            print(f"📋 Test {i}: {question}")
            
            start_time = time.time()
            result = rag_engine.answer_query_with_context(question)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            sources = result.get('sources', [])
            confidence = result.get('verification', {}).get('confidence_score', 0)
            avg_similarity = sum(s.get('similarity', 0) for s in sources) / len(sources) if sources else 0
            
            print(f"   ⏱️  Time: {response_time:.2f}s")
            print(f"   📊 Sources Retrieved: {len(sources)}")
            print(f"   🎯 Avg Similarity: {avg_similarity:.3f}")
            print(f"   ✅ Confidence: {confidence:.3f}")
            print(f"   📄 Answer Length: {len(result.get('answer', '')):,} chars")
            
            # Show first source for verification
            if sources:
                first_source = sources[0]
                doc_name = first_source.get('document_name', 'Unknown')
                similarity = first_source.get('similarity', 0)
                print(f"   🏆 Top Match: {doc_name} ({similarity:.1%})")
            print()
        
        avg_time = total_time / len(test_questions)
        print("📈 PERFORMANCE SUMMARY:")
        print(f"   ⏱️  Average Response Time: {avg_time:.2f}s")
        print(f"   🔍 Sources per Query: {settings.TOP_K} (optimized)")
        print(f"   📝 Context Window: {settings.CONTEXT_WINDOW_SIZE:,} chars (optimized)")
        print()
        
        print("✅ OPTIMIZATION BENEFITS:")
        print("   🎯 Focused retrieval with Top-K=5 (vs 10)")
        print("   ⚡ Efficient context window (2500 vs 4000 chars)")
        print("   🧠 Simplified chunking level (3 vs 5)")
        print("   📊 Minimal overlap for efficiency (20 vs 200 chars)")
        
        return {
            'avg_response_time': avg_time,
            'chunk_count': vector_store.index.ntotal,
            'settings': {
                'chunk_size': settings.CHUNK_SIZE,
                'overlap': settings.CHUNK_OVERLAP,
                'top_k': settings.TOP_K,
                'context_window': settings.CONTEXT_WINDOW_SIZE,
                'chunking_level': settings.CHUNKING_LEVEL
            }
        }
        
    except Exception as e:
        print(f"❌ Error testing optimized system: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = test_optimized_settings()
    if results:
        print(f"\n🎉 SUCCESS! Optimized RAG system is running with:")
        print(f"   📊 {results['chunk_count']} total chunks")
        print(f"   ⏱️  {results['avg_response_time']:.2f}s average response time")
        print(f"   🎯 Best practice configuration applied!")