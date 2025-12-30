import sys
import os
sys.path.append('backend')

from backend.vectorstore import FAISSVectorStore
from backend.rag_engine import RAGEngine
from backend.llm_loader import get_llm_engine
from backend.config import settings

def test_rag_system():
    """Test the complete RAG system with the loan policy question."""
    print("=== Testing RAG System ===\n")
    
    try:
        # Initialize components
        print("🔧 Initializing RAG components...")
        vector_store = FAISSVectorStore()
        llm_engine = get_llm_engine()
        rag_engine = RAGEngine(vector_store, llm_engine, top_k=5)
        print("✅ RAG system initialized")
        
        # Test the exact question from your original query
        question = "what is loan policy for 1 year experience guy in mindbowser and the leave policies as well"
        print(f"❓ Question: {question}")
        
        # Perform search
        print("\n🔍 Performing retrieval...")
        results = vector_store.search(question, top_k=5)
        
        print(f"📊 Retrieved {len(results)} results:")
        for i, (chunk, similarity, metadata) in enumerate(results, 1):
            print(f"   {i}. Similarity: {similarity:.3f}")
            print(f"      Content: {chunk[:200]}...")
            print(f"      Metadata: {metadata}")
            print()
            
        # Generate answer
        print("🤖 Generating answer...")
        result = rag_engine.answer_query_with_context(question)
        
        print(f"📝 Generated Answer:\n{result.get('answer', 'No answer generated')}\n")
        
        sources = result.get('sources', [])
        if sources:
            print("📄 Sources:")
            for i, source in enumerate(sources, 1):
                print(f"   {i}. {source}")
        else:
            print("❌ No sources provided")
            
        # Test with a question that should match the documents
        print("\n" + "="*50)
        print("Testing with document-relevant question:")
        
        question2 = "What is machine learning and artificial intelligence?"
        print(f"❓ Question: {question2}")
        
        results2 = vector_store.search(question2, top_k=3)
        print(f"📊 Retrieved {len(results2)} results:")
        for i, (chunk, similarity, metadata) in enumerate(results2, 1):
            print(f"   {i}. Similarity: {similarity:.3f}")
            print(f"      Content: {chunk[:200]}...")
            print()
            
        answer2_result = rag_engine.answer_query_with_context(question2)
        print(f"📝 Generated Answer:\n{answer2_result.get('answer', 'No answer generated')}\n")
        
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_system()