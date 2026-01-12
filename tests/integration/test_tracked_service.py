"""Test the TrackedRAGService to verify full Opik pipeline tracing."""

import asyncio
import sys
sys.path.insert(0, '.')

from backend.services.tracked_chat_service import TrackedRAGService, LITELLM_AVAILABLE
from backend.vectorstore import FAISSVectorStore
from backend.llm_loader import get_llm_engine
from backend.rag_engine import RAGEngine
from backend.config import settings

print(f'LiteLLM Available: {LITELLM_AVAILABLE}')
print('TrackedRAGService imported successfully!')

# Initialize components
print('Initializing vectorstore...')
vs = FAISSVectorStore(
    embedding_model_name=settings.EMBEDDING_MODEL,
    index_path=settings.INDEX_PATH,
    metadata_path=settings.METADATA_PATH
)
print(f'Chunks: {len(vs.chunks)}')

print('Initializing LLM...')
llm = get_llm_engine()
print(f'LLM Ready: {llm.is_ready()}')

print('Initializing RAG engine...')
rag = RAGEngine(vector_store=vs, llm_engine=llm)

print('Initializing TrackedRAGService...')
service = TrackedRAGService(rag)
print('TrackedRAGService ready!')

# Test a query
print('\n=== Testing query with full Opik tracing ===')
result = asyncio.run(service.process_query('What is loan in mindbowser?', top_k=3, temperature=0.7))
print(f'\nAnswer: {result["answer"][:200]}...')
print(f'\nSources: {len(result.get("sources", []))}')
print(f'Confidence: {result.get("confidence", 0)}')
print(f'Metrics: {result.get("metrics", {})}')

print('\n=== SUCCESS! Check your Opik dashboard for the full trace ===')
print('Dashboard: https://www.comet.com/opik/parth-d -> Projects -> rag-system')
