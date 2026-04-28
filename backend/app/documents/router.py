import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user, get_optional_user
from app.documents.ingestion import save_upload, extract_text, validate_file
from app.documents.chunker import split_into_chunks
from app.embeddings.vector_store import get_vector_store
from app import models, schemas

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=schemas.DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    """
    Upload a PDF/DOCX/TXT file.
    Pipeline: save → validate → parse text → chunk → embed → store in ChromaDB + SQLite
    """
    file_bytes = await file.read()

    # 1. Validate
    try:
        file_ext = validate_file(file.filename, len(file_bytes))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Save to disk
    saved_path, unique_name = save_upload(file_bytes, file.filename)

    # 3. Create DB record with "processing" status
    doc = models.Document(
        filename=unique_name,
        original_name=file.filename,
        file_type=file_ext,
        file_size=len(file_bytes),
        file_path=saved_path,
        status="processing",
        owner_id=current_user.id if current_user else None,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        # 4. Extract text (page by page)
        pages = extract_text(saved_path, file_ext)
        if not pages:
            raise ValueError("No text could be extracted from this document")

        # 5. Split into chunks
        chunks = split_into_chunks(pages)
        if not chunks:
            raise ValueError("Document appears to be empty or unreadable")

        # 6. Embed + store in ChromaDB
        vector_store = get_vector_store()
        chroma_ids = vector_store.add_chunks(
            chunks=chunks,
            document_id=doc.id,
            document_name=file.filename,
        )

        # 7. Save chunks to SQLite
        for i, (chunk, chroma_id) in enumerate(zip(chunks, chroma_ids)):
            db_chunk = models.Chunk(
                document_id=doc.id,
                chunk_index=chunk["chunk_index"],
                content=chunk["text"],
                page_number=chunk["page"],
                chroma_id=chroma_id,
            )
            db.add(db_chunk)

        # 8. Mark document as indexed
        doc.status = "indexed"
        doc.total_chunks = len(chunks)
        db.commit()
        db.refresh(doc)

    except Exception as e:
        doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return doc


@router.get("/", response_model=schemas.DocumentListResponse)
def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all uploaded and indexed documents."""
    query = db.query(models.Document).filter(models.Document.status == "indexed")
    total = query.count()
    documents = query.order_by(models.Document.created_at.desc()).offset(skip).limit(limit).all()
    return schemas.DocumentListResponse(documents=documents, total=total)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a document and remove its embeddings from ChromaDB."""
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Only owner or admin can delete
    if doc.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")

    # Remove from ChromaDB
    try:
        vector_store = get_vector_store()
        chunk_ids = [c.chroma_id for c in doc.chunks if c.chroma_id]
        if chunk_ids:
            vector_store.delete_chunks(chunk_ids)
    except Exception:
        pass  # Don't block deletion if vector store removal fails

    db.delete(doc)
    db.commit()


@router.get("/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Return summary statistics."""
    from sqlalchemy import func
    total_docs = db.query(models.Document).filter(models.Document.status == "indexed").count()
    total_chunks = db.query(models.Chunk).count()
    total_queries = db.query(models.QueryLog).count()
    avg_score = db.query(func.avg(models.QueryLog.top_score)).scalar()
    return schemas.StatsResponse(
        total_documents=total_docs,
        total_chunks=total_chunks,
        total_queries=total_queries,
        avg_similarity_score=round(avg_score, 3) if avg_score else None,
    )
