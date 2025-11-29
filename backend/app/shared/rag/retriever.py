"""RAG retriever combining BM25 (PostgreSQL) and vector search (Qdrant)."""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.shared.database.qdrant import search_vectors, COLLECTION_NAME
from app.shared.ingestion.embedder import generate_embeddings
from app.models import Chunk, Video


def bm25_search(query: str, top_k: int = 10, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Perform BM25-style full-text search in PostgreSQL.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        db: Optional database session (if None, creates new one)
    
    Returns:
        List of chunk results with scores
    """
    from app.shared.database.postgres import get_db
    
    close_db = False
    if db is None:
        db_gen = get_db()
        db = next(db_gen)
        close_db = True
    
    try:
        # Use PostgreSQL's full-text search with ts_rank
        # This provides BM25-like ranking
        sql_query = text("""
            SELECT 
                c.id,
                c.video_id,
                c.start_time,
                c.end_time,
                c.text,
                c.qdrant_id,
                v.title as video_title,
                v.url as video_url,
                ts_rank(
                    to_tsvector('english', c.text),
                    plainto_tsquery('english', :query)
                ) as rank_score
            FROM chunks c
            JOIN videos v ON c.video_id = v.id
            WHERE to_tsvector('english', c.text) @@ plainto_tsquery('english', :query)
            ORDER BY rank_score DESC
            LIMIT :limit
        """)
        
        results = db.execute(
            sql_query,
            {"query": query, "limit": top_k}
        ).fetchall()
        
        chunks = []
        for row in results:
            chunks.append({
                "chunk_id": row.id,
                "video_id": row.video_id,
                "video_title": row.video_title,
                "video_url": row.video_url,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "text": row.text,
                "qdrant_id": row.qdrant_id,
                "score": float(row.rank_score),
                "source": "bm25"
            })
        
        return chunks
    finally:
        if close_db:
            db.close()


def vector_search(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search in Qdrant.
    
    Args:
        query: Search query string
        top_k: Number of results to return
    
    Returns:
        List of chunk results with scores
    """
    # Generate embedding for query
    query_embedding = generate_embeddings([query])[0]
    
    # Search in Qdrant
    results = search_vectors(
        query_vector=query_embedding,
        limit=top_k,
    )
    
    chunks = []
    for result in results:
        payload = result["payload"]
        chunks.append({
            "chunk_id": None,  # Will be looked up from qdrant_id if needed
            "video_id": payload.get("video_id"),
            "video_title": payload.get("video_title"),
            "video_url": payload.get("video_url"),
            "start_time": payload.get("start_time"),
            "end_time": payload.get("end_time"),
            "text": payload.get("text"),
            "qdrant_id": result["id"],
            "score": float(result["score"]),
            "source": "vector"
        })
    
    return chunks


def retrieve_chunks(
    query: str,
    top_k: int = 10,
    bm25_k: int = 10,
    vector_k: int = 10,
    video_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks using hybrid search (BM25 + Vector).
    
    Combines results from PostgreSQL BM25 search and Qdrant vector search,
    then deduplicates by qdrant_id.
    
    Args:
        query: Search query string
        top_k: Total number of results to return after combining
        bm25_k: Number of BM25 results to fetch
        vector_k: Number of vector results to fetch
        video_ids: Optional list of video IDs to filter by
    
    Returns:
        List of unique chunk results with metadata
    """
    # Perform both searches
    bm25_results = bm25_search(query, top_k=bm25_k)
    vector_results = vector_search(query, top_k=vector_k)
    
    # Apply video filter if provided
    if video_ids:
        bm25_results = [r for r in bm25_results if r["video_id"] in video_ids]
        vector_results = [r for r in vector_results if r["video_id"] in video_ids]
    
    # Combine and deduplicate by qdrant_id
    seen_ids = set()
    combined_results = []
    
    # Add vector results first (typically higher quality)
    for result in vector_results:
        qdrant_id = result.get("qdrant_id")
        if qdrant_id and qdrant_id not in seen_ids:
            seen_ids.add(qdrant_id)
            combined_results.append(result)
    
    # Add BM25 results that aren't already included
    for result in bm25_results:
        qdrant_id = result.get("qdrant_id")
        if qdrant_id and qdrant_id not in seen_ids:
            seen_ids.add(qdrant_id)
            combined_results.append(result)
    
    # Sort by score (vector scores are typically 0-1, BM25 scores vary)
    # Normalize scores for better comparison
    for result in combined_results:
        if result["source"] == "vector":
            # Vector scores are already normalized (cosine similarity)
            result["normalized_score"] = result["score"]
        else:
            # Normalize BM25 scores (rough normalization)
            # BM25 scores can vary widely, so we'll use a simple min-max approach
            result["normalized_score"] = min(result["score"] / 10.0, 1.0) if result["score"] > 0 else 0.0
    
    # Sort by normalized score
    combined_results.sort(key=lambda x: x["normalized_score"], reverse=True)
    
    # Return top_k results
    return combined_results[:top_k]
