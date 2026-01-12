"""
Local Docling client for enriching chunks with document structure and semantic links.

Usage:
    from backend.docling_client import DoclingClient
    client = DoclingClient()
    nodes = client.enrich_chunks(chunks, source="file.xlsx")

This module uses the local Docling library for document structure extraction.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    DOCLING_AVAILABLE = True
    
    # Get all available formats
    SUPPORTED_FORMATS = [
        InputFormat.PDF,
        InputFormat.DOCX,
        InputFormat.PPTX,
        InputFormat.HTML,
        InputFormat.IMAGE,
    ]
    
    # Add Excel formats if available
    if hasattr(InputFormat, 'XLSX'):
        SUPPORTED_FORMATS.append(InputFormat.XLSX)
    if hasattr(InputFormat, 'XLS'):
        SUPPORTED_FORMATS.append(InputFormat.XLS)
        
except ImportError:
    DOCLING_AVAILABLE = False
    SUPPORTED_FORMATS = []
    logging.warning("Docling library not installed. Install with: pip install docling")

logger = logging.getLogger(__name__)


class DoclingClient:
    """Local Docling-based document structure extractor."""
    
    def __init__(self):
        if not DOCLING_AVAILABLE:
            logger.warning("Docling not available - enrichment will use fallback mode")
            self.converter = None
        else:
            try:
                # Initialize Docling converter with all supported formats
                self.converter = DocumentConverter(allowed_formats=SUPPORTED_FORMATS)
                logger.info(f"Docling converter initialized with formats: {[f.value for f in SUPPORTED_FORMATS]}")
            except Exception as e:
                logger.error(f"Failed to initialize Docling converter: {e}")
                self.converter = None

    def enrich_chunks(self, chunks: List[Any], source: str = "unknown", source_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enrich chunks with document structure and semantic links.

        Args:
            chunks: list of strings or dicts (if dict, expects a `text` key)
            source: source document identifier
            source_path: optional path to source file for structure extraction

        Returns:
            List of nodes: each node is a dict with keys `id`, `text`, `meta`, `links`.
        """
        # If Docling is unavailable or no source path provided, use enhanced fallback
        if not self.converter or not source_path:
            return self._create_fallback_nodes(chunks, source)
        
        try:
            # Convert document to extract structure
            logger.info(f"Processing document with Docling: {source_path}")
            result = self.converter.convert(source_path)
            
            # Extract document structure
            doc_structure = self._extract_structure(result)
            
            # Enrich chunks with structure information
            enriched_nodes = self._match_chunks_to_structure(chunks, doc_structure, source)
            
            logger.info(f"Docling enriched {len(enriched_nodes)} chunks with structure data")
            return enriched_nodes
            
        except Exception as e:
            logger.exception(f"Docling enrichment failed: {e}")
            return self._create_fallback_nodes(chunks, source)
    
    def _extract_structure(self, doc_result) -> Dict[str, Any]:
        """Extract hierarchical structure from Docling result."""
        structure = {
            "sections": [],
            "tables": [],
            "figures": [],
            "links": []
        }
        
        try:
            # Extract document elements
            doc = doc_result.document
            
            # Get sections/headings
            for item in doc.iterate_items():
                if hasattr(item, 'label'):
                    if 'heading' in item.label.lower() or 'title' in item.label.lower():
                        structure["sections"].append({
                            "text": item.text,
                            "level": getattr(item, 'level', 1),
                            "bbox": getattr(item, 'bbox', None)
                        })
                    elif 'table' in item.label.lower():
                        structure["tables"].append({
                            "text": item.text,
                            "bbox": getattr(item, 'bbox', None)
                        })
                    elif 'figure' in item.label.lower() or 'image' in item.label.lower():
                        structure["figures"].append({
                            "text": getattr(item, 'text', ''),
                            "bbox": getattr(item, 'bbox', None)
                        })
            
            # Extract cross-references if available
            if hasattr(doc, 'links'):
                structure["links"] = doc.links
                
        except Exception as e:
            logger.warning(f"Error extracting structure: {e}")
        
        return structure
    
    def _match_chunks_to_structure(self, chunks: List[Any], structure: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
        """Match chunks to document structure and create enriched nodes."""
        enriched_nodes = []
        
        for i, chunk in enumerate(chunks):
            # Extract chunk text
            if isinstance(chunk, dict):
                text = chunk.get("text") or chunk.get("chunk") or ""
                meta = chunk.get("meta") or {}
            else:
                text = str(chunk)
                meta = {}
            
            # Generate stable node ID
            node_id = self._generate_node_id(text, source, i)
            
            # Find relevant structure elements
            relevant_section = self._find_relevant_section(text, structure["sections"])
            links = self._find_semantic_links(text, structure, i, len(chunks))
            
            # Build enriched node
            node = {
                "id": node_id,
                "text": text,
                "meta": {
                    **meta,
                    "source": source,
                    "chunk_index": i,
                    "section": relevant_section,
                    "has_tables": any(t["text"][:50] in text for t in structure["tables"][:5]),
                    "has_figures": any(f["text"][:50] in text for f in structure["figures"][:5]),
                },
                "links": links
            }
            enriched_nodes.append(node)
        
        return enriched_nodes
    
    def _find_relevant_section(self, text: str, sections: List[Dict]) -> Optional[str]:
        """Find the most relevant section heading for a chunk."""
        # Simple heuristic: return the last section that appears before this text
        for section in reversed(sections):
            if section["text"] and len(section["text"]) > 3:
                return section["text"]
        return None
    
    def _find_semantic_links(self, text: str, structure: Dict, idx: int, total: int) -> List[str]:
        """Find semantic links between chunks."""
        links = []
        
        # Link to adjacent chunks (sequential context)
        if idx > 0:
            links.append(f"prev-{idx-1}")
        if idx < total - 1:
            links.append(f"next-{idx+1}")
        
        # Could add more sophisticated linking based on:
        # - Shared section membership
        # - Table/figure references
        # - Cross-references in structure["links"]
        
        return links
    
    def _generate_node_id(self, text: str, source: str, index: int) -> str:
        """Generate a stable, unique node ID."""
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"{source}-{index}-{content_hash}"
    
    def _create_fallback_nodes(self, chunks: List[Any], source: str) -> List[Dict[str, Any]]:
        """Create basic nodes without structure extraction (fallback mode)."""
        logger.info(f"Using fallback mode for {len(chunks)} chunks")
        fallback_nodes = []
        
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, dict):
                text = chunk.get("text") or chunk.get("chunk") or ""
                meta = chunk.get("meta") or {}
            else:
                text = str(chunk)
                meta = {}
            
            node = {
                "id": self._generate_node_id(text, source, i),
                "text": text,
                "meta": {**meta, "source": source, "chunk_index": i},
                "links": [
                    f"prev-{i-1}" if i > 0 else None,
                    f"next-{i+1}" if i < len(chunks) - 1 else None
                ]
            }
            # Remove None links
            node["links"] = [link for link in node["links"] if link]
            fallback_nodes.append(node)
        
        return fallback_nodes


__all__ = ["DoclingClient"]
