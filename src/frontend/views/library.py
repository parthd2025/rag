"""
Library Page - Document list and statistics
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any

from components.state import get_state, get_api_client


def render_library_page():
    """Render the document library page."""
    
    api = get_api_client()
    if not api:
        st.error("API client not available. Please check connection.")
        return
    
    total_docs = get_state("total_docs", 0)
    total_chunks = get_state("total_chunks", 0)
    
    if total_docs == 0:
        _render_empty_library()
        return
    
    # Statistics overview
    _render_statistics_overview(total_docs, total_chunks)
    
    st.divider()
    
    # Document list and management
    col1, col2 = st.columns([2, 1])
    
    with col1:
        _render_document_list(api)
    
    with col2:
        _render_quick_actions(api)


def _render_empty_library():
    """Render empty library state with guidance."""
    
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                border-radius: 12px; margin: 1rem 0;">
        <h2 style="color: #fff; margin-bottom: 1rem;">📭 Your Library is Empty</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Upload documents to start building your knowledge base.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Getting started tips
    st.markdown("### 💡 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📚 Supported Formats**
        - PDF files
        - Word documents (.docx)
        - Text & Markdown files
        - Excel & CSV files
        - PowerPoint presentations
        - HTML files
        """)
    
    with col2:
        st.markdown("""
        **🎯 Best Practices**
        - Upload related documents
        - Ensure text-readable files
        - Start with 2-5 documents
        - Organize by topic
        """)
    
    with col3:
        st.markdown("""
        **🚀 What You Can Do**
        - Ask questions about content
        - Compare across documents
        - Get summaries & insights
        - Generate follow-ups
        """)
    
    st.info("👉 Navigate to **Upload** page to add your first documents!")


def _render_statistics_overview(total_docs: int, total_chunks: int):
    """Render document statistics overview."""
    
    st.markdown("### 📊 Library Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📄 Total Documents",
            total_docs,
            help="Number of uploaded documents"
        )
    
    with col2:
        st.metric(
            "🧩 Total Chunks",
            f"{total_chunks:,}",
            help="Number of searchable text chunks"
        )
    
    with col3:
        avg_chunks = total_chunks / total_docs if total_docs > 0 else 0
        st.metric(
            "📈 Avg Chunks/Doc",
            f"{avg_chunks:.1f}",
            help="Average chunks per document"
        )
    
    with col4:
        # Estimate storage (rough calculation)
        est_storage_kb = total_chunks * 2  # ~2KB per chunk average
        if est_storage_kb > 1024:
            st.metric("💾 Est. Storage", f"{est_storage_kb/1024:.1f} MB")
        else:
            st.metric("💾 Est. Storage", f"{est_storage_kb} KB")


def _render_document_list(api):
    """Render the document list with details."""
    
    st.markdown("### 📋 Document List")
    
    try:
        docs_data = api.get_documents()
        documents = docs_data.get("documents", []) if docs_data else []
        
        if not documents:
            st.info("No documents found.")
            return
        
        # Filter active documents
        active_docs = [doc for doc in documents if doc.get('chunks', doc.get('chunk_count', 0)) > 0]
        
        # Document table header
        header_cols = st.columns([4, 2, 2, 2])
        with header_cols[0]:
            st.markdown("**Document Name**")
        with header_cols[1]:
            st.markdown("**Chunks**")
        with header_cols[2]:
            st.markdown("**Upload Date**")
        with header_cols[3]:
            st.markdown("**Actions**")
        
        st.divider()
        
        # Document rows
        for i, doc in enumerate(active_docs):
            doc_name = doc.get('name', 'Unknown')
            doc_chunks = doc.get('chunks', doc.get('chunk_count', 0))
            upload_date = doc.get('upload_date', '')
            
            # Format date
            date_str = _format_date(upload_date)
            
            # File icon
            icon = _get_file_icon(doc_name)
            
            row_cols = st.columns([4, 2, 2, 2])
            
            with row_cols[0]:
                st.markdown(f"{icon} **{doc_name}**")
            
            with row_cols[1]:
                st.write(f"{doc_chunks:,} chunks")
            
            with row_cols[2]:
                st.write(date_str if date_str else "—")
            
            with row_cols[3]:
                # Delete button with confirmation
                if st.button("🗑️", key=f"del_{i}", help=f"Delete {doc_name}"):
                    _handle_document_deletion(api, doc_name, i)
        
        # Show count
        if len(active_docs) > 0:
            st.caption(f"Showing {len(active_docs)} document(s)")
            
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")


def _render_quick_actions(api):
    """Render quick actions panel."""
    
    st.markdown("### ⚡ Quick Actions")
    
    # Refresh documents
    if st.button("🔄 Refresh List", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # Danger zone
    st.markdown("### ⚠️ Danger Zone")
    
    st.warning("These actions cannot be undone!")
    
    # Clear all with confirmation
    confirm_clear = st.checkbox("I understand this will delete all documents")
    
    if st.button(
        "🗑️ Clear All Documents",
        use_container_width=True,
        type="secondary",
        disabled=not confirm_clear
    ):
        try:
            with st.spinner("Clearing all documents..."):
                api.clear_data()
                st.success("✅ All documents cleared!")
                import time
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")


def _handle_document_deletion(api, doc_name: str, index: int):
    """Handle document deletion with confirmation."""
    
    confirm_key = f"confirm_del_{index}"
    
    if get_state(confirm_key, False):
        try:
            with st.spinner(f"Deleting {doc_name}..."):
                success = api.delete_document(doc_name)
                if success:
                    st.success(f"✅ Deleted '{doc_name}'")
                    # Clear confirmation state
                    st.session_state[confirm_key] = False
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed to delete '{doc_name}'")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.session_state[confirm_key] = True
        st.warning(f"Click again to confirm deletion of '{doc_name}'")
        st.rerun()


def _get_file_icon(filename: str) -> str:
    """Get emoji icon based on file extension."""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    icons = {
        'pdf': '📄', 'docx': '📝', 'doc': '📝', 'txt': '📄', 'md': '📑',
        'csv': '📊', 'xlsx': '📈', 'xls': '📈', 'pptx': '📺', 'ppt': '📺',
        'html': '🌐', 'htm': '🌐'
    }
    return icons.get(ext, '📄')


def _format_date(date_str: str) -> str:
    """Format date string for display."""
    if not date_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        try:
            return date_str[:16]  # Just take first 16 chars
        except:
            return ""
