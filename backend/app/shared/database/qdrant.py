"""Qdrant vector database client."""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, CollectionStatus
)
from typing import List, Dict, Any, Optional

from app.shared.config.settings import QDRANT_HOST, QDRANT_PORT

# Collection name
COLLECTION_NAME = "youtubelm_transcripts"
# Vector dimension for sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIMENSION = 384

# Global client instance
_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    """Get Qdrant client instance (singleton)."""
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=int(QDRANT_PORT))
    return _client


def ensure_collection():
    """Ensure Qdrant collection exists."""
    client = get_client()
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if COLLECTION_NAME not in collection_names:
        # Create collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_DIMENSION,
                distance=Distance.COSINE,
            ),
        )


def upsert_points(points: List[PointStruct]):
    """Upsert points to Qdrant collection."""
    client = get_client()
    ensure_collection()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


def search_vectors(
    query_vector: List[float],
    limit: int = 5,
    filter_dict: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Search vectors in Qdrant."""
    client = get_client()
    ensure_collection()
    
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter=filter_dict,
    )
    
    results = []
    for hit in search_result:
        results.append({
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload,
        })
    
    return results
