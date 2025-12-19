"""
Chat Component - Professional Chat Interface
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


def render_chat_interface(api_client, config):
    """Render professional chat interface."""
    st.markdown("### 💬 Chat with Your Documents")
    
    # Chat container
    chat_container = st.container()
    
    # Input area
    input_container = st.container()
    
    with input_container:
        col1, col2 = st.columns([5, 1])
        
        with col1:
            question = st.text_input(
                "Ask a question:",
                placeholder="What is this document about?",
                key="chat_input",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_btn = st.button("Send", use_container_width=True)
    
    # Process query
    if submit_btn and question.strip():
        with chat_container:
            # Add user message
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            
            st.session_state.chat_messages.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get response
            try:
                with st.spinner("🔍 Searching documents..."):
                    response = api_client.query(
                        question,
                        top_k=config.get("TOP_K", 5)
                    )
                
                if response:
                    answer = response.get("answer", "")
                    sources = response.get("sources", [])
                    
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    st.success("✅ Response generated successfully!")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display chat history
    if "chat_messages" in st.session_state:
        for message in st.session_state.chat_messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.write("")
                st.markdown(
                    f'<div class="chat-message user">{content}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant">{content}</div>',
                    unsafe_allow_html=True
                )
                
                sources = message.get("sources", [])
                if sources:
                    with st.expander("📚 View Sources", expanded=False):
                        for source in sources:
                            st.caption(f"📄 {source.get('document', 'Unknown')}")
                            st.markdown(source.get("content", "")[:300] + "...")
                            st.metric("Relevance Score", f"{source.get('relevance_score', 0):.1%}")
                            st.divider()


def render_quick_actions(api_client):
    """Render quick action buttons."""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Clear Chat", use_container_width=True):
            if "chat_messages" in st.session_state:
                st.session_state.chat_messages = []
            st.rerun()
    
    with col2:
        if st.button("📤 Export Chat", use_container_width=True):
            if "chat_messages" in st.session_state:
                chat_json = json.dumps(st.session_state.chat_messages, indent=2)
                st.download_button(
                    label="Download",
                    data=chat_json,
                    file_name="chat_history.json",
                    mime="application/json"
                )
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col4:
        if st.button("❓ Help", use_container_width=True):
            st.info(
                """
                **Chat Tips:**
                - Be specific in your questions
                - Use keywords from documents
                - Try rephrasing if no good results
                - Check sources for context
                """
            )
