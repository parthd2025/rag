import sys
import os
sys.path.append('backend')

from backend.vectorstore import FAISSVectorStore
from backend.rag_engine import RAGEngine
from backend.llm_loader import get_llm_engine

def test_improved_sources():
    """Test the improved source display with document names and detailed references."""
    print("=== Testing Improved Source Display ===\n")
    
    try:
        # Initialize components
        print("🔧 Initializing RAG system...")
        vector_store = FAISSVectorStore()
        llm_engine = get_llm_engine()
        rag_engine = RAGEngine(vector_store, llm_engine, top_k=3)
        print("✅ RAG system initialized\n")
        
        # Test question about AI/ML (should find relevant content)
        question = "What is retrieval augmented generation?"
        print(f"❓ Question: {question}")
        print("-" * 50)
        
        # Get answer with improved sources
        result = rag_engine.answer_query_with_context(question)
        
        print(f"🤖 Answer:")
        print(f"{result.get('answer', 'No answer generated')}")
        print()
        
        # Display improved sources
        sources = result.get('sources', [])
        if sources:
            print("📄 Sources with Enhanced Display:")
            print("="*60)
            for source in sources:
                doc_name = source.get('document_name', 'Unknown Document')
                similarity = source.get('similarity', 0.0)
                preview = source.get('chunk_preview', 'No preview available')
                chunk_length = source.get('chunk_length', 0)
                
                print(f"📄 {doc_name} • {similarity:.1%} match")
                print(f"   Length: {chunk_length:,} characters")
                print(f"   Preview:")
                # Show multi-line preview
                preview_lines = preview.split('\\n')
                for line in preview_lines[:3]:  # Show first 3 lines
                    print(f"   > {line.strip()}")
                if len(preview_lines) > 3:
                    print("   > ...")
                print()
        else:
            print("❌ No sources found")
            
        print("\\n" + "="*70)
        print("Testing with different question...")
        
        # Test with loan policy question (should correctly say not found)
        question2 = "What is the loan policy?"
        print(f"❓ Question: {question2}")
        print("-" * 50)
        
        result2 = rag_engine.answer_query_with_context(question2)
        print(f"🤖 Answer:")
        print(f"{result2.get('answer', 'No answer generated')}")
        print()
        
        sources2 = result2.get('sources', [])
        if sources2:
            print("📄 Sources:")
            for i, source in enumerate(sources2[:2], 1):  # Show only first 2
                doc_name = source.get('document_name', 'Unknown Document')
                similarity = source.get('similarity', 0.0)
                preview = source.get('formatted_preview', 'No preview')
                
                print(f"{i}. {doc_name} • {similarity:.1%} match")
                print(f"   {preview}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_sources()