"""
Tests for document ingestion.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from backend.ingest import DocumentIngestor


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def ingestor():
    """Create document ingestor instance."""
    return DocumentIngestor(chunk_size=100, chunk_overlap=20)


def test_ingestor_initialization(ingestor):
    """Test ingestor initialization."""
    assert ingestor.chunk_size == 100
    assert ingestor.chunk_overlap == 20


def test_chunk_text(ingestor):
    """Test text chunking."""
    text = "This is a test. " * 50  # Create long text
    chunks = ingestor._chunk_text(text)
    
    assert len(chunks) > 0
    assert all(len(chunk) <= ingestor.chunk_size + 50 for chunk in chunks)  # Allow some flexibility


def test_chunk_text_short(ingestor):
    """Test chunking short text."""
    text = "Short text."
    chunks = ingestor._chunk_text(text)
    
    assert len(chunks) == 1
    assert chunks[0] == text.strip()


def test_chunk_text_empty(ingestor):
    """Test chunking empty text."""
    chunks = ingestor._chunk_text("")
    assert chunks == []


def test_invalid_initialization():
    """Test invalid ingestor initialization."""
    with pytest.raises(ValueError):
        DocumentIngestor(chunk_size=0)
    
    with pytest.raises(ValueError):
        DocumentIngestor(chunk_size=100, chunk_overlap=-1)
    
    with pytest.raises(ValueError):
        DocumentIngestor(chunk_size=100, chunk_overlap=100)


def test_extract_text_file(ingestor, temp_dir):
    """Test extracting text from file."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("This is test content.")
    
    text = ingestor._extract_text_file(str(test_file))
    assert "test content" in text


def test_process_uploaded_file(ingestor):
    """Test processing uploaded file."""
    content = b"This is test content for uploaded file."
    chunks, doc_name = ingestor.process_uploaded_file(content, "test.txt")
    
    assert len(chunks) > 0
    assert doc_name is not None

