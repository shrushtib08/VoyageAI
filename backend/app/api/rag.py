import logging
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.rag.embeddings import EmbeddingError
from app.rag.ingestion import (
    DocumentMetadata,
    RagStorageUnavailable,
    SUPPORTED_EXTENSIONS,
    ingest_document,
)
from app.rag.rag_service import rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG knowledge"])
MAX_DOCUMENT_BYTES = 20 * 1024 * 1024


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    destination: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    document_type: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


def require_rag_admin(user: User = Depends(get_current_user)) -> User:
    if user.username.casefold() not in settings.rag_admin_usernames:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RAG administrator access required.")
    return user


def _parse_date(value: Optional[str], field_name: str) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{field_name} must use YYYY-MM-DD format.") from exc


def _optional_text(value: Optional[str]) -> Optional[str]:
    return value.strip() or None if value else None


@router.post("/search")
async def search_knowledge(
    request: RagSearchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    del user
    filters = {
        "destination": request.destination,
        "country": request.country,
        "category": request.category,
        "document_type": request.document_type,
    }
    try:
        results = await rag_service.retriever.search(
            request.query,
            filters=filters,
            top_k=request.top_k,
            db=db,
        )
    except RagStorageUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EmbeddingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"results": results, "source_type": "RAG KNOWLEDGE"}


@router.get("/admin/documents")
def list_documents(
    admin: User = Depends(require_rag_admin),
    db: Session = Depends(get_db),
):
    del admin
    if db.get_bind().dialect.name != "postgresql":
        raise HTTPException(status_code=503, detail="RAG administration requires PostgreSQL with pgvector.")
    rows = db.execute(
        text(
            """
            SELECT d.id, d.title, d.source, d.url, d.destination, d.country, d.category,
                   d.document_type, d.publication_date, d.update_date, d.created_at,
                   COUNT(c.id) AS chunk_count
            FROM rag_documents d
            LEFT JOIN rag_chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.created_at DESC
            """
        )
    ).mappings().all()
    return {"documents": [dict(row) for row in rows]}


@router.post("/admin/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(..., min_length=1, max_length=500),
    source: str = Form(..., min_length=1, max_length=1000),
    url: Optional[str] = Form(default=None, max_length=2000),
    destination: Optional[str] = Form(default=None, max_length=200),
    country: Optional[str] = Form(default=None, max_length=200),
    category: Optional[str] = Form(default=None, max_length=200),
    document_type: Optional[str] = Form(default=None, max_length=100),
    publication_date: Optional[str] = Form(default=None),
    update_date: Optional[str] = Form(default=None),
    admin: User = Depends(require_rag_admin),
    db: Session = Depends(get_db),
):
    del admin
    filename = Path(file.filename or "").name
    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Upload a PDF, TXT, Markdown, or HTML document.")
    content = await file.read(MAX_DOCUMENT_BYTES + 1)
    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Knowledge documents must be 20 MB or smaller.")
    url = _optional_text(url)
    if url and urlparse(url).scheme not in {"http", "https"}:
        raise HTTPException(status_code=422, detail="Document URL must use HTTP or HTTPS.")
    metadata = DocumentMetadata(
        title=title,
        source=source,
        url=url,
        destination=_optional_text(destination),
        country=_optional_text(country),
        category=_optional_text(category),
        document_type=_optional_text(document_type),
        publication_date=_parse_date(publication_date, "publication_date"),
        update_date=_parse_date(update_date, "update_date"),
    )
    try:
        result = await ingest_document(db, filename, content, metadata)
    except (RagStorageUnavailable,):
        raise HTTPException(status_code=503, detail="RAG ingestion requires PostgreSQL with pgvector.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Knowledge document ingestion failed.")
        raise HTTPException(status_code=502, detail="Document ingestion failed; check embedding provider and database logs.") from exc
    return result


@router.delete("/admin/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    admin: User = Depends(require_rag_admin),
    db: Session = Depends(get_db),
):
    del admin
    if db.get_bind().dialect.name != "postgresql":
        raise HTTPException(status_code=503, detail="RAG administration requires PostgreSQL with pgvector.")
    result = db.execute(text("DELETE FROM rag_documents WHERE id = :id"), {"id": document_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Knowledge document not found.")
