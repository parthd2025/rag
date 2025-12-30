"""
Test script to debug M2 mileage retrieval issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import settings
from backend.vectorstore import VectorStoreManager
from backend.rag_engine import RAGEngine
from backend.llm_loader import LLMEngine

def test_m2_mileage_retrieval():
    """Test different queries for M2 mileage information"""
    
    print("=== Testing M2 Mileage Retrieval ===")
    
    # Initialize components
    vector_store = VectorStoreManager(
        index_path=settings.INDEX_PATH,
        metadata_path=settings.METADATA_PATH,
        model_name=settings.EMBEDDING_MODEL
    )
    
    llm_engine = LLMEngine(
        model_name=settings.LLM_MODEL,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS
    )
    
    rag_engine = RAGEngine(
        vector_store=vector_store,
        llm_engine=llm_engine,
        top_k=8,  # Increase to get more results
        temperature=settings.TEMPERATURE,
        enable_hybrid_search=True,
        keyword_weight=0.4,  # Increase keyword weight
        semantic_weight=0.6
    )
    
    # Test queries with variations
    test_queries = [
        "m2 mileage",
        "M2 mileage", 
        "mindbowser mileage M2",
        "MindBowser Mileages M2",
        "what is m2 mileage",
        "lm2 mileage",  # Original typo
        "mileage policy M2",
        "travel allowance M2",
        "transportation M2"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i}: '{query}' ---")
        
        try:
            # Test retrieval context first
            context = rag_engine.retrieve_context(query, top_k=10)
            print(f"Retrieved {len(context['chunks'])} chunks")
            print(f"Average confidence: {context['confidence']:.4f}")
            
            # Show top results with metadata
            for j, metadata in enumerate(context['metadata'][:3]):
                print(f"Result {j+1}: {metadata['document_name'][:50]}")
                print(f"  Score: {metadata['similarity']:.4f}")
                print(f"  Preview: {metadata['chunk_preview'][:100]}...")
                
            # Test full RAG query
            print(f"\n=== Full RAG Response ===")
            response = rag_engine.query(query)
            print(f"Answer: {response['answer'][:200]}...")
            print(f"Sources used: {len(response['sources'])}")
            
        except Exception as e:
            print(f"Error testing query '{query}': {e}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_m2_mileage_retrieval()