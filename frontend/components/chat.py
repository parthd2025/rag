"""
Chat Component - Minimal
"""

import streamlit as st


def render_chat_interface(api_client, config):
    """Simple chat."""
    
    if st.session_state.chat_messages:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")
                if msg.get("sources"):
                    with st.expander("📖 Sources"):
                        for src in msg["sources"]:
                            st.write(f"📄 {src.get('document', 'N/A')}")
    else:
        st.info("💭 Ask a question...")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        q = st.text_input("Q:", placeholder="Ask...", label_visibility="collapsed")
    with col2:
        send = st.button("Send", use_container_width=True)
    
    if send and q.strip():
        with st.spinner("Searching..."):
            try:
                st.session_state.chat_messages.append({"role": "user", "content": q})
                resp = api_client.query(q, top_k=config.get("TOP_K", 5))
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": resp.get("answer", ""),
                    "sources": resp.get("sources", [])
                })
                st.rerun()
            except Exception as e:
                st.error(str(e))
