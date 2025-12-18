"""
System Configuration Display Component - Shows model and API service information.
"""

import streamlit as st
import requests
import os
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv


def get_system_config() -> Dict[str, str]:
    """
    Fetch system configuration from the API.
    
    Returns:
        Dictionary with system configuration info
    """
    api_url = os.getenv("API_URL", "http://localhost:8001")
    
    try:
        response = requests.get(f"{api_url}/config", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to environment variables
    return {
        "llm_model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "chunk_size": os.getenv("CHUNK_SIZE", "1000"),
        "temperature": os.getenv("TEMPERATURE", "0.7"),
    }


def render_system_info() -> None:
    """
    Render system configuration information.
    
    Displays:
    - LLM Model and Provider
    - Embedding Model
    - Core Services
    """
    
    st.markdown("""
    <style>
    .system-info-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: white;
    }
    
    .system-info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        font-size: 12px;
        margin: 4px 0;
    }
    
    .system-info-label {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        min-width: 120px;
    }
    
    .system-info-value {
        color: white;
        font-weight: 500;
        padding: 4px 8px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
        flex-grow: 1;
        text-align: right;
    }
    
    .system-info-badge {
        display: inline-block;
        padding: 2px 8px;
        background: rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    try:
        config = get_system_config()
        
        llm_model = config.get("llm_model", "llama-3.3-70b-versatile")
        llm_provider = config.get("llm_provider", "groq").upper()
        embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")
        chunk_size = config.get("chunk_size", "1000")
        temperature = config.get("temperature", "0.7")
        
        # Build info HTML
        info_html = '<div class="system-info-container">'
        info_html += '<div class="system-info-row">'
        info_html += f'<span class="system-info-label">🤖 LLM Model:</span>'
        info_html += f'<span class="system-info-value">{llm_model} <span class="system-info-badge">{llm_provider}</span></span>'
        info_html += '</div>'
        
        info_html += '<div class="system-info-row">'
        info_html += f'<span class="system-info-label">🔗 Embedding:</span>'
        info_html += f'<span class="system-info-value">{embedding_model}</span>'
        info_html += '</div>'
        
        info_html += '<div class="system-info-row">'
        info_html += f'<span class="system-info-label">⚙️ Configuration:</span>'
        info_html += f'<span class="system-info-value">Chunk: {chunk_size} | Temp: {temperature}</span>'
        info_html += '</div>'
        
        info_html += '</div>'
        
        st.markdown(info_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.warning(f"Could not load system configuration: {str(e)}")


def render_api_services() -> None:
    """
    Render available API services.
    
    Displays:
    - API Endpoints
    - Available Operations
    """
    
    st.markdown("""
    <style>
    .api-services-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 10px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        color: white;
        font-size: 11px;
    }
    
    .services-grid {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .service-badge {
        background: rgba(255, 255, 255, 0.25);
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 500;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)
    
    services_html = '''
    <div class="api-services-container">
        <div style="font-weight: 600; margin-bottom: 6px;">📡 API Services:</div>
        <div class="services-grid">
            <span class="service-badge">📤 Upload</span>
            <span class="service-badge">💬 Chat</span>
            <span class="service-badge">📚 Documents</span>
            <span class="service-badge">❓ Quiz</span>
            <span class="service-badge">🔍 Health</span>
        </div>
    </div>
    '''
    
    st.markdown(services_html, unsafe_allow_html=True)
