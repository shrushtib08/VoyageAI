import hashlib
import logging
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import engine
from app.rag.chunking import chunk_text
from app.rag.embeddings import embedding_service

logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".html", ".htm"}


class RagStorageUnavailable(RuntimeError):
    """Raised if RAG is used without PostgreSQL and the pgvector extension."""


@dataclass(frozen=True)
class DocumentMetadata:
    title: str
    source: str
    url: Optional[str] = None
    destination: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    document_type: Optional[str] = None
    publication_date: Optional[date] = None
    update_date: Optional[date] = None


class _HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self.parts = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        elif tag.lower() in {"p", "br", "div", "li", "h1", "h2", "h3", "section"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif tag.lower() in {"p", "div", "li", "h1", "h2", "h3", "section"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def extract_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Supported document formats are PDF, TXT, Markdown, and HTML.")
    if extension == ".pdf":
        try:
            from pypdf import PdfReader
            from io import BytesIO

            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            logger.exception("Unable to extract text from uploaded PDF.")
            raise ValueError("The PDF could not be read or contains no extractable text.") from exc

    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Text, Markdown, and HTML documents must use UTF-8 encoding.") from exc
    if extension in {".html", ".htm"}:
        parser = _HtmlTextExtractor()
        parser.feed(decoded)
        return "".join(parser.parts)
    return decoded


def initialize_schema(db: Session) -> bool:
    if db.get_bind().dialect.name != "postgresql":
        logger.info("RAG storage is disabled: DATABASE_URL is not PostgreSQL.")
        return False

    dimensions = settings.EMBEDDING_DIMENSIONS
    if dimensions <= 0:
        raise ValueError("EMBEDDING_DIMENSIONS must be greater than zero.")
    statements = [
        "CREATE EXTENSION IF NOT EXISTS vector",
        """
        CREATE TABLE IF NOT EXISTS rag_documents (
            id BIGSERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT UNIQUE,
            destination TEXT,
            country TEXT,
            category TEXT,
            document_type TEXT,
            publication_date DATE,
            update_date DATE,
            content_hash CHAR(64) NOT NULL UNIQUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS rag_chunks (
            id BIGSERIAL PRIMARY KEY,
            document_id BIGINT NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding VECTOR({dimensions}) NOT NULL,
            UNIQUE (document_id, chunk_index)
        )
        """,
        "CREATE INDEX IF NOT EXISTS ix_rag_chunks_document_id ON rag_chunks (document_id)",
        "CREATE INDEX IF NOT EXISTS ix_rag_chunks_embedding ON rag_chunks USING hnsw (embedding vector_cosine_ops)",
        "CREATE INDEX IF NOT EXISTS ix_rag_documents_destination ON rag_documents (destination)",
        "CREATE INDEX IF NOT EXISTS ix_rag_documents_country ON rag_documents (country)",
    ]
    try:
        for statement in statements:
            db.execute(text(statement))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Unable to initialize PostgreSQL pgvector schema.")
        raise
    return True


async def ingest_document(
    db: Session,
    filename: str,
    content: bytes,
    metadata: DocumentMetadata,
) -> Dict[str, Any]:
    if db.get_bind().dialect.name != "postgresql":
        raise RagStorageUnavailable("RAG ingestion requires PostgreSQL with the pgvector extension.")
    if not metadata.title.strip() or not metadata.source.strip():
        raise ValueError("Document title and source are required.")
    if metadata.url:
        duplicate = db.execute(
            text("SELECT id FROM rag_documents WHERE url = :url"),
            {"url": metadata.url},
        ).first()
        if duplicate:
            return {"document_id": duplicate.id, "duplicate": True, "chunk_count": 0}

    plain_text = extract_text(filename, content).strip()
    if not plain_text:
        raise ValueError("The document contains no extractable text.")
    digest = hashlib.sha256(content).hexdigest()
    duplicate = db.execute(
        text("SELECT id FROM rag_documents WHERE content_hash = :digest"),
        {"digest": digest},
    ).first()
    if duplicate:
        return {"document_id": duplicate.id, "duplicate": True, "chunk_count": 0}

    chunks = chunk_text(plain_text)
    vectors = await embedding_service.embed(chunks)
    result = db.execute(
        text(
            """
            INSERT INTO rag_documents
                (title, source, url, destination, country, category, document_type,
                 publication_date, update_date, content_hash)
            VALUES
                (:title, :source, :url, :destination, :country, :category, :document_type,
                 :publication_date, :update_date, :content_hash)
            RETURNING id
            """
        ),
        {
            "title": metadata.title.strip(),
            "source": metadata.source.strip(),
            "url": metadata.url,
            "destination": metadata.destination,
            "country": metadata.country,
            "category": metadata.category,
            "document_type": metadata.document_type or Path(filename).suffix.lower().lstrip("."),
            "publication_date": metadata.publication_date,
            "update_date": metadata.update_date,
            "content_hash": digest,
        },
    )
    document_id = result.scalar_one()
    try:
        for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
            vector_literal = "[" + ",".join(str(value) for value in vector) + "]"
            db.execute(
                text(
                    """
                    INSERT INTO rag_chunks (document_id, chunk_index, content, embedding)
                    VALUES (:document_id, :chunk_index, :content, CAST(:embedding AS vector))
                    """
                ),
                {
                    "document_id": document_id,
                    "chunk_index": index,
                    "content": chunk,
                    "embedding": vector_literal,
                },
            )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist document chunks and embeddings.")
        raise
    return {"document_id": document_id, "duplicate": False, "chunk_count": len(chunks)}
