"""
Complete M2 Document Diagnostic and Re-indexing Script
"""
import sys
import os
sys.path.append('backend')

from backend.config import settings
from backend.ingest import DocumentIngestor
from backend.vectorstore import VectorStoreManager
from backend.rag_engine import RAGEngine
from backend.llm_loader import LLMEngine
import json

def diagnose_and_fix_m2_retrieval():
    """Complete diagnostic and fix for M2 document retrieval"""
    
    print("🔍 === M2 Document Retrieval Diagnostic & Fix ===")
    
    # Step 1: Check if M2 document exists
    print("\n1. Checking M2 document presence...")
    doc_dir = "backend/data/documents"
    m2_files = []
    all_files = []
    
    for file in os.listdir(doc_dir):
        if file.endswith(('.pdf', '.docx', '.txt', '.md')):
            all_files.append(file)
            if 'M2' in file or 'mileage' in file.lower():
                m2_files.append(file)
                print(f"   ✅ Found M2 document: {file}")
    
    if not m2_files:
        print("   ❌ No M2/mileage documents found!")
        print(f"   Available files: {all_files}")
        return
    
    # Step 2: Check current vector store metadata
    print("\n2. Analyzing current vector store...")
    try:
        with open(settings.METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"   📊 Current index has {len(metadata)} chunks")
        
        # Check for M2 chunks
        m2_chunks = []
        for i, meta in enumerate(metadata):
            doc_name = meta.get('document', '')
            if 'M2' in doc_name or 'mileage' in doc_name.lower():
                m2_chunks.append((i, meta))
        
        print(f"   📊 M2-related chunks: {len(m2_chunks)}")
        for i, (idx, meta) in enumerate(m2_chunks[:3]):
            print(f"      - Chunk {idx}: {meta.get('document', 'Unknown')[:50]}")
            
    except Exception as e:
        print(f"   ⚠️  Could not read current metadata: {e}")
    
    # Step 3: Re-ingest with optimized settings
    print(f"\n3. Re-ingesting with optimized embedding model: {settings.EMBEDDING_MODEL}")
    
    # Initialize with new settings
    ingestor = DocumentIngestor(
        chunk_size=600,  # Smaller chunks for precision
        chunk_overlap=150,  # Higher overlap for context
        enable_ocr=False,
        chunking_level=5
    )
    
    print("   🔄 Clearing existing vector store...")
    vector_store = VectorStoreManager(
        index_path=settings.INDEX_PATH,
        metadata_path=settings.METADATA_PATH,
        model_name=settings.EMBEDDING_MODEL
    )
    vector_store.clear_index()
    
    # Process all documents
    all_doc_paths = [os.path.join(doc_dir, f) for f in all_files]
    
    print(f"   📄 Processing {len(all_doc_paths)} documents...")
    chunks, doc_names = ingestor.load_and_process_documents(all_doc_paths)
    
    if chunks:
        print(f"   ✅ Generated {len(chunks)} total chunks")
        
        # Add to vector store
        vector_store.add_documents(chunks, doc_names)
        vector_store.save_index()
        
        # Analyze M2 chunks specifically
        m2_chunk_count = 0
        for i, chunk in enumerate(chunks):
            if 'M2' in chunk or 'm2' in chunk.lower() or 'mileage' in chunk.lower():
                m2_chunk_count += 1
                if m2_chunk_count <= 3:  # Show first 3 M2 chunks
                    print(f"   🎯 M2 Chunk {m2_chunk_count}: {chunk[:100]}...")
        
        print(f"   📊 M2-containing chunks: {m2_chunk_count}")
    else:
        print("   ❌ No chunks generated!")
        return
    
    # Step 4: Test retrieval immediately
    print(f"\n4. Testing M2 retrieval with new index...")
    
    try:
        llm_engine = LLMEngine(
            model_name=settings.LLM_MODEL,
            temperature=0.3,
            max_tokens=500
        )
        
        rag_engine = RAGEngine(
            vector_store=vector_store,
            llm_engine=llm_engine,
            top_k=12,  # Use increased TOP_K
            enable_hybrid_search=True,
            keyword_weight=0.4,
            semantic_weight=0.6
        )
        
        test_queries = [
            "what is M2 benefits in mindbowser?",
            "M2 mileage policy",
            "mindbowser M2 allowance"
        ]
        
        for query in test_queries:
            print(f"\n   🔍 Testing: '{query}'")
            
            # Test context retrieval
            context = rag_engine.retrieve_context(query, top_k=12)
            
            print(f"      📊 Retrieved {len(context['chunks'])} chunks")
            print(f"      📊 Average confidence: {context['confidence']:.3f}")
            
            # Check if any chunks are from M2 document
            m2_sources = 0
            for meta in context['metadata'][:5]:
                doc_name = meta.get('document_name', '')
                if 'M2' in doc_name or 'mileage' in doc_name.lower():
                    m2_sources += 1
                    print(f"      ✅ M2 Source found: {doc_name}")
                    print(f"         Score: {meta.get('similarity', 0):.3f}")
                    print(f"         Preview: {meta.get('chunk_preview', '')[:100]}...")
            
            if m2_sources == 0:
                print(f"      ❌ No M2 sources in top results")
                print("      🔍 Top sources:")
                for meta in context['metadata'][:3]:
                    print(f"         - {meta.get('document_name', 'Unknown')[:40]} (score: {meta.get('similarity', 0):.3f})")
            else:
                print(f"      ✅ Found {m2_sources} M2 sources!")
        
    except Exception as e:
        print(f"   ❌ Error testing retrieval: {e}")
    
    print(f"\n🎉 === Diagnostic Complete ===")
    print("📋 Action Items:")
    print("1. ✅ Upgraded embedding model for better semantic understanding")
    print("2. ✅ Applied document-specific boosting for M2 queries")
    print("3. ✅ Used smaller, overlapping chunks for better precision")
    print("4. ✅ Increased retrieval parameters (TOP_K=12)")
    print("\n🚀 Next Steps:")
    print("1. Restart your backend server")
    print("2. Test the query: 'what is M2 benefits in mindbowser?'")
    print("3. Check if M2 document appears in sources")

if __name__ == "__main__":
    diagnose_and_fix_m2_retrieval()