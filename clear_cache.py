import os
import shutil
import sys
sys.path.append('backend')

def clear_all_caches():
    """Clear all caches including embeddings, logs, and temporary files."""
    print("=== Clearing All Caches ===\n")
    
    cache_locations = [
        # FAISS embeddings
        "data/embeddings/",
        
        # Logs
        "logs/",
        
        # Python cache
        "__pycache__/",
        "backend/__pycache__/",
        "frontend/__pycache__/",
        "backend/api/__pycache__/",
        "backend/services/__pycache__/",
        "backend/utils/__pycache__/",
        "backend/api/models/__pycache__/",
        "frontend/components/__pycache__/",
        "frontend/utils/__pycache__/",
        "tests/__pycache__/",
        "scripts/__pycache__/",
        
        # Temporary files
        "data/documents/.gitkeep",  # Keep only gitkeep
    ]
    
    files_to_keep = [
        "data/embeddings/.gitkeep",
        "logs/.gitkeep", 
        "backend/data/documents/.gitkeep",
    ]
    
    for cache_path in cache_locations:
        if os.path.exists(cache_path):
            try:
                if os.path.isdir(cache_path):
                    # Clear directory contents but keep .gitkeep files
                    for item in os.listdir(cache_path):
                        item_path = os.path.join(cache_path, item)
                        if not item.endswith('.gitkeep'):
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                                print(f"✅ Removed directory: {item_path}")
                            else:
                                os.remove(item_path)
                                print(f"✅ Removed file: {item_path}")
                        else:
                            print(f"⚪ Kept: {item_path}")
                else:
                    os.remove(cache_path)
                    print(f"✅ Removed file: {cache_path}")
            except Exception as e:
                print(f"❌ Error clearing {cache_path}: {e}")
        else:
            print(f"ℹ️  Not found: {cache_path}")
    
    # Also clear any .pyc files recursively
    pyc_count = 0
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    pyc_path = os.path.join(root, file)
                    os.remove(pyc_path)
                    pyc_count += 1
                except Exception as e:
                    print(f"❌ Error removing {file}: {e}")
    
    if pyc_count > 0:
        print(f"✅ Removed {pyc_count} .pyc files")
    
    print("\n🧹 Cache clearing complete!")

if __name__ == "__main__":
    clear_all_caches()