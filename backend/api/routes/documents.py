"""Document endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from api.models.responses import DocumentListResponse, DocumentInfo
from logger_config import logger
import os
import tempfile

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    """
    Get all uploaded documents.
    
    Returns:
        List of documents with metadata
    """
    try:
        logger.info("ENDPOINT: /documents - List documents")
        
        from main import document_service
        
        result = await document_service.get_documents()
        
        docs = [DocumentInfo(
            name=d["name"],
            file_type="unknown",
            upload_date=d.get("upload_date", ""),
            chunk_count=d["chunk_count"],
            size_bytes=d.get("size_bytes", 0)
        ) for d in result["documents"]]
        
        return DocumentListResponse(
            documents=docs,
            total_count=result["total_count"],
            total_chunks=result["total_chunks"]
        )
        
    except Exception as e:
        logger.error(f"ENDPOINT: /documents error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents for ingestion.
    
    Args:
        files: List of files to upload
        
    Returns:
        Upload result with statistics
    """
    try:
        logger.info(f"ENDPOINT: /upload - {len(files)} files")
        
        from main import document_service
        
        # Save files temporarily
        temp_paths = []
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_paths.append(temp_file.name)
        
        # Process documents
        result = await document_service.upload_documents(temp_paths)
        
        # Clean up temp files
        for path in temp_paths:
            try:
                os.remove(path)
            except:
                pass
        
        return result
        
    except Exception as e:
        logger.error(f"ENDPOINT: /upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_document_count() -> dict:
    """
    Get total document chunk count.
    
    Returns:
        Document count information
    """
    try:
        logger.info("ENDPOINT: /documents/count")
        
        from main import document_service
        
        result = await document_service.get_documents()
        
        return {
            "count": result["total_chunks"],
            "documents": result["total_count"]
        }
        
    except Exception as e:
        logger.error(f"ENDPOINT: /documents/count error: {e}", exc_info=True)
        return {"count": 0, "documents": 0}


@router.delete("/clear")
async def clear_documents() -> dict:
    """
    Clear all documents from vectorstore.
    
    Returns:
        Success status
    """
    try:
        logger.info("ENDPOINT: /documents/clear")
        
        from main import document_service
        
        await document_service.clear_all_documents()
        
        return {"success": True, "message": "All documents cleared"}
        
    except Exception as e:
        logger.error(f"ENDPOINT: /documents/clear error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
