import time
from typing import List, Optional
from app.embeddings.vector_store import get_vector_store
from app.config import settings


def semantic_search(
    query: str,
    top_k: int = None,
    document_ids: Optional[List[int]] = None,
) -> dict:
    """
    Full semantic search pipeline.

    Steps:
    1. Embed the query into a vector
    2. Search ChromaDB for top-k most similar chunks
    3. Filter out results below similarity threshold
    4. Return ranked results with metadata

    Returns dict with results + timing info.
    """
    top_k = top_k or settings.top_k_results
    start_time = time.time()

    vector_store = get_vector_store()

    # Check if anything is indexed
    if vector_store.count() == 0:
        return {
            "results": [],
            "search_time_ms": 0,
            "message": "No documents indexed yet. Please upload some documents first.",
        }

    # Perform vector similarity search
    raw_results = vector_store.search(
        query=query,
        top_k=top_k,
        document_ids=document_ids,
        min_score=settings.similarity_threshold,
    )

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "results": raw_results,
        "search_time_ms": elapsed_ms,
        "message": None if raw_results else "No relevant documents found for this query.",
    }


def mmr_rerank(
    results: List[dict],
    query_embedding: List[float],
    lambda_mult: float = 0.5,
) -> List[dict]:
    """
    Maximal Marginal Relevance (MMR) reranking.

    PURPOSE: Avoid returning 5 chunks that all say the same thing.
    MMR balances relevance (close to query) vs diversity (different from each other).

    lambda_mult = 1.0 → pure relevance (no diversity)
    lambda_mult = 0.0 → pure diversity (no relevance)
    lambda_mult = 0.5 → balanced (recommended)
    """
    from app.embeddings.embedder import cosine_similarity

    if not results:
        return results

    selected = []
    candidates = results.copy()

    while candidates and len(selected) < len(results):
        if not selected:
            # First pick: highest similarity to query
            best = max(candidates, key=lambda x: x["similarity_score"])
        else:
            # Subsequent picks: balance relevance vs redundancy
            best = None
            best_score = float("-inf")
            for candidate in candidates:
                # Relevance to query
                relevance = candidate["similarity_score"]
                # Max similarity to already selected items
                max_redundancy = max(
                    cosine_similarity(
                        [candidate["similarity_score"]],
                        [s["similarity_score"]],
                    )
                    for s in selected
                )
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_redundancy
                if mmr_score > best_score:
                    best_score = mmr_score
                    best = candidate

        selected.append(best)
        candidates.remove(best)

    return selected
