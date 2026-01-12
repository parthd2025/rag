"""
Navbar Component
Top navigation bar with app title and status
"""

import streamlit as st
from components.state import get_state, get_current_page


def render_navbar():
    """Render the top navigation bar."""
    
    # Get current page for breadcrumb
    current_page = get_current_page()
    page_titles = {
        "chat": "💬 Chat",
        "library": "📚 Document Library",
        "upload": "📤 Upload Documents",
        "settings": "⚙️ Settings"
    }
    
    page_title = page_titles.get(current_page, "RAG Chatbot")
    
    # Header row
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        st.markdown(f"## {page_title}")
    
    with col2:
        # Document status
        total_docs = get_state("total_docs", 0)
        total_chunks = get_state("total_chunks", 0)
        
        if total_chunks > 0:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; background: rgba(0, 180, 120, 0.1); border-radius: 8px;">
                <span style="font-size: 0.9rem;">📄 {total_docs} docs • 🧩 {total_chunks:,} chunks</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 0.5rem; background: rgba(255, 180, 0, 0.1); border-radius: 8px;">
                <span style="font-size: 0.9rem;">📭 No documents uploaded</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Connection status badge
        is_connected = get_state("api_connected", False)
        
        if is_connected:
            st.markdown("""
            <div style="text-align: right; padding: 0.5rem;">
                <span style="background: rgba(0, 180, 120, 0.2); color: #00b478; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem;">
                    ● Connected
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: right; padding: 0.5rem;">
                <span style="background: rgba(220, 50, 50, 0.2); color: #dc3232; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem;">
                    ● Disconnected
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()


def render_page_header(title: str, subtitle: str = None, icon: str = None):
    """Render a consistent page header."""
    
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")
    
    if subtitle:
        st.caption(subtitle)


def render_breadcrumb():
    """Render breadcrumb navigation."""
    
    current_page = get_current_page()
    page_names = {
        "chat": "Chat",
        "library": "Library",
        "upload": "Upload",
        "settings": "Settings"
    }
    
    breadcrumb = f"🏠 Home › {page_names.get(current_page, 'Unknown')}"
    st.caption(breadcrumb)
