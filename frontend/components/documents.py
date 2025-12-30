"""
Documents - Enhanced Document Management
"""

import streamlit as st
import time
from typing import Dict, List, Any
from datetime import datetime


def render_upload_section(api_client):
    """Enhanced upload with batch processing and previews."""
    
    # Upload section with better organization
    st.subheader("📤 Document Upload")
    
    files = st.file_uploader(
        "Select documents to upload:", 
        type=["pdf", "docx", "txt", "md", "csv", "xlsx", "pptx", "html"], 
        accept_multiple_files=True,
        help="Supported formats: PDF, Word, Text, Markdown, CSV, Excel, PowerPoint, HTML"
    )
    
    if files:
        # Enhanced file preview with better formatting
        st.markdown(f"**📋 {len(files)} file(s) selected for upload:**")
        
        # Create columns for better layout
        preview_container = st.container()
        with preview_container:
            for i, f in enumerate(files):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    # File name with type icon
                    file_icon = get_file_icon(f.name)
                    st.write(f"{file_icon} {f.name}")
                
                with col2:
                    # File size with better formatting
                    size_mb = f.size / (1024 * 1024)
                    if size_mb < 1:
                        st.write(f"{f.size / 1024:.1f} KB")
                    else:
                        st.write(f"{size_mb:.1f} MB")
                
                with col3:
                    # File type
                    file_ext = f.name.split('.')[-1].upper()
                    st.write(f"📄 {file_ext}")
                
                with col4:
                    # Status indicator (will be updated during upload)
                    status_placeholder = st.empty()
                    status_placeholder.write("⏳ Ready")
        
        # Upload controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            upload_button = st.button(
                f"🚀 Upload {len(files)} Files", 
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            # Batch size control
            batch_size = st.selectbox(
                "Batch size:",
                [1, 3, 5, 10],
                index=1,
                help="Number of files to process simultaneously"
            )
        
        with col3:
            # Processing options
            show_details = st.checkbox("Show details", value=True)
        
        if upload_button:
            upload_with_progress(api_client, files, batch_size, show_details)


def get_file_icon(filename: str) -> str:
    """Get emoji icon based on file extension."""
    ext = filename.split('.')[-1].lower()
    icons = {
        'pdf': '📄', 'docx': '📝', 'doc': '📝', 'txt': '📄', 'md': '📑',
        'csv': '📊', 'xlsx': '📈', 'xls': '📈', 'pptx': '📺', 'ppt': '📺',
        'html': '🌐', 'htm': '🌐'
    }
    return icons.get(ext, '📄')


def upload_with_progress(api_client, files, batch_size: int, show_details: bool):
    """Handle batch upload with enhanced progress tracking."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    success_count = 0
    total_chunks = 0
    failed_files = []
    
    # Process files in batches
    for batch_start in range(0, len(files), batch_size):
        batch = files[batch_start:batch_start + batch_size]
        
        for i, f in enumerate(batch):
            current_file = batch_start + i + 1
            progress = current_file / len(files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {current_file}/{len(files)}: {f.name}")
            
            try:
                start_time = time.time()
                r = api_client.upload_document(f.getvalue(), f.name)
                processing_time = time.time() - start_time
                
                chunks = r.get('chunks_created', 0)
                total_chunks += chunks
                success_count += 1
                
                if show_details:
                    with results_container:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"✅ {f.name}")
                        with col2:
                            st.write(f"{chunks} chunks")
                        with col3:
                            st.write(f"{processing_time:.1f}s")
                        with col4:
                            st.write("Success")
                            
            except Exception as e:
                failed_files.append((f.name, str(e)))
                if show_details:
                    with results_container:
                        st.write(f"❌ {f.name}: {str(e)}")
    
    # Final results
    progress_bar.progress(1.0)
    status_text.empty()
    
    # Summary with enhanced formatting
    if success_count > 0:
        st.success(
            f"🎉 Upload Complete: {success_count}/{len(files)} files processed successfully\n"
            f"📊 Total chunks created: {total_chunks}"
        )
    
    if failed_files:
        st.error(f"❌ {len(failed_files)} files failed to upload:")
        for name, error in failed_files:
            st.write(f"• {name}: {error}")
    
    # Auto-refresh after upload
    time.sleep(1)
    st.rerun()


def render_document_stats(api_client):
    """Enhanced document statistics with better organization."""
    st.subheader("📊 Document Statistics")
    
    try:
        d = api_client.get_documents()
        if d and d.get("documents"):
            # Main metrics in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "📄 Documents", 
                    len(d.get("documents", [])),
                    help="Total number of uploaded documents"
                )
            
            with col2:
                total_chunks = d.get("chunks", d.get("total_chunks", 0))
                st.metric(
                    "🧩 Chunks", 
                    f"{total_chunks:,}",
                    help="Total number of text chunks for search"
                )
            
            with col3:
                # Calculate average chunks per document
                docs_count = len(d.get("documents", []))
                avg_chunks = total_chunks / docs_count if docs_count > 0 else 0
                st.metric(
                    "📈 Avg/Doc", 
                    f"{avg_chunks:.1f}",
                    help="Average chunks per document"
                )
            
            # Document list with enhanced details
            if d.get("documents"):
                st.markdown("**📋 Document Library:**")
                
                for i, doc in enumerate(d.get("documents", [])[:10]):  # Show up to 10
                    doc_name = doc.get('name', '?')
                    doc_chunks = doc.get('chunks', doc.get('chunk_count', 0))
                    upload_date = doc.get('upload_date', '')
                    
                    # Format date if available
                    date_str = ""
                    if upload_date:
                        try:
                            dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                            date_str = f" • {dt.strftime('%Y-%m-%d %H:%M')}"
                        except:
                            date_str = f" • {upload_date[:10]}"
                    
                    icon = get_file_icon(doc_name)
                    st.write(f"{icon} **{doc_name}** ({doc_chunks} chunks){date_str}")
                
                if len(d.get("documents", [])) > 10:
                    remaining = len(d.get("documents", [])) - 10
                    st.write(f"*...and {remaining} more documents*")
        else:
            st.info("📭 No documents uploaded yet. Use the upload section above to get started!")
            
    except Exception as e:
        st.error(f"❌ Error loading document statistics: {str(e)}")
        st.info("📭 No documents available")


def render_document_management(api_client):
    """Enhanced document management with individual deletion."""
    st.subheader("🗂️ Document Management")
    
    # Get current documents
    try:
        d = api_client.get_documents()
        documents = d.get("documents", []) if d else []
        
        if documents:
            # Document management options
            tab1, tab2 = st.tabs(["📋 Document List", "🗑️ Bulk Actions"])
            
            with tab1:
                st.markdown("**Manage individual documents:**")
                
                for i, doc in enumerate(documents):
                    doc_name = doc.get('name', '?')
                    doc_chunks = doc.get('chunks', doc.get('chunk_count', 0))
                    
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        icon = get_file_icon(doc_name)
                        st.write(f"{icon} **{doc_name}**")
                        st.caption(f"{doc_chunks} chunks")
                    
                    with col2:
                        # Individual delete button
                        if st.button(f"🗑️", key=f"del_{i}", help=f"Delete {doc_name}"):
                            if st.session_state.get(f"confirm_del_{i}", False):
                                try:
                                    with st.spinner(f"Deleting {doc_name}..."):
                                        success = api_client.delete_document(doc_name)
                                        if success:
                                            st.success(f"✅ Deleted '{doc_name}' successfully!")
                                            # Clear confirmation state
                                            if f"confirm_del_{i}" in st.session_state:
                                                del st.session_state[f"confirm_del_{i}"]
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Failed to delete '{doc_name}'")
                                except Exception as e:
                                    st.error(f"❌ Error deleting '{doc_name}': {str(e)}")
                            else:
                                st.session_state[f"confirm_del_{i}"] = True
                                st.rerun()
                    
                    with col3:
                        # Confirmation checkbox for deletion
                        if st.session_state.get(f"confirm_del_{i}", False):
                            st.write("✅ Confirm")
            
            with tab2:
                st.markdown("**Bulk operations:**")
                
                # Clear all with enhanced confirmation
                st.warning("⚠️ This will remove ALL documents and their chunks from the system.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    clear_button = st.button(
                        "🗑️ Clear All Documents", 
                        use_container_width=True,
                        type="secondary"
                    )
                
                with col2:
                    confirm_clear = st.checkbox(
                        "I understand this cannot be undone",
                        help="Check this box to enable the clear operation"
                    )
                
                if clear_button and confirm_clear:
                    with st.spinner("Clearing all documents..."):
                        try:
                            api_client.clear_data()
                            st.success("✅ All documents cleared successfully!")
                            # Clear any session state
                            for key in list(st.session_state.keys()):
                                if key.startswith("confirm_del_"):
                                    del st.session_state[key]
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error clearing documents: {str(e)}")
                elif clear_button and not confirm_clear:
                    st.error("Please confirm that you understand this operation cannot be undone.")
        
        else:
            st.info("📁 No documents to manage. Upload some documents first!")
            
    except Exception as e:
        st.error(f"❌ Error loading documents: {str(e)}")
