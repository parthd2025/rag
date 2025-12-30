"""
Settings Dashboard Component - Real-time Configuration
"""

import streamlit as st
from typing import Dict, Any


def render_settings_dashboard(api_client):
    """Render interactive settings dashboard for real-time configuration."""
    
    st.subheader("⚙️ System Settings")
    
    # Load current configuration
    try:
        current_config = api_client.get_config()
        if not current_config:
            st.error("❌ Could not load current configuration")
            return
        
        # Organize settings into tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "🤖 LLM", "📊 Processing", "🎯 Advanced"])
        
        with tab1:
            render_search_settings(api_client, current_config)
        
        with tab2:
            render_llm_settings(api_client, current_config)
        
        with tab3:
            render_processing_settings(api_client, current_config)
        
        with tab4:
            render_advanced_settings(api_client, current_config)
            
    except Exception as e:
        st.error(f"❌ Error loading settings: {str(e)}")


def render_search_settings(api_client, config: Dict[str, Any]):
    """Search and retrieval settings."""
    
    st.markdown("**🔍 Search & Retrieval Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top-K results
        current_top_k = config.get("TOP_K", 5)
        new_top_k = st.slider(
            "Top-K Results",
            min_value=1,
            max_value=20,
            value=current_top_k,
            step=1,
            help="Number of most relevant chunks to retrieve for each query"
        )
        
        # Similarity threshold
        current_threshold = config.get("SIMILARITY_THRESHOLD", 0.3)
        new_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=current_threshold,
            step=0.05,
            format="%.2f",
            help="Minimum similarity score for including chunks in results"
        )
        
        # Context window size
        current_context = config.get("CONTEXT_WINDOW_SIZE", 2500)
        new_context = st.number_input(
            "Context Window Size",
            min_value=1000,
            max_value=10000,
            value=current_context,
            step=500,
            help="Maximum characters to include in LLM context"
        )
    
    with col2:
        # Search preview
        st.markdown("**📊 Search Impact Preview**")
        
        # Estimate impact of changes
        if new_top_k != current_top_k:
            impact = "🔼 More sources" if new_top_k > current_top_k else "🔽 Fewer sources"
            st.info(f"Top-K: {impact}")
        
        if abs(new_threshold - current_threshold) > 0.05:
            if new_threshold > current_threshold:
                st.info("🎯 Higher quality, fewer results")
            else:
                st.info("🌐 Lower quality, more results")
        
        if abs(new_context - current_context) > 500:
            if new_context > current_context:
                st.info("📚 More context, slower responses")
            else:
                st.info("⚡ Less context, faster responses")
    
    # Apply search settings
    search_settings = {
        "TOP_K": new_top_k,
        "SIMILARITY_THRESHOLD": new_threshold,
        "CONTEXT_WINDOW_SIZE": new_context
    }
    
    if st.button("🔍 Apply Search Settings", use_container_width=True):
        apply_settings_update(api_client, search_settings, "search")


def render_llm_settings(api_client, config: Dict[str, Any]):
    """LLM and response generation settings."""
    
    st.markdown("**🤖 Language Model Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature
        current_temp = config.get("TEMPERATURE", 0.3)
        new_temp = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=current_temp,
            step=0.1,
            format="%.1f",
            help="Controls response creativity (0.0 = deterministic, 2.0 = very creative)"
        )
        
        # Max tokens
        current_max_tokens = config.get("MAX_TOKENS", 800)
        new_max_tokens = st.slider(
            "Max Response Tokens",
            min_value=100,
            max_value=2000,
            value=current_max_tokens,
            step=50,
            help="Maximum length of generated responses"
        )
        
        # Model selection (if supported)
        current_model = config.get("MODEL_NAME", "llama-3.3-70b-versatile")
        st.text_input(
            "Model Name",
            value=current_model,
            disabled=True,
            help="Current model (change in backend configuration)"
        )
    
    with col2:
        # Response style settings
        st.markdown("**🎨 Response Style**")
        
        use_citations = st.checkbox(
            "Include Source Citations",
            value=True,
            help="Add document references to responses"
        )
        
        use_confidence = st.checkbox(
            "Show Confidence Scores",
            value=True,
            help="Display confidence indicators for responses"
        )
        
        markdown_formatting = st.checkbox(
            "Enhanced Markdown",
            value=True,
            help="Use rich formatting in responses"
        )
        
        # Preview current settings
        st.markdown("**📊 Response Preview**")
        temp_desc = get_temperature_description(new_temp)
        st.info(f"🌡️ {temp_desc}")
        
        length_desc = get_length_description(new_max_tokens)
        st.info(f"📏 {length_desc}")
    
    # Apply LLM settings
    llm_settings = {
        "TEMPERATURE": new_temp,
        "MAX_TOKENS": new_max_tokens
    }
    
    if st.button("🤖 Apply LLM Settings", use_container_width=True):
        apply_settings_update(api_client, llm_settings, "LLM")


def render_processing_settings(api_client, config: Dict[str, Any]):
    """Document processing and chunking settings."""
    
    st.markdown("**📊 Document Processing Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chunk size
        current_chunk_size = config.get("CHUNK_SIZE", 1000)
        new_chunk_size = st.slider(
            "Chunk Size",
            min_value=200,
            max_value=2000,
            value=current_chunk_size,
            step=100,
            help="Number of characters per document chunk"
        )
        
        # Chunk overlap
        current_overlap = config.get("CHUNK_OVERLAP", 200)
        new_overlap = st.slider(
            "Chunk Overlap",
            min_value=0,
            max_value=min(500, new_chunk_size // 2),
            value=min(current_overlap, new_chunk_size // 2),
            step=50,
            help="Character overlap between adjacent chunks"
        )
        
        # Embedding model info
        embedding_model = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        st.text_input(
            "Embedding Model",
            value=embedding_model,
            disabled=True,
            help="Current embedding model (requires restart to change)"
        )
    
    with col2:
        # Processing impact preview
        st.markdown("**📊 Processing Impact**")
        
        # Calculate chunk statistics
        overlap_percentage = (new_overlap / new_chunk_size) * 100 if new_chunk_size > 0 else 0
        
        st.metric(
            "Overlap Percentage", 
            f"{overlap_percentage:.1f}%",
            help="Percentage of chunk content that overlaps with adjacent chunks"
        )
        
        # Estimate chunks per document
        avg_doc_size = 50000  # Estimated average document size in characters
        estimated_chunks = max(1, (avg_doc_size - new_overlap) // (new_chunk_size - new_overlap))
        st.metric(
            "Est. Chunks/Doc",
            estimated_chunks,
            help="Estimated chunks for a typical document"
        )
        
        # Processing recommendations
        if new_chunk_size < 500:
            st.warning("⚠️ Small chunks may lose context")
        elif new_chunk_size > 1500:
            st.info("📚 Large chunks preserve more context")
        
        if overlap_percentage > 50:
            st.warning("⚠️ High overlap increases storage needs")
        elif overlap_percentage < 10:
            st.warning("⚠️ Low overlap may lose connections")
    
    # Note about processing settings
    st.info("📝 **Note:** Processing settings apply to newly uploaded documents only. Existing documents need re-processing to apply changes.")
    
    # Apply processing settings
    processing_settings = {
        "CHUNK_SIZE": new_chunk_size,
        "CHUNK_OVERLAP": new_overlap
    }
    
    if st.button("📊 Apply Processing Settings", use_container_width=True):
        apply_settings_update(api_client, processing_settings, "processing")


def render_advanced_settings(api_client, config: Dict[str, Any]):
    """Advanced system settings and diagnostics."""
    
    st.markdown("**🎯 Advanced Configuration & Diagnostics**")
    
    # System information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 System Information**")
        
        # Display current system stats
        try:
            doc_stats = api_client.get_documents()
            if doc_stats:
                st.metric("Total Documents", len(doc_stats.get("documents", [])))
                st.metric("Total Chunks", doc_stats.get("chunks", doc_stats.get("total_chunks", 0)))
            
            # API response time test
            if st.button("🔄 Test API Response Time"):
                import time
                start = time.time()
                health = api_client.health_check()
                response_time = time.time() - start
                
                if health:
                    st.success(f"✅ API responding in {response_time:.3f}s")
                else:
                    st.error("❌ API health check failed")
                    
        except Exception as e:
            st.error(f"Error loading system info: {str(e)}")
    
    with col2:
        st.markdown("**🔧 Maintenance Actions**")
        
        # Re-index documents
        if st.button("🔄 Re-index All Documents", help="Rebuild search index with current settings"):
            st.warning("⚠️ This feature requires backend implementation")
        
        # Clear cache
        if st.button("🗑️ Clear System Cache", help="Clear temporary files and cache"):
            st.info("💡 Cache clearing would be implemented here")
        
        # Export settings
        if st.button("📥 Export Settings", help="Download current configuration"):
            st.download_button(
                label="💾 Download Config",
                data=str(config),
                file_name="rag_config.json",
                mime="application/json"
            )
    
    # Configuration reset
    st.markdown("---")
    st.markdown("**⚠️ Danger Zone**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset to Defaults", help="Reset all settings to default values"):
            if st.checkbox("Confirm reset to defaults"):
                default_settings = get_default_settings()
                apply_settings_update(api_client, default_settings, "reset")
    
    with col2:
        # Show current configuration as JSON
        with st.expander("🔍 View Raw Configuration"):
            st.json(config)


def get_temperature_description(temp: float) -> str:
    """Get description for temperature setting."""
    if temp < 0.3:
        return "Very focused and deterministic"
    elif temp < 0.7:
        return "Balanced creativity and consistency"
    elif temp < 1.2:
        return "Creative with some variability"
    else:
        return "Highly creative and diverse"


def get_length_description(tokens: int) -> str:
    """Get description for max tokens setting."""
    if tokens < 300:
        return "Short, concise responses"
    elif tokens < 800:
        return "Moderate length responses"
    elif tokens < 1200:
        return "Detailed responses"
    else:
        return "Very detailed, comprehensive responses"


def get_default_settings() -> Dict[str, Any]:
    """Get default configuration settings."""
    return {
        "TOP_K": 5,
        "SIMILARITY_THRESHOLD": 0.3,
        "CONTEXT_WINDOW_SIZE": 2500,
        "TEMPERATURE": 0.3,
        "MAX_TOKENS": 800,
        "CHUNK_SIZE": 1000,
        "CHUNK_OVERLAP": 200
    }


def apply_settings_update(api_client, settings: Dict[str, Any], category: str):
    """Apply settings update to backend."""
    try:
        # This would require implementing a settings update endpoint in the backend
        # For now, we'll show what would be updated
        
        st.success(f"✅ {category.title()} settings would be updated:")
        for key, value in settings.items():
            st.write(f"• {key}: {value}")
        
        st.info("💡 Settings update endpoint needs to be implemented in the backend API")
        
        # If the backend had an update_settings method:
        # result = api_client.update_settings(settings)
        # if result:
        #     st.success(f"✅ {category.title()} settings updated successfully!")
        #     st.rerun()
        # else:
        #     st.error(f"❌ Failed to update {category} settings")
            
    except Exception as e:
        st.error(f"❌ Error updating {category} settings: {str(e)}")


def render_quick_settings_panel(api_client):
    """Render a compact quick settings panel for sidebar."""
    
    st.markdown("**⚙️ Quick Settings**")
    
    try:
        config = api_client.get_config()
        if config:
            # Most commonly adjusted settings
            current_top_k = config.get("TOP_K", 5)
            new_top_k = st.slider("Results", 1, 10, current_top_k, key="quick_top_k")
            
            current_temp = config.get("TEMPERATURE", 0.3)
            new_temp = st.slider("Creativity", 0.0, 1.0, current_temp, 0.1, key="quick_temp")
            
            if st.button("Apply", key="quick_apply"):
                quick_settings = {"TOP_K": new_top_k, "TEMPERATURE": new_temp}
                apply_settings_update(api_client, quick_settings, "quick")
        else:
            st.warning("Config unavailable")
            
    except Exception as e:
        st.error(f"Settings error: {str(e)}")