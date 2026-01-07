"""
Migration script to convert existing TF-IDF embeddings to neural embeddings.
This script re-indexes all documents using SentenceTransformer models.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.vectorstore import FAISSVectorStore
from backend.config import settings
from backend.logger_config import logger


def backup_existing_index():
    """Create backup of existing index files."""
    index_path = Path("data/embeddings/faiss.index")
    metadata_path = Path("data/embeddings/metadata.json")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backups = []
    
    if index_path.exists():
        backup_index = index_path.parent / f"faiss.index.backup_{timestamp}"
        index_path.rename(backup_index)
        backups.append(backup_index)
        print(f"✓ Backed up index: {backup_index}")
    
    if metadata_path.exists():
        backup_metadata = metadata_path.parent / f"metadata.json.backup_{timestamp}"
        metadata_path.rename(backup_metadata)
        backups.append(backup_metadata)
        print(f"✓ Backed up metadata: {backup_metadata}")
    
    return backups


def load_old_data(backup_metadata_path):
    """Load chunks and metadata from backup."""
    try:
        with open(backup_metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks = data.get('chunks', [])
            metadata = data.get('metadata', [])
            return chunks, metadata
    except Exception as e:
        print(f"✗ Error loading backup data: {e}")
        return [], []


def migrate():
    """Main migration function."""
    print("=" * 80)
    print("Migration: TF-IDF to Neural Embeddings (SentenceTransformer)")
    print("=" * 80)
    print()
    
    # Check if using neural mode
    embedding_mode = getattr(settings, 'EMBEDDING_MODE', 'neural')
    if embedding_mode != 'neural':
        print(f"   Warning: EMBEDDING_MODE is '{embedding_mode}', not 'neural'")
        print("   Set EMBEDDING_MODE=neural in your environment or config")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
    
    # Step 1: Backup existing index
    print("\n   Step 1: Backing up existing index files...")
    backups = backup_existing_index()
    
    if not backups:
        print("   No existing index found. This appears to be a fresh installation.")
        print("   You can directly use neural embeddings by uploading documents.")
        return
    
    # Find backup metadata file
    backup_metadata = next((b for b in backups if 'metadata' in str(b)), None)
    
    if not backup_metadata:
        print("   Error: Could not find metadata backup")
        return
    
    # Step 2: Load old data
    print(f"\n   Step 2: Loading existing chunks from backup...")
    old_chunks, old_metadata = load_old_data(backup_metadata)
    
    if not old_chunks:
        print("   No chunks found in backup. Nothing to migrate.")
        return
    
    print(f"   Loaded {len(old_chunks)} chunks from backup")
    
    # Step 3: Group chunks by document
    print(f"\n   Step 3: Organizing chunks by document...")
    doc_chunks = defaultdict(list)
    for chunk, meta in zip(old_chunks, old_metadata):
        doc_name = meta.get('source_doc', 'unknown')
        doc_chunks[doc_name].append(chunk)
    
    print(f"   Found {len(doc_chunks)} unique documents")
    for doc_name, chunks in doc_chunks.items():
        print(f"   - {doc_name}: {len(chunks)} chunks")
    
    # Step 4: Create new vectorstore with neural embeddings
    print(f"\n   Step 4: Initializing neural embedding model...")
    try:
        # Force neural mode
        os.environ['EMBEDDING_MODE'] = 'neural'
        vectorstore = FAISSVectorStore()
        print(f"   Neural embeddings initialized (dim={vectorstore.embedding_dim})")
    except Exception as e:
        print(f"   Error initializing neural embeddings: {e}")
        print("\n   Make sure sentence-transformers is installed:")
        print("   pip install sentence-transformers")
        return
    
    # Step 5: Re-index all documents
    print(f"\n   Step 5: Re-indexing {len(doc_chunks)} documents with neural embeddings...")
    print("-" * 80)
    
    success_count = 0
    fail_count = 0
    
    for idx, (doc_name, chunks) in enumerate(doc_chunks.items(), 1):
        try:
            print(f"\n[{idx}/{len(doc_chunks)}] Processing: {doc_name}")
            print(f"   Chunks: {len(chunks)}")
            
            # Re-index with neural embeddings
            vectorstore.add_chunks(chunks, doc_name)
            
            print(f"      Successfully re-indexed with neural embeddings")
            success_count += 1
            
        except Exception as e:
            print(f"      Failed to re-index: {e}")
            fail_count += 1
    
    print("\n" + "-" * 80)
    print(f"\n   Migration Complete!")
    print(f"   Success: {success_count} documents")
    print(f"   Failed:  {fail_count} documents")
    print(f"   Total chunks: {vectorstore.index.ntotal if vectorstore.index else 0}")
    
    # Step 6: Verify
    print(f"\n   Step 6: Verifying new index...")
    stats = vectorstore.get_statistics()
    unique_docs = len(set(m.get('source_doc') for m in vectorstore.metadata))
    print(f"   Total chunks: {stats.get('total_chunks', len(vectorstore.chunks))}")
    print(f"   Total documents: {unique_docs}")
    print(f"   Embedding dimension: {stats.get('embedding_dim', vectorstore.embedding_dim)}")
    print(f"   Embedding mode: {vectorstore.embedding_mode}")
    
    print(f"\n   Backups saved:")
    for backup in backups:
        print(f"   {backup}")
    
    print("\n   You can now use the improved neural embeddings!")
    print("  To switch back to TF-IDF, set EMBEDDING_MODE=tfidf and restore backups.")


def restore_backup():
    """Restore from backup files."""
    print("\n   Restoring from backup...")
    
    # Find latest backup
    backup_dir = Path("data/embeddings")
    index_backups = sorted(backup_dir.glob("faiss.index.backup_*"), reverse=True)
    metadata_backups = sorted(backup_dir.glob("metadata.json.backup_*"), reverse=True)
    
    if not index_backups or not metadata_backups:
        print("   No backups found")
        return
    
    # Remove current files if they exist
    current_index = backup_dir / "faiss.index"
    current_metadata = backup_dir / "metadata.json"
    
    if current_index.exists():
        current_index.unlink()
    if current_metadata.exists():
        current_metadata.unlink()
    
    # Restore backups
    index_backups[0].rename(current_index)
    metadata_backups[0].rename(current_metadata)
    
    print(f"   Restored from backup:")
    print(f"   {index_backups[0].name}")
    print(f"   {metadata_backups[0].name}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate vector store to neural embeddings")
    parser.add_argument('--restore', action='store_true', help='Restore from backup instead of migrating')
    
    args = parser.parse_args()
    
    if args.restore:
        restore_backup()
    else:
        try:
            migrate()
        except KeyboardInterrupt:
            print("\n\n   Migration interrupted by user")
            print("   Backups are preserved in data/embeddings/")
        except Exception as e:
            print(f"\n   Migration failed: {e}")
            print("   Backups are preserved in data/embeddings/")
            import traceback
            traceback.print_exc()
