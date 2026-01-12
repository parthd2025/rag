"""
Sidebar Navigation Component
Left navigation for page routing
"""

import streamlit as st
from components.state import navigate_to, get_current_page, get_state


def render_sidebar():
    """Render the left sidebar navigation."""
    
    with st.sidebar:
        # App branding
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
            <h1 style="margin: 0; font-size: 1.5rem;">🤖 RAG Chatbot</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.7;">
                Intelligent Document Q&A
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation buttons
        current_page = get_current_page()
        
        # Navigation items with icons
        nav_items = [
            ("chat", "💬", "Chat", "Ask questions about your documents"),
            ("library", "📚", "Library", "View uploaded documents & stats"),
            ("upload", "📤", "Upload", "Upload new documents"),
            ("settings", "⚙️", "Settings", "Configure system settings"),
        ]
        
        st.markdown("### Navigation")
        
        for page_id, icon, label, tooltip in nav_items:
            is_active = current_page == page_id
            
            # Style active button differently
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                f"{icon} {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type=button_type,
                help=tooltip
            ):
                navigate_to(page_id)
                st.rerun()
        
        st.divider()
        
        # Quick stats section
        render_quick_stats()
        
        st.divider()
        
        # Connection status
        render_connection_status()


def render_quick_stats():
    """Render quick statistics in sidebar."""
    
    st.markdown("### 📊 Quick Stats")
    
    total_docs = get_state("total_docs", 0)
    total_chunks = get_state("total_chunks", 0)
    chat_count = len([m for m in get_state("chat_messages", []) if m.get("role") == "user"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Docs", total_docs)
    
    with col2:
        st.metric("Chunks", total_chunks)
    
    if chat_count > 0:
        st.caption(f"💬 {chat_count} question{'s' if chat_count != 1 else ''} asked")


def render_connection_status():
    """Render API connection status."""
    
    is_connected = get_state("api_connected", False)
    
    if is_connected:
        st.success("🟢 API Connected", icon="✅")
    else:
        st.error("🔴 API Disconnected", icon="❌")
        st.caption("Start backend to connect")
