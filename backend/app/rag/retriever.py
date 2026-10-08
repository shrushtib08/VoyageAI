import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import SessionLocal
from app.rag.embeddings import embedding_service
from app.rag.ingestion import RagStorageUnavailable
from app.rag.reranker import rerank_results

logger = logging.getLogger(__name__)
ALLOWED_FILTERS = {"destination", "country", "category", "document_type"}


def build_filter_clause(filters: Optional[Dict[str, Optional[str]]]) -> tuple[str, Dict[str, str]]:
    clauses = []
    params: Dict[str, str] = {}
    for key, value in (filters or {}).items():
        if key not in ALLOWED_FILTERS:
            raise ValueError(f"Unsupported RAG metadata filter: {key}")
        if value:
            clauses.append(f"LOWER(d.{key}) = LOWER(:{key})")
            params[key] = value.strip()
    return (" AND ".join(clauses), params)


class RagRetriever:
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Optional[str]]] = None,
        top_k: int = 5,
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        if not query.strip():
            raise ValueError("Search query cannot be empty.")
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20.")

        owns_session = db is None
        session = db or SessionLocal()
        try:
            if session.get_bind().dialect.name != "postgresql":
                raise RagStorageUnavailable("RAG retrieval requires PostgreSQL with pgvector.")
            vector = (await embedding_service.embed([query]))[0]
            vector_literal = "[" + ",".join(str(value) for value in vector) + "]"
            filter_sql, filter_params = build_filter_clause(filters)
            where_sql = f"WHERE {filter_sql}" if filter_sql else ""
            params: Dict[str, Any] = {
                "embedding": vector_literal,
                "top_k": top_k,
                "min_similarity": 0.15,
                **filter_params,
            }
            rows = session.execute(
                text(
                    f"""
                    SELECT c.id AS chunk_id, c.content, d.id AS document_id, d.title,
                           d.source, d.url, d.destination, d.country, d.category,
                           d.document_type, d.publication_date, d.update_date,
                           1 - (c.embedding <=> CAST(:embedding AS vector)) AS similarity
                    FROM rag_chunks c
                    JOIN rag_documents d ON d.id = c.document_id
                    {where_sql}
                    ORDER BY c.embedding <=> CAST(:embedding AS vector)
                    LIMIT :top_k
                    """
                ),
                params,
            ).mappings().all()
            results = [dict(row) for row in rows]
            results = [
                result for result in results
                if float(result["similarity"]) >= params["min_similarity"]
            ]
            return rerank_results(query, results)
        except RagStorageUnavailable:
            raise
        except Exception:
            logger.exception("RAG vector retrieval failed.")
            raise
        finally:
            if owns_session:
                session.close()


rag_retriever = RagRetriever()
