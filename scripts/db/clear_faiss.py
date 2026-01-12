import os
import json
import sys
sys.path.append('backend')

def clear_faiss_index():
    """Clear the existing FAISS index and metadata."""
    print("=== Clearing FAISS Index ===\n")
    
    # Paths to FAISS files
    index_path = "data/embeddings/faiss.index"
    metadata_path = "data/embeddings/metadata.json"
    
    files_to_clear = [index_path, metadata_path]
    
    for file_path in files_to_clear:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")
        else:
            print(f"ℹ️  File not found: {file_path}")
    
    # Also check if there are any backup files
    embeddings_dir = "data/embeddings"
    if os.path.exists(embeddings_dir):
        files = os.listdir(embeddings_dir)
        remaining_files = [f for f in files if not f.startswith('.')]
        if remaining_files:
            print(f"📁 Remaining files in embeddings directory: {remaining_files}")
        else:
            print("📁 Embeddings directory is now clean")
    
    print("\n✅ FAISS index cleared successfully!")

if __name__ == "__main__":
    clear_faiss_index()