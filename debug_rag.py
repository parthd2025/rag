#!/usr/bin/env python3
"""
RAG System Debug Utility

This script helps debug issues with the RAG system by providing detailed
step-by-step analysis of the question-answering pipeline.

Usage:
    python debug_rag.py "Your question here"
    python debug_rag.py --interactive
    python debug_rag.py --test-questions
"""

import sys
import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.main import vector_store, llm_engine, rag_engine
    from backend.logger_config import logger
    from backend.config import settings
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Make sure you're running this from the RAG project root directory")
    print("Also ensure the backend services are initialized by running: python backend/main.py (in background)")
    
    # Try to initialize manually
    try:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from backend.vectorstore import FAISSVectorStore
        from backend.llm_loader import get_llm_engine
        from backend.rag_engine import RAGEngine
        from backend.config import settings
        from backend.logger_config import logger
        
        print("Initializing RAG components manually...")
        vector_store = FAISSVectorStore()
        llm_engine = get_llm_engine(use_groq=(settings.LLM_PROVIDER.lower() == "groq"))
        rag_engine = RAGEngine(vector_store=vector_store, llm_engine=llm_engine) if vector_store and llm_engine else None
        
    except Exception as e2:
        print(f"Failed to initialize manually: {e2}")
        print("Please start the backend service first: python backend/main.py")
        sys.exit(1)

class RAGDebugger:
    """Debug utility for RAG system analysis."""
    
    def __init__(self):
        self.vector_store = vector_store
        self.llm_engine = llm_engine
        self.rag_engine = rag_engine
        
        # Set debug logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    def debug_query(self, question: str, detailed: bool = True) -> Dict[str, Any]:
        """Debug a specific query step by step."""
        print(f"\n{'='*60}")
        print(f"DEBUGGING QUERY: {question}")
        print(f"{'='*60}")
        
        debug_results = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "recommendations": []
        }
        
        # Step 1: System Status
        print(f"\n--- STEP 1: SYSTEM STATUS ---")
        vector_available = self.vector_store and len(self.vector_store.chunks) > 0
        llm_available = self.llm_engine and self.llm_engine.is_ready()
        rag_available = self.rag_engine is not None
        
        debug_results["steps"]["system_status"] = {
            "vector_store_available": vector_available,
            "llm_engine_available": llm_available,
            "rag_engine_available": rag_available,
            "total_chunks": len(self.vector_store.chunks) if self.vector_store else 0,
            "settings": {
                "top_k": settings.TOP_K,
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_TOKENS,
                "context_window_size": settings.CONTEXT_WINDOW_SIZE
            }
        }
        
        print(f"  Vector Store: {'✓' if vector_available else '✗'} ({len(self.vector_store.chunks) if self.vector_store else 0} chunks)")
        print(f"  LLM Engine: {'✓' if llm_available else '✗'}")
        print(f"  RAG Engine: {'✓' if rag_available else '✗'}")
        print(f"  Settings: TOP_K={settings.TOP_K}, TEMP={settings.TEMPERATURE}, MAX_TOKENS={settings.MAX_TOKENS}")
        
        if not vector_available:
            debug_results["recommendations"].append("No documents loaded - please upload documents first")
            return debug_results
        
        if not llm_available:
            debug_results["recommendations"].append("LLM engine not available - check API configuration")
            return debug_results
        
        # Step 2: Vector Search Analysis
        print(f"\n--- STEP 2: VECTOR SEARCH ANALYSIS ---")
        try:
            search_results = self.vector_store.search(question, top_k=settings.TOP_K)
            debug_results["steps"]["vector_search"] = {
                "success": True,
                "results_count": len(search_results),
                "results": []
            }
            
            print(f"  Found {len(search_results)} results:")
            for i, (chunk, similarity, metadata) in enumerate(search_results[:5], 1):
                doc_name = metadata.get('source_doc', 'unknown')
                page = metadata.get('page', 'N/A')
                section = metadata.get('section', 'N/A')
                
                result_info = {
                    "rank": i,
                    "similarity": similarity,
                    "document": doc_name,
                    "page": page,
                    "section": section,
                    "chunk_length": len(chunk),
                    "preview": chunk[:200] + "..." if len(chunk) > 200 else chunk
                }
                debug_results["steps"]["vector_search"]["results"].append(result_info)
                
                print(f"    {i}. Similarity: {similarity:.4f} | Doc: {doc_name} | Page: {page}")
                if detailed:
                    print(f"       Preview: {chunk[:150]}...")
                    print()
            
            # Analyze similarity distribution
            similarities = [sim for _, sim, _ in search_results]
            if similarities:
                avg_sim = sum(similarities) / len(similarities)
                max_sim = max(similarities)
                min_sim = min(similarities)
                high_sim_count = sum(1 for sim in similarities if sim > 0.6)
                
                debug_results["steps"]["vector_search"]["similarity_analysis"] = {
                    "average": avg_sim,
                    "maximum": max_sim,
                    "minimum": min_sim,
                    "high_similarity_count": high_sim_count,
                    "distribution": "good" if avg_sim > 0.5 else "moderate" if avg_sim > 0.3 else "poor"
                }
                
                print(f"  Similarity Analysis:")
                print(f"    Average: {avg_sim:.4f} | Max: {max_sim:.4f} | Min: {min_sim:.4f}")
                print(f"    High similarity (>0.6): {high_sim_count}/{len(similarities)}")
                
                if avg_sim < 0.3:
                    debug_results["recommendations"].append("Low similarity scores - question may not match document content")
                elif avg_sim < 0.5:
                    debug_results["recommendations"].append("Moderate similarity - consider rephrasing question")
                else:
                    debug_results["recommendations"].append("Good similarity scores - relevant content found")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            debug_results["steps"]["vector_search"] = {"success": False, "error": str(e)}
            debug_results["recommendations"].append(f"Vector search failed: {e}")
            return debug_results
        
        # Step 3: RAG Generation
        print(f"\n--- STEP 3: RAG GENERATION ---")
        try:
            # Add debug logging before RAG call
            print(f"  Calling RAG engine with question length: {len(question)} chars")
            
            rag_result = self.rag_engine.answer_query_with_context(question)
            
            debug_results["steps"]["rag_generation"] = {
                "success": True,
                "answer_length": len(rag_result.get("answer", "")),
                "sources_count": len(rag_result.get("sources", [])),
                "has_verification": "verification" in rag_result
            }
            
            answer = rag_result.get("answer", "No answer generated")
            sources = rag_result.get("sources", [])
            verification = rag_result.get("verification", {})
            
            print(f"  Answer Generated: {'✓' if answer and answer != 'No answer generated' else '✗'}")
            print(f"  Answer Length: {len(answer)} characters")
            print(f"  Sources Used: {len(sources)}")
            
            if detailed and answer:
                print(f"  Answer Preview:")
                print(f"    {answer[:300]}{'...' if len(answer) > 300 else ''}")
                print()
            
            # Step 4: Verification Analysis
            if verification:
                print(f"--- STEP 4: VERIFICATION ANALYSIS ---")
                debug_results["steps"]["verification"] = verification
                
                is_verified = verification.get("is_verified", False)
                confidence = verification.get("confidence_score", 0.0)
                recommendations = verification.get("recommendations", [])
                
                print(f"  Verified: {'✓' if is_verified else '✗'}")
                print(f"  Confidence Score: {confidence:.3f}")
                
                if recommendations:
                    print(f"  Recommendations:")
                    for rec in recommendations:
                        print(f"    - {rec}")
                        debug_results["recommendations"].append(rec)
                
                # Analyze source coverage
                source_coverage = verification.get("source_coverage", {})
                if source_coverage:
                    print(f"  Source Coverage:")
                    for doc, info in source_coverage.items():
                        print(f"    {doc}: {info['count']} chunks, avg similarity: {info['avg_similarity']:.4f}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            debug_results["steps"]["rag_generation"] = {"success": False, "error": str(e)}
            debug_results["recommendations"].append(f"RAG generation failed: {e}")
        
        # Summary
        print(f"\n--- SUMMARY ---")
        if debug_results["recommendations"]:
            print("Recommendations:")
            for i, rec in enumerate(debug_results["recommendations"], 1):
                print(f"  {i}. {rec}")
        else:
            print("No specific recommendations - system appears to be working correctly.")
        
        return debug_results
    
    def test_sample_questions(self):
        """Test with a set of sample questions to identify patterns."""
        sample_questions = [
            "What is the main topic of this document?",
            "What are the key requirements mentioned?",
            "How do I get started?",
            "What are the installation steps?",
            "What is the system architecture?",
            "What are the troubleshooting steps?",
            "Who is the target audience?",
            "What are the benefits and limitations?"
        ]
        
        print(f"\n{'='*60}")
        print(f"TESTING SAMPLE QUESTIONS")
        print(f"{'='*60}")
        
        results = []
        for i, question in enumerate(sample_questions, 1):
            print(f"\n[TEST {i}/{len(sample_questions)}] Testing: {question}")
            try:
                result = self.debug_query(question, detailed=False)
                results.append(result)
                
                # Quick assessment
                vector_success = result["steps"].get("vector_search", {}).get("success", False)
                rag_success = result["steps"].get("rag_generation", {}).get("success", False)
                
                print(f"  Result: Vector {'✓' if vector_success else '✗'} | RAG {'✓' if rag_success else '✗'}")
                
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({"question": question, "error": str(e)})
        
        # Summary of test results
        successful_tests = sum(1 for r in results if r.get("steps", {}).get("rag_generation", {}).get("success", False))
        print(f"\n--- TEST RESULTS SUMMARY ---")
        print(f"Successful queries: {successful_tests}/{len(sample_questions)}")
        
        if successful_tests < len(sample_questions):
            print("Issues detected - review individual test results above")
        else:
            print("All tests passed - system appears to be working correctly")
        
        return results
    
    def interactive_mode(self):
        """Interactive debugging mode."""
        print(f"\n{'='*60}")
        print("RAG SYSTEM INTERACTIVE DEBUG MODE")
        print(f"{'='*60}")
        print("Enter questions to debug (type 'exit' to quit, 'test' for sample questions)")
        
        while True:
            try:
                question = input("\nEnter question: ").strip()
                
                if question.lower() == 'exit':
                    break
                elif question.lower() == 'test':
                    self.test_sample_questions()
                    continue
                elif not question:
                    continue
                
                self.debug_query(question)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function to run the debug utility."""
    if len(sys.argv) < 2:
        print("RAG Debug Utility")
        print("Usage:")
        print("  python debug_rag.py \"Your question here\"")
        print("  python debug_rag.py --interactive")
        print("  python debug_rag.py --test-questions")
        return
    
    debugger = RAGDebugger()
    
    if sys.argv[1] == "--interactive":
        debugger.interactive_mode()
    elif sys.argv[1] == "--test-questions":
        debugger.test_sample_questions()
    else:
        question = " ".join(sys.argv[1:])
        debugger.debug_query(question)

if __name__ == "__main__":
    main()