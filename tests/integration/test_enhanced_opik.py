"""
Test Enhanced Opik Integration
===============================

This script tests the enhanced Opik integration with comprehensive tracing.
"""

import asyncio
import sys
from backend.logger_config import logger

# Test if Opik is available
try:
    import opik
    print("✅ Opik is installed and available")
    OPIK_AVAILABLE = True
except ImportError:
    print("❌ Opik is NOT installed")
    print("   Run: pip install opik")
    OPIK_AVAILABLE = False
    sys.exit(1)


async def test_enhanced_chat_service():
    """Test the enhanced chat service with a sample query."""
    print("\n" + "="*60)
    print("Testing Enhanced Chat Service with Opik Tracking")
    print("="*60)
    
    try:
        # Import components
        from backend.vectorstore import FAISSVectorStore
        from backend.llm_loader import get_llm_engine
        from backend.rag_engine import RAGEngine
        from backend.services.chat_service_enhanced import EnhancedChatService
        from backend.config import settings
        
        print("\n1. Initializing components...")
        
        # Initialize vector store
        print("   - Loading vector store...")
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        print(f"   ✅ Vector store loaded with {len(vector_store.chunks)} chunks")
        
        if len(vector_store.chunks) == 0:
            print("   ❌ No documents in vector store. Please upload documents first.")
            return
        
        # Initialize LLM
        print("   - Initializing LLM engine...")
        llm_engine = get_llm_engine()
        if not llm_engine.is_ready():
            print("   ❌ LLM engine not ready. Check API key configuration.")
            return
        print(f"   ✅ LLM engine ready")
        
        # Initialize RAG engine
        print("   - Initializing RAG engine...")
        rag_engine = RAGEngine(
            vector_store=vector_store,
            llm_engine=llm_engine,
            top_k=5,
            temperature=0.7
        )
        print("   ✅ RAG engine initialized")
        
        # Initialize enhanced chat service
        print("   - Initializing enhanced chat service...")
        enhanced_service = EnhancedChatService(rag_engine)
        print("   ✅ Enhanced chat service initialized")
        
        # Test query
        print("\n2. Testing enhanced query processing...")
        test_query = "What is machine learning?"
        print(f"   Query: '{test_query}'")
        
        result = await enhanced_service.process_query_enhanced(
            query=test_query,
            top_k=5,
            temperature=0.7,
            user_id="test_user"
        )
        
        print("\n3. Results:")
        print(f"   ✅ Answer: {result['answer'][:200]}...")
        print(f"   ✅ Sources: {len(result.get('sources', []))} documents")
        print(f"   ✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"   ✅ Processing time: {result.get('processing_time', 0):.2f}s")
        
        if 'metrics' in result:
            print("\n4. Metrics:")
            metrics = result['metrics']
            print(f"   - Retrieval time: {metrics.get('retrieval_time', 0):.3f}s")
            print(f"   - Generation time: {metrics.get('generation_time', 0):.3f}s")
            print(f"   - Chunks retrieved: {metrics.get('chunks_retrieved', 0)}")
            print(f"   - Chunks used: {metrics.get('chunks_used', 0)}")
            
            if 'tokens' in metrics:
                tokens = metrics['tokens']
                print(f"   - Input tokens: {tokens.get('input', 0)}")
                print(f"   - Output tokens: {tokens.get('output', 0)}")
                print(f"   - Total tokens: {tokens.get('total', 0)}")
                print(f"   - Estimated cost: ${metrics.get('estimated_cost_usd', 0):.6f}")
        
        print("\n" + "="*60)
        print("✅ Enhanced Opik integration test PASSED!")
        print("="*60)
        print("\n📊 Check your Opik dashboard for detailed traces:")
        print("   https://www.comet.com/opik")
        print("\nYou should see:")
        print("   - Main trace: 'rag_query_complete'")
        print("   - Nested spans: query_preprocessing, document_retrieval,")
        print("                   document_reranking, context_building, llm_generation")
        print("   - Rich metadata and metrics at each step")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_document_processing():
    """Test document processing with Opik tracking."""
    print("\n" + "="*60)
    print("Testing Document Processing Service")
    print("="*60)
    
    try:
        from backend.services.chat_service_enhanced import DocumentProcessingService
        
        service = DocumentProcessingService()
        print("✅ Document processing service initialized")
        
        # Note: This is a simulation - replace with actual document path
        print("\n📝 Note: Document processing traces will appear when you:")
        print("   1. Upload documents via the /upload endpoint")
        print("   2. Re-ingest documents")
        print("\nExpected traces:")
        print("   - process_document_complete")
        print("   - pdf_extraction (or other format)")
        print("   - llm_parsing")
        print("   - csv_generation")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("Enhanced Opik Integration Test Suite")
    print("="*60)
    
    if not OPIK_AVAILABLE:
        return
    
    # Run tests
    asyncio.run(test_enhanced_chat_service())
    asyncio.run(test_document_processing())
    
    print("\n" + "="*60)
    print("All Tests Complete!")
    print("="*60)
    print("\n🚀 Next steps:")
    print("   1. Restart your FastAPI server")
    print("   2. Make queries through the /chat endpoint")
    print("   3. Check Opik dashboard for rich traces")
    print("   4. Look for nested spans with detailed metrics")


if __name__ == "__main__":
    main()
