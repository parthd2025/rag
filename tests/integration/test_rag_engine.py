"""
Tests for RAG engine.
"""

import pytest
from unittest.mock import Mock, MagicMock

from backend.rag_engine import RAGEngine


@pytest.fixture
def mock_vector_store():
    """Create mock vector store."""
    store = Mock()
    store.chunks = ["chunk1", "chunk2", "chunk3"]
    store.search = Mock(return_value=[("chunk1", 0.9), ("chunk2", 0.8)])
    return store


@pytest.fixture
def mock_llm_engine():
    """Create mock LLM engine."""
    engine = Mock()
    engine.is_ready = Mock(return_value=True)
    engine.generate = Mock(return_value="Test answer")
    return engine


@pytest.fixture
def rag_engine(mock_vector_store, mock_llm_engine):
    """Create RAG engine instance."""
    return RAGEngine(
        vector_store=mock_vector_store,
        llm_engine=mock_llm_engine,
        top_k=2,
        temperature=0.7
    )


def test_rag_engine_initialization(rag_engine):
    """Test RAG engine initialization."""
    assert rag_engine.top_k == 2
    assert rag_engine.temperature == 0.7


def test_answer_query(rag_engine, mock_vector_store, mock_llm_engine):
    """Test answering query."""
    answer = rag_engine.answer_query("test question")
    
    assert answer is not None
    assert isinstance(answer, str)
    mock_vector_store.search.assert_called_once()
    mock_llm_engine.generate.assert_called_once()


def test_answer_query_with_context(rag_engine, mock_vector_store, mock_llm_engine):
    """Test answering query with context."""
    result = rag_engine.answer_query_with_context("test question")
    
    assert "answer" in result
    assert "context" in result
    assert "sources" in result
    assert len(result["sources"]) > 0


def test_answer_query_no_documents(rag_engine, mock_vector_store):
    """Test answering query with no documents."""
    mock_vector_store.search.return_value = []
    
    answer = rag_engine.answer_query("test question")
    assert "No documents" in answer or "documents" in answer.lower()


def test_set_top_k(rag_engine):
    """Test setting top_k."""
    rag_engine.set_top_k(5)
    assert rag_engine.top_k == 5


def test_set_temperature(rag_engine):
    """Test setting temperature."""
    rag_engine.set_temperature(0.5)
    assert rag_engine.temperature == 0.5


def test_invalid_initialization():
    """Test invalid RAG engine initialization."""
    mock_store = Mock()
    mock_llm = Mock()
    
    with pytest.raises(ValueError):
        RAGEngine(mock_store, mock_llm, top_k=0)
    
    with pytest.raises(ValueError):
        RAGEngine(mock_store, mock_llm, top_k=5, temperature=3.0)


def test_get_statistics(rag_engine):
    """Test getting statistics."""
    stats = rag_engine.get_statistics()
    
    assert "llm_ready" in stats
    assert "top_k" in stats
    assert "temperature" in stats

