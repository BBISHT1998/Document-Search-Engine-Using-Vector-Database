from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config import settings

# [OK][OK][OK][OK][OK][OK][OK][OK][OK] Singleton pattern [OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK][OK]
# Load the model once at startup [OK][OK][OK] it's ~90MB, we don't want to reload it
# per request. Using a module-level variable acts like a singleton.
_model = None  # SentenceTransformer instance, loaded lazily


def get_embedder() -> SentenceTransformer:
    """
    Returns the singleton embedding model instance.

    Model: all-MiniLM-L6-v2
    - Produces 384-dimensional vectors
    - Very fast (CPU-friendly)
    - Great quality for semantic similarity
    - Downloaded once from HuggingFace Hub (~90MB)
    """
    global _model
    if _model is None:
        print(f"[Embedder] Loading model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        print("[Embedder] Model loaded successfully [OK][OK][OK]")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of text strings into embedding vectors.

    Input:  ["cats are mammals", "dogs are pets"]
    Output: [[0.12, -0.55, ...], [0.14, -0.52, ...]]  (384 dims each)

    Uses batch processing for efficiency.
    """
    model = get_embedder()
    # normalize_embeddings=True [OK][OK][OK] vectors on unit sphere
    # Makes cosine similarity = dot product (faster)
    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 50,
    )
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Embed a single search query string."""
    return embed_texts([query])[0]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors (0 to 1)."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))
