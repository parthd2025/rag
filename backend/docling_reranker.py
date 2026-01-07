"""
Simple reranker that uses Docling node links to boost connected nodes.

The reranker expects search results in the format:
    [(text, score, metadata), ...]

And a docling graph mapping node_id -> list of linked node_ids, or the metadata can include `links`.
"""
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def rerank_using_links(results: List[Tuple[str, float, Dict[str, Any]]], hops: int = 1) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Rerank results by boosting scores when nodes are connected via Docling links.

    Strategy:
    - Extract node_ids from result metadata (metadata['node_id'] or metadata.get('id'))
    - Build a set of top node_ids
    - For each result, count how many of its links point to other top node_ids
    - Boost score: new_score = score * (1 + 0.2 * connectivity_count)

    This is intentionally simple and deterministic.
    """
    # Map node_id -> result index
    top_node_ids = []
    for _, _, meta in results:
        nid = meta.get("node_id") or meta.get("id") or meta.get("node")
        top_node_ids.append(nid)

    top_set = set([n for n in top_node_ids if n is not None])

    reranked = []
    for text, score, meta in results:
        nid = meta.get("node_id") or meta.get("id") or meta.get("node")
        links = meta.get("links") or []
        # normalize links to ids
        linked_ids = set()
        for l in links:
            if isinstance(l, dict):
                linked_ids.add(l.get("id") or l.get("node_id"))
            else:
                linked_ids.add(l)

        connectivity = len(top_set.intersection(linked_ids))
        boost = 1.0 + 0.2 * connectivity
        new_score = float(score) * boost
        reranked.append((text, new_score, meta))

    # sort by new_score descending
    reranked.sort(key=lambda t: t[1], reverse=True)
    logger.debug(f"Reranked {len(results)} results using Docling links")
    return reranked


__all__ = ["rerank_using_links"]
