"""Embedding generation using HuggingFace sentence-transformers."""

from typing import List
from sentence_transformers import SentenceTransformer
import torch


# Global model instance (singleton)
_model: SentenceTransformer = None
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2


def get_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
        # Use CPU if CUDA is not available
        if not torch.cuda.is_available():
            _model = _model.to('cpu')
    return _model


def get_embedding_dimension() -> int:
    """Get the embedding dimension for the current model."""
    return _EMBEDDING_DIMENSION


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using HuggingFace sentence-transformers.
    
    Args:
        texts: List of text strings
    
    Returns:
        List of embedding vectors (384 dimensions for all-MiniLM-L6-v2)
    """
    model = get_model()
    
    # Generate embeddings in batch
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=32,
    )
    
    # Convert to list of lists
    return embeddings.tolist()
