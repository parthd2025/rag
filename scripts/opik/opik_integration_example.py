"""
Opik Integration Example for RAG System

This demonstrates how to integrate Opik tracing into the RAG system.
"""

import opik
from opik import track
from opik.decorator import tracker


# Example 1: Track a simple function
@track()
def query_rag_simple(question: str) -> dict:
    """Simple RAG query with Opik tracking"""
    # Your RAG logic here
    response = {
        "answer": "Example answer",
        "sources": ["doc1.pdf", "doc2.pdf"],
        "question": question
    }
    return response


# Example 2: Track with custom metadata
@track(
    name="RAG Query with Metadata",
    project_name="rag-system",
    tags=["rag", "retrieval"]
)
def query_rag_with_metadata(question: str, top_k: int = 5) -> dict:
    """RAG query with custom metadata tracking"""
    
    # Simulate retrieval
    retrieved_docs = ["doc1", "doc2", "doc3"]
    
    # Simulate generation  
    answer = f"Generated answer for: {question}"
    
    return {
        "answer": answer,
        "sources": retrieved_docs,
        "question": question,
        "top_k": top_k
    }


# Example 3: Manual tracking with client
def query_rag_manual(question: str) -> dict:
    """Manual Opik tracking for more control"""
    
    client = opik.Opik()
    
    # Create a trace
    trace = client.trace(
        name="RAG Query - Manual",
        input={"question": question},
        project_name="rag-system",
        tags=["rag", "manual"]
    )
    
    # Track retrieval
    retrieval_span = trace.span(
        name="Document Retrieval",
        input={"question": question, "top_k": 5}
    )
    retrieved_docs = ["doc1.pdf", "doc2.pdf"]
    retrieval_span.end(output={"documents": retrieved_docs})
    
    # Track generation
    generation_span = trace.span(
        name="Answer Generation",
        input={"documents": retrieved_docs, "question": question}
    )
    answer = "Generated answer"
    generation_span.end(output={"answer": answer})
    
    # End trace
    trace.end(output={"answer": answer, "sources": retrieved_docs})
    
    return {
        "answer": answer,
        "sources": retrieved_docs,
        "question": question
    }


# Example 4: Integration with LangChain (Optional - requires langchain package)
def setup_langchain_with_opik():
    """Example of integrating Opik with LangChain
    
    To use this, install langchain first:
    pip install langchain langchain-community
    """
    try:
        from langchain.callbacks import OpikCallbackHandler
        
        # Create callback handler
        opik_callback = OpikCallbackHandler(
            project_name="rag-system",
            tags=["langchain", "rag"]
        )
        
        # Use with LangChain
        # chain.run(query, callbacks=[opik_callback])
        
        return opik_callback
    except ImportError:
        print("⚠️  LangChain not installed. Install with: pip install langchain langchain-community")
        return None


if __name__ == "__main__":
    # Test simple tracking
    print("Testing Opik integration...")
    
    # Test 1: Simple tracking
    result1 = query_rag_simple("What is AI?")
    print(f"✅ Simple tracking: {result1['answer']}")
    
    # Test 2: Metadata tracking
    result2 = query_rag_with_metadata("What is machine learning?", top_k=3)
    print(f"✅ Metadata tracking: {result2['answer']}")
    
    # Test 3: Manual tracking
    result3 = query_rag_manual("What is deep learning?")
    print(f"✅ Manual tracking: {result3['answer']}")
    
    print("\n🎉 All tests passed! Check the Opik UI at http://localhost:5173")
