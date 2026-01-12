import sys
import os
sys.path.append('backend')

from backend.ingest import DocumentIngestor
from backend.vectorstore import FAISSVectorStore
import time

def re_ingest_documents():
    """Re-ingest all documents in the documents directory."""
    print("=== Re-ingesting Documents ===\n")
    
    try:
        # Initialize components
        print("🔧 Initializing document ingestor...")
        ingestor = DocumentIngestor()
        print("✅ Document ingestor initialized")
        
        # Get list of documents
        docs_dir = "backend/data/documents"
        if not os.path.exists(docs_dir):
            print(f"❌ Documents directory not found: {docs_dir}")
            return
            
        files = [f for f in os.listdir(docs_dir) if not f.startswith('.') and os.path.isfile(os.path.join(docs_dir, f))]
        print(f"📄 Found {len(files)} files to ingest:")
        for f in files:
            size = os.path.getsize(os.path.join(docs_dir, f))
            print(f"   - {f} ({size:,} bytes)")
        
        if not files:
            print("❌ No files found to ingest")
            return
            
        print("\n🚀 Starting ingestion process...")
        start_time = time.time()
        
        # Ingest each file
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(docs_dir, filename)
            print(f"\n📥 [{i}/{len(files)}] Ingesting: {filename}")
            
            try:
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                    
                # Process the file using the correct method
                result = ingestor.process_uploaded_file(file_content, filename)
                chunks, summary, metadata = result
                
                print(f"   ✅ Ingested: {len(chunks)} chunks")
                print(f"   📝 Summary: {summary[:100]}...")
                print(f"   📊 Metadata: {metadata}")
                
            except Exception as e:
                print(f"   ❌ Error ingesting {filename}: {e}")
                import traceback
                traceback.print_exc()
        
        end_time = time.time()
        print(f"\n⏱️ Total ingestion time: {end_time - start_time:.2f} seconds")
        
        # Verify the results
        print("\n🔍 Verifying ingestion results...")
        vs = FAISSVectorStore()
        
        if hasattr(vs, 'index') and vs.index:
            print(f"✅ FAISS index created with {vs.index.ntotal} vectors")
        else:
            print("❌ No FAISS index found after ingestion")
            
        # Check metadata
        metadata_path = "data/embeddings/metadata.json"
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            chunks = len(metadata.get('chunks', []))
            source_docs = len(metadata.get('source_documents', []))
            print(f"✅ Metadata file created with {chunks} chunks from {source_docs} documents")
        else:
            print("❌ No metadata file found after ingestion")
            
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    re_ingest_documents()