"""Component library for Streamlit UI."""

import streamlit as st
from typing import List, Dict, Any


def render_chat_message(role: str, content: str, sources: List[str] = None, confidence: float = None):
    """Render a chat message."""
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.write(content)
            
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.code(source)
            
            if confidence is not None:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"⏱️ Processing time")
                with col2:
                    if confidence >= 0.8:
                        st.success(f"{confidence:.2%} confidence")
                    elif confidence >= 0.6:
                        st.warning(f"{confidence:.2%} confidence")
                    else:
                        st.error(f"{confidence:.2%} confidence")


def render_stats_cards(stats: Dict[str, Any]):
    """Render statistics cards."""
    cols = st.columns(len(stats))
    
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            st.metric(label, value)


def render_document_card(doc: Dict[str, Any]):
    """Render a document card."""
    with st.container(border=True):
        st.subheader(f"📄 {doc['name']}")
        col1, col2, col3 = st.columns(3)
        col1.caption(f"📦 {doc['chunk_count']} chunks")
        col2.caption(f"📅 {doc['upload_date']}")
        col3.caption(f"💾 {doc['size_bytes']} bytes")


def render_suggested_question(question: Dict[str, Any]):
    """Render a suggested question."""
    badge = "📊" if question["type"] == "comparative" else "📝"
    st.write(f"{badge} {question['question']}")
