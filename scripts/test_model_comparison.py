"""
Test Model Comparison Feature
==============================

This script tests the model comparison functionality by comparing
responses from multiple LLM models and evaluating them.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.config import settings
from backend.vectorstore import FAISSVectorStore
from backend.llm_loader import get_llm_engine
from backend.rag_engine import RAGEngine
from backend.services.evaluation_service import ModelComparisonService, LLMEvaluator


async def test_model_comparison():
    """Test the model comparison feature."""
    print("=" * 60)
    print("🔬 Model Comparison Test")
    print("=" * 60)
    
    # Step 1: Initialize components
    print("\n1️⃣  Initializing RAG components...")
    
    try:
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        print(f"   ✅ Vector store loaded with {len(vector_store.chunks)} chunks")
    except Exception as e:
        print(f"   ❌ Vector store error: {e}")
        return
    
    if not vector_store.chunks:
        print("   ⚠️  No documents loaded. Please upload documents first.")
        return
    
    llm_engine = get_llm_engine()
    if not llm_engine.is_ready():
        print("   ❌ LLM engine not ready - check GROQ_API_KEY")
        return
    print(f"   ✅ LLM engine ready (model: {llm_engine.model_name})")
    
    rag_engine = RAGEngine(
        vector_store=vector_store,
        llm_engine=llm_engine,
        top_k=5
    )
    print("   ✅ RAG engine initialized")
    
    # Step 2: Initialize comparison service
    print("\n2️⃣  Initializing Model Comparison Service...")
    comparison_service = ModelComparisonService(rag_engine)
    print("   ✅ Comparison service ready")
    
    # Step 3: Test with a sample query
    test_query = "What is the leave policy?"
    print(f"\n3️⃣  Testing model comparison with query:")
    print(f"   📝 \"{test_query}\"")
    
    # Compare all 4 Groq models
    models_to_compare = [
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "openai/gpt-oss-20b",
        "qwen/qwen3-32b",
    ]
    print(f"\n   Comparing 4 Groq models:")
    print(f"   • Llama 3.3 70B")
    print(f"   • Llama 4 Maverick 17B")
    print(f"   • GPT-OSS 20B")
    print(f"   • Qwen3 32B")
    print("   ⏳ This may take a moment...")
    
    try:
        result = await comparison_service.compare_models(
            query=test_query,
            models=models_to_compare,
            top_k=5
        )
        
        print("\n" + "=" * 60)
        print("📊 COMPARISON RESULTS")
        print("=" * 60)
        
        print(f"\n⏱️  Total comparison time: {result.get('comparison_time', 0)}s")
        print(f"📚 Context chunks used: {result.get('context_chunks', 0)}")
        print(f"🏆 Best model: {result.get('best_model', 'N/A')}")
        
        for i, model_result in enumerate(result.get("results", []), 1):
            print(f"\n{'='*50}")
            print(f"Model #{i}: {model_result['model']}")
            print(f"{'='*50}")
            
            scores = model_result.get("scores", {})
            print(f"\n📈 Scores:")
            print(f"   • Relevance:    {scores.get('relevance', 0):.2f}")
            print(f"   • Faithfulness: {scores.get('faithfulness', 0):.2f}")
            print(f"   • Completeness: {scores.get('completeness', 0):.2f}")
            print(f"   • Overall:      {scores.get('overall', 0):.2f}")
            
            print(f"\n⚡ Generation time: {model_result.get('generation_time', 0):.3f}s")
            
            tokens = model_result.get("tokens", {})
            print(f"🔢 Tokens used: {tokens.get('total', 0)}")
            
            print(f"\n💬 Answer preview:")
            answer = model_result.get("answer", "No answer")
            print(f"   {answer[:300]}..." if len(answer) > 300 else f"   {answer}")
            
            reasoning = scores.get("reasoning", {})
            if reasoning:
                print(f"\n📝 Evaluation reasoning:")
                if reasoning.get("relevance"):
                    print(f"   • Relevance: {reasoning['relevance'][:100]}...")
                if reasoning.get("faithfulness"):
                    print(f"   • Faithfulness: {reasoning['faithfulness'][:100]}...")
        
        print("\n" + "=" * 60)
        print("✅ Model comparison test completed successfully!")
        print("=" * 60)
        
        print("\n💡 Check your OPIK dashboard to see the traced comparison:")
        print(f"   https://www.comet.com/opik/parth-d/projects")
        
    except Exception as e:
        print(f"\n❌ Comparison error: {e}")
        import traceback
        traceback.print_exc()


async def test_single_evaluation():
    """Test evaluating a single response."""
    print("\n" + "=" * 60)
    print("🔍 Single Response Evaluation Test")
    print("=" * 60)
    
    evaluator = LLMEvaluator()
    
    # Sample data
    question = "What is the annual leave entitlement?"
    context = """
    According to the company policy:
    - All full-time employees are entitled to 20 days of annual leave per year.
    - Part-time employees receive prorated leave based on their working hours.
    - Unused leave can be carried forward up to 5 days into the next year.
    """
    answer = "Full-time employees are entitled to 20 days of annual leave per year. Part-time employees receive prorated leave."
    
    print(f"\n📝 Question: {question}")
    print(f"💬 Answer: {answer}")
    
    scores = evaluator.evaluate(
        question=question,
        context=context,
        answer=answer,
        model_used="test-model"
    )
    
    print(f"\n📊 Evaluation Scores:")
    print(f"   • Relevance:    {scores.relevance:.2f}")
    print(f"   • Faithfulness: {scores.faithfulness:.2f}")
    print(f"   • Completeness: {scores.completeness:.2f}")
    print(f"   • Overall:      {scores.overall:.2f}")
    
    print("\n✅ Single evaluation test completed!")


if __name__ == "__main__":
    print("\n🚀 Starting Model Comparison Tests\n")
    
    # Run single evaluation test first (fast)
    asyncio.run(test_single_evaluation())
    
    # Run full model comparison test
    asyncio.run(test_model_comparison())
