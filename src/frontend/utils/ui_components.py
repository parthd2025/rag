"""
UI Components - Professional Component Library
Expert UI/UX patterns for modern data applications
"""

import streamlit as st
import time
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import json


def render_custom_css():
    """Inject professional CSS for enhanced UI."""
    css = """
    <style>
    /* Color Variables */
    :root {
        --primary: #0078D4;
        --secondary: #50E6FF;
        --success: #107C10;
        --warning: #FFB900;
        --error: #E81123;
        --neutral: #F3F2F1;
        --text-primary: #201F1E;
        --text-secondary: #605E5C;
        --border: #D2D0CE;
    }
    
    /* Global Styles */
    * {
        transition: all 0.2s ease-in-out;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, #0063B1 100%);
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0, 120, 212, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 16px rgba(0, 120, 212, 0.3);
        transform: translateY(-2px);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid var(--border) !important;
        border-radius: 6px;
        padding: 10px 12px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        font-size: 14px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.1);
    }
    
    /* Cards */
    .info-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .info-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #F3F2F1 0%, #E8E7E6 100%);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--primary);
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background: #E7F6E7;
        color: var(--success);
    }
    
    .badge-warning {
        background: #FFF8E7;
        color: #BE8B00;
    }
    
    .badge-error {
        background: #FFE7E7;
        color: var(--error);
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        word-wrap: break-word;
        line-height: 1.5;
    }
    
    .chat-message.user {
        background: var(--primary);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 2px;
    }
    
    .chat-message.assistant {
        background: #F3F2F1;
        color: var(--text-primary);
        margin-right: 20%;
        border-bottom-left-radius: 2px;
        border-left: 3px solid var(--secondary);
    }
    
    /* Source Tags */
    .source-tag {
        display: inline-block;
        background: #E0F2FF;
        color: var(--primary);
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 4px;
        margin-top: 4px;
    }
    
    /* Loading State */
    .loading-spinner {
        display: inline-block;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Alerts */
    .alert {
        padding: 12px 16px;
        border-radius: 6px;
        border-left: 4px solid;
        margin-bottom: 16px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .alert-success {
        background: #E7F6E7;
        border-color: var(--success);
        color: var(--success);
    }
    
    .alert-error {
        background: #FFE7E7;
        border-color: var(--error);
        color: var(--error);
    }
    
    .alert-warning {
        background: #FFF8E7;
        border-color: var(--warning);
        color: #BE8B00;
    }
    
    .alert-info {
        background: #E0F2FF;
        border-color: var(--primary);
        color: var(--primary);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .chat-message.user { margin-left: 0%; }
        .chat-message.assistant { margin-right: 0%; }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    """Render professional application header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            """
            # 🤖 RAG Chatbot
            *Intelligent Question-Answering from Your Documents*
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.caption("v1.0.0")


def render_sidebar_header():
    """Render sidebar header with professional styling."""
    st.sidebar.markdown("---")
    st.sidebar.title("⚙️ Settings")
    st.sidebar.markdown("---")


def metric_card(label: str, value: Any, icon: str = "📊"):
    """Render professional metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size: 28px; margin-bottom: 8px;">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def info_box(text: str, icon: str = "ℹ️"):
    """Render professional info box."""
    st.markdown(
        f"""
        <div class="info-card">
            <span style="font-size: 18px; margin-right: 8px;">{icon}</span>
            <span>{text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def success_alert(message: str):
    """Render success alert."""
    st.markdown(
        f'<div class="alert alert-success">✅ {message}</div>',
        unsafe_allow_html=True
    )


def error_alert(message: str):
    """Render error alert."""
    st.markdown(
        f'<div class="alert alert-error">❌ {message}</div>',
        unsafe_allow_html=True
    )


def warning_alert(message: str):
    """Render warning alert."""
    st.markdown(
        f'<div class="alert alert-warning">⚠️ {message}</div>',
        unsafe_allow_html=True
    )


def info_alert(message: str):
    """Render info alert."""
    st.markdown(
        f'<div class="alert alert-info">ℹ️ {message}</div>',
        unsafe_allow_html=True
    )


def render_chat_message(role: str, content: str, sources: Optional[List[Dict]] = None):
    """Render chat message with professional styling."""
    css_class = "user" if role == "user" else "assistant"
    
    st.markdown(
        f'<div class="chat-message {css_class}">{content}</div>',
        unsafe_allow_html=True
    )
    
    if sources and role == "assistant":
        with st.expander("📚 Sources", expanded=False):
            for i, source in enumerate(sources, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Source {i}: {source.get('document', 'Unknown')}**")
                        st.caption(source.get('content', '')[:200] + "...")
                    with col2:
                        score = source.get('relevance_score', 0)
                        st.metric("Match", f"{score:.0%}")


def render_loading_spinner(message: str):
    """Render loading spinner with message."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px;">
            <span class="loading-spinner">⏳</span>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_badge(text: str, badge_type: str = "success"):
    """Render professional badge."""
    st.markdown(
        f'<span class="badge badge-{badge_type}">{text}</span>',
        unsafe_allow_html=True
    )


def render_divider():
    """Render professional divider."""
    st.markdown("---")


def render_empty_state(icon: str, title: str, description: str):
    """Render empty state with helpful message."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 40px 20px; color: #605E5C;">
            <div style="font-size: 48px; margin-bottom: 16px;">{icon}</div>
            <h3 style="color: #201F1E; margin-bottom: 8px;">{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stat_row(stat1: tuple, stat2: tuple, stat3: tuple):
    """Render row of statistics."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card(stat1[0], stat1[1], stat1[2])
    
    with col2:
        metric_card(stat2[0], stat2[1], stat2[2])
    
    with col3:
        metric_card(stat3[0], stat3[1], stat3[2])


def render_source_visualization(sources: List[Dict]):
    """Render professional source visualization."""
    for source in sources:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.caption("📄 Document")
                st.write(source.get('document', 'Unknown'))
            
            with col2:
                st.caption("📝 Content")
                content = source.get('content', '')
                st.write(content[:150] + "..." if len(content) > 150 else content)
            
            with col3:
                score = source.get('relevance_score', 0)
                st.metric("Relevance", f"{score:.0%}")
            
            st.divider()
