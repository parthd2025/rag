import sys
import os
import json
sys.path.append('backend')

from backend.ingest import DocumentIngestor
from backend.vectorstore import FAISSVectorStore

def complete_ingestion():
    """Complete the document ingestion by adding processed chunks to vector store."""
    print("=== Complete Document Ingestion to Vector Store ===\n")
    
    try:
        # Initialize components
        ingestor = DocumentIngestor()
        vector_store = FAISSVectorStore()
        
        print("✅ Initialized ingestor and vector store")
        
        # Get document files
        docs_dir = "backend/data/documents"
        files = [f for f in os.listdir(docs_dir) if not f.startswith('.') and os.path.isfile(os.path.join(docs_dir, f))]
        
        print(f"📄 Found {len(files)} files to process:")
        for f in files:
            size = os.path.getsize(os.path.join(docs_dir, f))
            print(f"   - {f} ({size:,} bytes)")
            
        all_chunks = []
        source_documents = []
        
        # Process each file and collect chunks
        for filename in files:
            print(f"\n📥 Processing: {filename}")
            file_path = os.path.join(docs_dir, filename)
            
            try:
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                    
                # Process the file
                chunks, summary, metadata = ingestor.process_uploaded_file(file_content, filename)
                
                print(f"   ✅ Processed: {len(chunks)} chunks")
                print(f"   📝 Summary: {summary}")
                
                # Add source info to chunks (this might be needed)
                for chunk in chunks:
                    all_chunks.append(chunk)
                    
                source_documents.append(filename)
                
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
                continue
        
        print(f"\n📊 Total chunks collected: {len(all_chunks)}")
        print(f"📄 Source documents: {len(source_documents)}")
        
        if all_chunks:
            # Add chunks to vector store
            print("💾 Adding chunks to FAISS vector store...")
            vector_store.add_chunks(all_chunks, source_documents)
            print("✅ Chunks added to vector store successfully!")
            
            # Verify the results
            print("\n🔍 Verifying results...")
            if hasattr(vector_store, 'index') and vector_store.index:
                print(f"✅ FAISS index contains {vector_store.index.ntotal} vectors")
            
            # Check metadata file
            metadata_path = vector_store.metadata_path
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"✅ Metadata file contains {len(metadata.get('chunks', []))} chunks")
                print(f"✅ Source documents: {metadata.get('source_documents', [])}")
                
                # Test search for loan/policy content
                chunks = metadata.get('chunks', [])
                loan_count = sum(1 for chunk in chunks if 'loan' in str(chunk).lower() or 'policy' in str(chunk).lower())
                print(f"📝 Chunks with 'loan' or 'policy': {loan_count}")
                
            else:
                print("❌ No metadata file created")
        else:
            print("❌ No chunks to add to vector store")
            
    except Exception as e:
        print(f"❌ Error during complete ingestion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    complete_ingestion()