import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.auth.dependencies import get_optional_user
from app.search.retriever import semantic_search
from app import models, schemas

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/", response_model=schemas.SearchResponse)
def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Number of results"),
    document_ids: Optional[str] = Query(None, description="Comma-separated document IDs to filter"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    """
    Semantic search across all indexed documents.

    Returns ranked chunks with similarity scores.
    Score of 1.0 = perfect match, 0.0 = completely unrelated.
    Results below the similarity threshold are filtered out.
    """
    # Parse optional document filter
    doc_id_list = None
    if document_ids:
        try:
            doc_id_list = [int(d.strip()) for d in document_ids.split(",") if d.strip()]
        except ValueError:
            pass

    # Run semantic search
    search_result = semantic_search(query=q, top_k=limit, document_ids=doc_id_list)

    # Format results to schema
    formatted_results = []
    for hit in search_result["results"]:
        score = hit["similarity_score"]
        formatted_results.append(schemas.SearchResult(
            chunk_id=hit["chroma_id"],
            content=hit["text"],
            document_name=hit["document_name"],
            document_id=hit["document_id"],
            page_number=hit.get("page_number"),
            similarity_score=score,
            relevance_percent=int(score * 100),
        ))

    # Log the query to SQLite
    try:
        log = models.QueryLog(
            query_text=q,
            query_type="search",
            results_count=len(formatted_results),
            top_score=formatted_results[0].similarity_score if formatted_results else None,
            response_time_ms=search_result["search_time_ms"],
            user_id=current_user.id if current_user else None,
        )
        db.add(log)
        db.commit()
    except Exception:
        pass  # Don't fail the request if logging fails

    return schemas.SearchResponse(
        query=q,
        results=formatted_results,
        total_results=len(formatted_results),
        search_time_ms=search_result["search_time_ms"],
    )
