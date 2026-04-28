from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_optional_user
from app.rag.pipeline import run_rag_pipeline
from app import models, schemas

router = APIRouter(prefix="/rag", tags=["RAG Chatbot"])


@router.post("/chat", response_model=schemas.RAGResponse)
def rag_chat(
    payload: schemas.RAGRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    """
    RAG-powered Q&A endpoint.

    Send a question and receive a grounded answer with source citations.
    Optionally include conversation history for multi-turn conversations.
    Optionally filter by specific document IDs.
    """
    result = run_rag_pipeline(
        question=payload.question,
        conversation_history=payload.conversation_history,
        document_ids=payload.document_ids,
    )

    # Log to SQLite
    try:
        log = models.QueryLog(
            query_text=payload.question,
            query_type="rag",
            results_count=len(result["sources"]),
            top_score=result["sources"][0]["similarity_score"] if result["sources"] else None,
            response_time_ms=result["response_time_ms"],
            user_id=current_user.id if current_user else None,
        )
        db.add(log)
        db.commit()
    except Exception:
        pass

    # Build source response objects
    sources = [
        schemas.RAGSource(
            document_name=s["document_name"],
            document_id=s["document_id"],
            page_number=s.get("page_number"),
            chunk_preview=s["chunk_preview"],
            similarity_score=s["similarity_score"],
        )
        for s in result["sources"]
    ]

    return schemas.RAGResponse(
        question=payload.question,
        answer=result["answer"],
        sources=sources,
        has_answer=result["has_answer"],
        response_time_ms=result["response_time_ms"],
    )
