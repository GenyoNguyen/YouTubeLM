"""Reranker using cross-encoder model for improved relevance ranking."""

from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder


# Global reranker model instance (singleton)
_reranker: CrossEncoder = None
_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_reranker() -> CrossEncoder:
    """Get or initialize the reranker model (singleton)."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(_MODEL_NAME)
    return _reranker


def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Rerank search results using cross-encoder model.
    
    Args:
        query: Original search query
        results: List of chunk results from retriever
        top_k: Optional number of top results to return after reranking
    
    Returns:
        Reranked list of results with updated scores
    """
    if not results:
        return []
    
    # Get reranker model
    reranker = get_reranker()
    
    # Prepare query-document pairs for reranking
    pairs = []
    for result in results:
        text = result.get("text", "")
        pairs.append([query, text])
    
    # Get reranking scores
    rerank_scores = reranker.predict(pairs)
    
    # Update results with rerank scores
    for i, result in enumerate(results):
        result["rerank_score"] = float(rerank_scores[i])
        # Keep original score for reference
        result["original_score"] = result.get("normalized_score", result.get("score", 0.0))
    
    # Sort by rerank score
    reranked_results = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
    
    # Return top_k if specified
    if top_k is not None:
        return reranked_results[:top_k]
    
    return reranked_results
