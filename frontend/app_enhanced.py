"""Main Streamlit app configuration and layout."""

import streamlit as st
from utils.api_client import get_api_client

# Page configuration
st.set_page_config(
    page_title="Document Helper",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 50px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_client" not in st.session_state:
    st.session_state.api_client = get_api_client()

# Header
st.title("📚 Document Helper")
st.markdown("*Your intelligent document companion - powered by AI*")

# Main layout
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_health = st.status("🔌 API Connection")
    try:
        health = st.session_state.api_client.get_health()
        api_health.update(label="🔌 API: Ready ✅", state="complete")
    except:
        api_health.update(label="🔌 API: Offline ❌", state="error")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Top-K", 5)
    with col2:
        st.metric("🌡️ Temperature", 0.7)
    
    st.divider()
    
    if st.button("🔄 Refresh Settings", use_container_width=True):
        st.rerun()
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.success("Conversation cleared!")

# Tabs for main content
tabs = st.tabs(["💬 Chat", "📚 Documents", "📊 Analytics", "⚙️ Settings"])

with tabs[0]:
    st.subheader("Chat Interface")
    st.write("Ask questions about your documents")
    
    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.code(source)
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        try:
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.api_client.chat(prompt)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response.get("sources", [])
            })
            
            with st.chat_message("assistant"):
                st.write(response["answer"])
                if response.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in response["sources"]:
                            st.code(source)
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tabs[1]:
    st.subheader("Document Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "txt", "docx", "md"],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("Upload"):
            with st.spinner("Uploading..."):
                try:
                    result = st.session_state.api_client.upload_documents(uploaded_files)
                    st.success(f"Uploaded {result.get('documents_processed', 0)} documents!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("### 📚 Loaded Documents")
        try:
            docs = st.session_state.api_client.get_documents()
            
            if docs["documents"]:
                for doc in docs["documents"]:
                    with st.container(border=True):
                        st.write(f"**{doc['name']}**")
                        col1, col2, col3 = st.columns(3)
                        col1.caption(f"📦 {doc['chunk_count']} chunks")
                        col2.caption(f"💾 {doc['size_bytes']} bytes")
            else:
                st.info("No documents uploaded yet")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tabs[2]:
    st.subheader("Analytics")
    
    try:
        docs = st.session_state.api_client.get_documents()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📄 Documents", docs["total_count"])
        col2.metric("📦 Total Chunks", docs["total_chunks"])
        col3.metric("💬 Messages", len(st.session_state.messages))
        
        st.divider()
        st.write("**Document Breakdown:**")
        
        if docs["documents"]:
            data = {doc["name"]: doc["chunk_count"] for doc in docs["documents"]}
            st.bar_chart(data)
    except Exception as e:
        st.error(f"Error: {str(e)}")

with tabs[3]:
    st.subheader("Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Query Settings")
        top_k = st.slider("Top-K Results", 1, 20, 5)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    with col2:
        st.markdown("### Chunking Settings")
        chunk_size = st.number_input("Chunk Size", 100, 2000, 1000)
        chunk_overlap = st.number_input("Chunk Overlap", 0, 500, 200)
    
    st.divider()
    
    if st.button("💾 Save Settings"):
        try:
            settings = {
                "top_k": top_k,
                "temperature": temperature,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            }
            st.session_state.api_client.update_settings(settings)
            st.success("Settings saved!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.button("🔄 Reset to Defaults"):
        try:
            st.session_state.api_client.reset_settings()
            st.success("Settings reset!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
