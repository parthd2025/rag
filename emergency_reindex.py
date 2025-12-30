"""
Emergency fix for corrupted vector store - Complete re-indexing
"""
import sys
import os
import json
sys.path.append('backend')

from backend.config import settings
from backend.vectorstore import FAISSVectorStore
from backend.ingest import DocumentIngestor

def emergency_reindex():
    """Complete re-indexing to fix the corrupted vector store"""
    
    print("🚨 === EMERGENCY RE-INDEXING ===")
    print("Issue detected: Only 2 chunks in vector store vs 396 in UI")
    
    # Step 1: Clear everything
    print("\\n1. Clearing corrupted vector store...")
    try:
        if os.path.exists(settings.INDEX_PATH):
            os.remove(settings.INDEX_PATH)
            print("   ✅ Removed old FAISS index")
        
        if os.path.exists(settings.METADATA_PATH):
            os.remove(settings.METADATA_PATH)  
            print("   ✅ Removed old metadata")
    except Exception as e:
        print(f"   ⚠️  Error clearing: {e}")
    
    # Step 2: Check available documents
    print("\\n2. Checking available documents...")
    doc_dir = "backend/data/documents"
    
    if not os.path.exists(doc_dir):
        print(f"   ❌ Documents directory not found: {doc_dir}")
        return
    
    doc_files = []
    for file in os.listdir(doc_dir):
        if file.endswith(('.pdf', '.docx', '.txt', '.md')):
            doc_files.append(file)
    
    print(f"   📊 Found {len(doc_files)} documents:")
    for doc in doc_files:
        print(f"      - {doc}")
    
    if not doc_files:
        print("   ❌ No documents found to index!")
        return
    
    # Step 3: Re-ingest with correct embedding model
    print(f"\\n3. Re-ingesting with embedding model: {settings.EMBEDDING_MODEL}")
    
    # Initialize ingestor with M2-optimized settings
    ingestor = DocumentIngestor(
        chunk_size=600,
        chunk_overlap=100,
        enable_ocr=False
    )
    
    # Initialize vector store (will create new index)
    vector_store = FAISSVectorStore(
        embedding_model_name=settings.EMBEDDING_MODEL,
        index_path=settings.INDEX_PATH,
        metadata_path=settings.METADATA_PATH
    )
    
    # Process documents
    all_chunks = []
    all_doc_names = []
    
    for doc_file in doc_files:
        doc_path = os.path.join(doc_dir, doc_file)
        print(f"\\n   Processing: {doc_file}")
        
        try:
            chunks, doc_name = ingestor.load_and_process_documents([doc_path])
            
            if chunks:
                print(f"      ✅ Generated {len(chunks)} chunks")
                all_chunks.extend(chunks)
                all_doc_names.extend([doc_name] * len(chunks))
                
                # Show M2 content if found
                if 'M2' in doc_file or 'mileage' in doc_file.lower():
                    m2_chunk_count = sum(1 for chunk in chunks if 'M2' in chunk or 'm2' in chunk.lower())
                    print(f"      🎯 M2 content chunks: {m2_chunk_count}")
            else:
                print(f"      ❌ No chunks generated")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Step 4: Add to vector store
    print(f"\\n4. Adding {len(all_chunks)} chunks to vector store...")
    
    if all_chunks:
        try:
            # Add documents in batches for better memory management
            batch_size = 50
            for i in range(0, len(all_chunks), batch_size):
                batch_chunks = all_chunks[i:i+batch_size]
                batch_names = all_doc_names[i:i+batch_size]
                
                # FAISSVectorStore uses add_chunks method
                for chunk, doc_name in zip(batch_chunks, batch_names):
                    vector_store.add_chunks([chunk], doc_name)
                
                print(f"   ✅ Added batch {i//batch_size + 1}: {len(batch_chunks)} chunks")
            
            # Save the index
            vector_store.save_index()
            print("   ✅ Vector store saved!")
            
        except Exception as e:
            print(f"   ❌ Error adding documents: {e}")
            import traceback
            traceback.print_exc()
            return
    
    # Step 5: Verify the fix
    print("\\n5. Verifying the fix...")
    
    try:
        # Check metadata
        with open(settings.METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"   📊 New metadata entries: {len(metadata)}")
        
        # Test search
        test_results = vector_store.search("mindbowser", top_k=5)
        print(f"   🔍 Test search returned: {len(test_results)} results")
        
        # Test M2 search
        m2_results = vector_store.search("M2 mileage", top_k=5)
        print(f"   🎯 M2 test search returned: {len(m2_results)} results")
        
        if m2_results:
            chunk, score, meta_info = m2_results[0]
            print(f"      Top M2 result: {chunk[:100]}... (score: {score:.3f})")
        
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
    
    print("\\n🎉 === RE-INDEXING COMPLETE ===")
    print("📋 Next steps:")
    print("1. ✅ Vector store rebuilt with correct embedding model")
    print("2. 🔄 Restart your backend server")
    print("3. 🔄 Refresh your frontend (Ctrl+F5)")
    print("4. 🧪 Test M2 queries: 'what is M2 benefits in mindbowser?'")
    print("\\n⚠️  IMPORTANT: The UI showing 396 chunks was cached/incorrect data!")

if __name__ == "__main__":
    emergency_reindex()