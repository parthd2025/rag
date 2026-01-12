"""
Re-ingest documents with improved chunking for M2 terms
"""
import sys
import os
sys.path.append('backend')

from backend.config import settings
from backend.ingest import DocumentIngestor
from backend.vectorstore import VectorStoreManager
import json

def re_ingest_with_improvements():
    """Re-ingest documents with improved chunking settings"""
    
    print("=== Re-ingesting Documents with M2 Optimization ===")
    
    # Use improved chunking settings
    ingestor = DocumentIngestor(
        chunk_size=800,  # Smaller for better precision
        chunk_overlap=100,  # More overlap for context
        enable_ocr=False,
        chunking_level=4  # Medium-high level
    )
    
    vector_store = VectorStoreManager(
        index_path=settings.INDEX_PATH,
        metadata_path=settings.METADATA_PATH,
        model_name=settings.EMBEDDING_MODEL
    )
    
    # Clear existing index
    print("1. Clearing existing vector store...")
    vector_store.clear_index()
    
    # Get document files
    doc_dir = "backend/data/documents"
    doc_files = []
    
    for file in os.listdir(doc_dir):
        if file.endswith(('.pdf', '.docx', '.txt', '.md')):
            doc_files.append(os.path.join(doc_dir, file))
    
    print(f"2. Found {len(doc_files)} documents to process")
    
    # Process each document individually for better tracking
    for doc_file in doc_files:
        print(f"3. Processing: {doc_file}")
        
        try:
            chunks, doc_name = ingestor.load_and_process_documents([doc_file])
            
            if chunks:
                # Add to vector store
                vector_store.add_documents(chunks, [doc_name] * len(chunks))
                print(f"   ✅ Added {len(chunks)} chunks from {doc_name}")
                
                # Show chunk stats for M2 document
                if 'M2' in doc_name or 'mileage' in doc_name.lower():
                    print(f"   📊 M2 Document Stats:")
                    print(f"      - Chunks: {len(chunks)}")
                    print(f"      - Avg chunk size: {sum(len(c) for c in chunks) // len(chunks)}")
                    
                    # Show first few chunks that contain M2
                    m2_chunks = [c for c in chunks if 'M2' in c or 'm2' in c.lower()]
                    print(f"      - M2-containing chunks: {len(m2_chunks)}")
                    for i, chunk in enumerate(m2_chunks[:2]):
                        print(f"      - Sample {i+1}: {chunk[:100]}...")
            else:
                print(f"   ❌ No chunks extracted from {doc_file}")
                
        except Exception as e:
            print(f"   ❌ Error processing {doc_file}: {e}")
    
    print("4. Saving vector store...")
    vector_store.save_index()
    
    print("✅ Re-ingestion complete!")
    print("\nRecommendations:")
    print("1. Restart your backend server")
    print("2. Test queries like 'M2 benefits' or 'M2 mileage policy'")
    print("3. Check that M2 document is being retrieved in responses")

if __name__ == "__main__":
    re_ingest_with_improvements()