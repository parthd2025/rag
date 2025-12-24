"""
System Info Component - Simplified
"""

import streamlit as st


def render_system_dashboard(api_client):
    """System status."""
    try:
        import requests
        resp = requests.get("http://localhost:8001/health", timeout=5)
        st.metric("API", "✅ Online" if resp.status_code == 200 else "⚠️ Offline")
    except:
        st.metric("API", "❌ Offline")
    


def render_help_section():
    """Help."""
    with st.expander("❓ Help"):
        st.markdown("**Upload** → **Ask** → **Learn**")

