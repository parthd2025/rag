"""
Test Opik integration with actual RAG system
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vectorstore import FAISSVectorStore
from backend.llm_loader import GroqLLMEngine
from backend.rag_engine import RAGEngine
from backend.services.chat_service import ChatService
from backend.config import settings


async def test_opik_integration():
    """Test Opik tracking with real RAG queries"""
    
    print("=" * 70)
    print("🔍 Testing Opik Integration with RAG System")
    print("=" * 70)
    
    # Initialize components
    print("\n1️⃣  Initializing RAG components...")
    try:
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        
        llm_engine = GroqLLMEngine(
            model_name=settings.LLM_MODEL
        )
        
        rag_engine = RAGEngine(
            vector_store=vector_store,
            llm_engine=llm_engine,
            top_k=5
        )
        
        chat_service = ChatService(rag_engine)
        
        print("✅ RAG components initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        return
    
    # Test queries
    test_questions = [
        "What is the main topic of the documents?",
        "Can you summarize the key points?",
        "What are the important details mentioned?"
    ]
    
    print(f"\n2️⃣  Running {len(test_questions)} test queries with Opik tracking...")
    print("-" * 70)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Query {i}: {question}")
        
        try:
            result = await chat_service.process_query(
                query=question,
                top_k=3,
                temperature=0.7
            )
            
            print(f"✅ Answer generated")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            print(f"   - Confidence: {result['confidence']:.2f}")
            print(f"   - Sources: {len(result['sources'])} documents")
            print(f"   - Answer preview: {result['answer'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Testing Complete!")
    print("=" * 70)
    print("\n🎯 Next Steps:")
    print("   1. Open Opik UI: http://localhost:5173")
    print("   2. Navigate to 'rag-system' project")
    print("   3. View the traces from your queries")
    print("   4. Analyze performance metrics")
    print("\n💡 Traces include:")
    print("   - Complete execution flow")
    print("   - Document retrieval timing")
    print("   - LLM generation metrics")
    print("   - Input/output at each step")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_opik_integration())
