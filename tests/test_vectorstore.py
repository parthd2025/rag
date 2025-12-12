"""
Tests for FAISS vector store.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

from backend.vectorstore import FAISSVectorStore


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def vector_store(temp_dir):
    """Create vector store instance for testing."""
    index_path = temp_dir / "test.index"
    metadata_path = temp_dir / "test.json"
    
    store = FAISSVectorStore(
        embedding_model_name="all-MiniLM-L6-v2",
        index_path=str(index_path),
        metadata_path=str(metadata_path)
    )
    return store


def test_vector_store_initialization(vector_store):
    """Test vector store initialization."""
    assert vector_store is not None
    assert len(vector_store.chunks) == 0
    assert vector_store.index is not None


def test_add_chunks(vector_store):
    """Test adding chunks to vector store."""
    chunks = [
        "This is the first chunk.",
        "This is the second chunk.",
        "This is the third chunk."
    ]
    
    vector_store.add_chunks(chunks, "test_doc")
    
    assert len(vector_store.chunks) == 3
    assert vector_store.index.ntotal == 3


def test_search(vector_store):
    """Test searching in vector store."""
    chunks = [
        "Python is a programming language.",
        "Machine learning uses algorithms.",
        "Natural language processing is a field of AI."
    ]
    
    vector_store.add_chunks(chunks, "test_doc")
    
    results = vector_store.search("programming", top_k=2)
    
    assert len(results) > 0
    assert len(results) <= 2
    assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
    assert all(isinstance(r[1], float) for r in results)  # similarity score


def test_clear(vector_store):
    """Test clearing vector store."""
    chunks = ["Test chunk 1", "Test chunk 2"]
    vector_store.add_chunks(chunks, "test_doc")
    
    assert len(vector_store.chunks) == 2
    
    vector_store.clear()
    
    assert len(vector_store.chunks) == 0
    assert vector_store.index.ntotal == 0


def test_get_statistics(vector_store):
    """Test getting statistics."""
    stats = vector_store.get_statistics()
    
    assert "total_chunks" in stats
    assert "index_size" in stats
    assert "embedding_dimension" in stats
    assert "model" in stats


def test_empty_search(vector_store):
    """Test searching empty vector store."""
    results = vector_store.search("test query")
    assert results == []


def test_persistence(vector_store, temp_dir):
    """Test that vector store persists data."""
    chunks = ["Persistent chunk 1", "Persistent chunk 2"]
    vector_store.add_chunks(chunks, "test_doc")
    
    # Create new instance to test loading
    new_store = FAISSVectorStore(
        embedding_model_name="all-MiniLM-L6-v2",
        index_path=str(temp_dir / "test.index"),
        metadata_path=str(temp_dir / "test.json")
    )
    
    assert len(new_store.chunks) == 2
    assert new_store.index.ntotal == 2

