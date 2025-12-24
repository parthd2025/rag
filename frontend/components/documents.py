"""
Documents - Minimal
"""

import streamlit as st


def render_upload_section(api_client):
    """Upload files."""
    
    f = st.file_uploader("File:", type=["pdf", "docx", "txt", "md", "csv", "xlsx", "pptx", "html"], label_visibility="collapsed")
    if f:
        st.write(f"{f.name} ({f.size / 1024:.1f} KB)")
        if st.button("Upload", use_container_width=True):
            with st.spinner("..."):
                try:
                    r = api_client.upload_document(f.getvalue(), f.name)
                    st.success(f"✅ {r.get('chunks_created', 0)} chunks")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


def render_document_stats(api_client):
    """Stats."""
    try:
        d = api_client.get_documents()
        if d:
            st.metric("Chunks", d.get("total_chunks", 0))
            st.metric("Docs", len(d.get("documents", [])))
            if d.get("documents"):
                st.markdown("**Recent:**")
                for doc in d.get("documents", [])[:3]:
                    st.write(f"- {doc.get('name', '?')} ({doc.get('chunks', 0)})")
    except:
        st.info("No docs")


def render_clear_section(api_client):
    """Delete data."""
    if st.button("Clear All", use_container_width=True):
        if st.checkbox("Confirm"):
            try:
                api_client.clear_data()
                st.success("Cleared!")
                st.rerun()
            except Exception as e:
                st.error(str(e))
