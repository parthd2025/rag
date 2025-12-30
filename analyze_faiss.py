import json
import sys
import os

# Add backend to path
sys.path.append('backend')
from backend.vectorstore import FAISSVectorStore

def check_faiss_db():
    print("=== FAISS Database Analysis ===\n")
    
    # Initialize FAISS vector store
    try:
        vs = FAISSVectorStore()
        # vs._load_or_create_index()  # This is called automatically in init
        print("✅ FAISS vector store loaded successfully")
        
        # Check metadata file
        metadata_file = vs.metadata_path
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            print(f"📊 Vector Store Statistics:")
            print(f"   - Total chunks: {len(metadata.get('chunks', []))}")
            print(f"   - Index dimension: {vs.embedding_dim}")
            print(f"   - Total vectors in FAISS index: {vs.index.ntotal if hasattr(vs, 'index') and vs.index else 0}")
            
            # Check source documents
            source_docs = metadata.get('source_documents', [])
            print(f"   - Source documents registered: {len(source_docs)}")
            
            if source_docs:
                print("📄 Source Documents:")
                for i, doc in enumerate(source_docs, 1):
                    print(f"   {i}. {doc}")
            else:
                print("⚠️  No source documents found in metadata")
                
            # Analyze chunks for content patterns
            chunks = metadata.get('chunks', [])
            chunk_metadata = metadata.get('chunk_metadata', [])
            
            print(f"\n🔍 Content Analysis:")
            
            # Search for loan/policy content
            loan_chunks = 0
            mindbowser_chunks = 0
            employee_chunks = 0
            
            sample_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_str = str(chunk).lower()
                if 'loan' in chunk_str or 'policy' in chunk_str:
                    loan_chunks += 1
                    if len(sample_chunks) < 3:
                        sample_chunks.append((i, str(chunk)[:200]))
                        
                if 'mindbowser' in chunk_str:
                    mindbowser_chunks += 1
                    
                if 'employee' in chunk_str:
                    employee_chunks += 1
                    
            print(f"   - Chunks mentioning 'loan' or 'policy': {loan_chunks}")
            print(f"   - Chunks mentioning 'mindbowser': {mindbowser_chunks}")
            print(f"   - Chunks mentioning 'employee': {employee_chunks}")
            
            if sample_chunks:
                print("\n📝 Sample chunks with loan/policy content:")
                for idx, content in sample_chunks:
                    print(f"   Chunk {idx}: {content}...")
                    print()
            
            # Check what documents are actually in data/documents
            docs_dir = "backend/data/documents"
            if os.path.exists(docs_dir):
                files = [f for f in os.listdir(docs_dir) if not f.startswith('.')]
                print(f"💾 Files in documents directory ({docs_dir}):")
                for f in files:
                    file_path = os.path.join(docs_dir, f)
                    size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                    print(f"   - {f} ({size:,} bytes)")
            else:
                print(f"❌ Documents directory not found: {docs_dir}")
                
        else:
            print("❌ No metadata file found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_faiss_db()