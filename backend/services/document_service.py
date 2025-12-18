"""Document service for document management."""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
from logger_config import logger


class DocumentService:
    """Service for handling document operations."""
    
    def __init__(self, vectorstore, ingest_module):
        self.vectorstore = vectorstore
        self.ingest = ingest_module
    
    async def upload_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Upload and process documents.
        
        Args:
            file_paths: List of file paths to upload
            
        Returns:
            Upload result with statistics
        """
        try:
            logger.info(f"DOCUMENT_SERVICE: Uploading {len(file_paths)} documents")
            
            results = []
            total_chunks = 0
            
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.warning(f"DOCUMENT_SERVICE: File not found: {file_path}")
                    continue
                
                # Ingest document
                chunks = self.ingest.ingest_document(file_path)
                total_chunks += len(chunks)
                
                results.append({
                    "file": os.path.basename(file_path),
                    "chunks": len(chunks),
                    "size_bytes": os.path.getsize(file_path),
                    "upload_date": datetime.now().isoformat()
                })
            
            logger.info(f"DOCUMENT_SERVICE: Uploaded {len(results)} documents with {total_chunks} chunks")
            
            return {
                "success": True,
                "documents_processed": len(results),
                "total_chunks": total_chunks,
                "details": results
            }
            
        except Exception as e:
            logger.error(f"DOCUMENT_SERVICE: Error uploading documents: {e}", exc_info=True)
            raise
    
    async def get_documents(self) -> Dict[str, Any]:
        """
        Get all loaded documents.
        
        Returns:
            List of document metadata
        """
        try:
            metadata = self.vectorstore.get_metadata()
            
            documents = []
            total_chunks = 0
            
            if metadata:
                for doc_name, doc_info in metadata.items():
                    chunk_count = len(doc_info.get("chunks", []))
                    total_chunks += chunk_count
                    
                    documents.append({
                        "name": doc_name,
                        "chunk_count": chunk_count,
                        "upload_date": doc_info.get("upload_date", "unknown"),
                        "size_bytes": doc_info.get("size_bytes", 0)
                    })
            
            return {
                "documents": documents,
                "total_count": len(documents),
                "total_chunks": total_chunks
            }
            
        except Exception as e:
            logger.error(f"DOCUMENT_SERVICE: Error retrieving documents: {e}")
            raise
    
    async def delete_document(self, document_name: str) -> bool:
        """
        Delete a document from vectorstore.
        
        Args:
            document_name: Name of document to delete
            
        Returns:
            Success status
        """
        try:
            logger.info(f"DOCUMENT_SERVICE: Deleting document: {document_name}")
            self.vectorstore.delete_document(document_name)
            return True
        except Exception as e:
            logger.error(f"DOCUMENT_SERVICE: Error deleting document: {e}")
            raise
    
    async def clear_all_documents(self) -> bool:
        """Clear all documents from vectorstore."""
        try:
            logger.info("DOCUMENT_SERVICE: Clearing all documents")
            self.vectorstore.clear()
            return True
        except Exception as e:
            logger.error(f"DOCUMENT_SERVICE: Error clearing documents: {e}")
            raise
