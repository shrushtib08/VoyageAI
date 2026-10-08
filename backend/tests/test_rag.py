from datetime import datetime, timezone
from io import BytesIO

import pytest
from reportlab.pdfgen import canvas

from app.rag.chunking import chunk_text
from app.rag.context_builder import build_context
from app.rag.ingestion import extract_text
from app.rag.rag_service import RagService
from app.rag.reranker import rerank_results
from app.rag.retriever import RagRetriever, build_filter_clause
from app.schemas.chat import ChatMessageResponse


def test_chunking_cleans_text_and_keeps_overlap():
    chunks = chunk_text("  Kyoto   customs\n\nRespect shrine rules.  ", chunk_size=24, overlap=5)

    assert len(chunks) >= 2
    assert all(chunk == chunk.strip() for chunk in chunks)
    assert "Kyoto customs" in chunks[0]
    assert set(chunks[0][-5:]) & set(chunks[1][:5])


def test_html_extraction_ignores_scripts_and_styles():
    extracted = extract_text(
        "guide.html",
        b"<h1>Kyoto</h1><script>secret()</script><p>Use local transit.</p>",
    )

    assert "Kyoto" in extracted
    assert "Use local transit." in extracted
    assert "secret" not in extracted


def test_pdf_extraction_reads_text():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 720, "Kyoto travel guide")
    pdf.save()

    assert "Kyoto travel guide" in extract_text("guide.pdf", buffer.getvalue())


def test_destination_filtering_is_parameterized_and_restricted():
    where, params = build_filter_clause({"destination": "Kyoto", "country": "Japan"})

    assert "LOWER(d.destination) = LOWER(:destination)" in where
    assert "LOWER(d.country) = LOWER(:country)" in where
    assert params == {"destination": "Kyoto", "country": "Japan"}
    with pytest.raises(ValueError):
        build_filter_clause({"title": "Kyoto"})


def test_semantic_candidates_are_reranked_by_query_terms():
    results = rerank_results(
        "Kyoto winter clothing",
        [
            {"content": "Kyoto temples and local etiquette", "similarity": 0.95},
            {"content": "Kyoto winter clothing layers and rain", "similarity": 0.90},
        ],
    )

    assert "winter clothing" in results[0]["content"]
    assert results[0]["rerank_score"] > results[1]["rerank_score"]


@pytest.mark.asyncio
async def test_retriever_applies_destination_and_similarity_filters(monkeypatch):
    class FakeResult:
        def mappings(self):
            return self

        def all(self):
            return [
                {"chunk_id": 1, "content": "Kyoto winter guide", "similarity": 0.88},
                {"chunk_id": 2, "content": "Unrelated result", "similarity": 0.10},
            ]

    class FakeDialect:
        name = "postgresql"

    class FakeBind:
        dialect = FakeDialect()

    class FakeSession:
        def get_bind(self):
            return FakeBind()

        def execute(self, statement, params):
            assert "LOWER(d.destination) = LOWER(:destination)" in str(statement)
            assert params["destination"] == "Kyoto"
            return FakeResult()

    async def embed_query(texts):
        return [[0.1, 0.2, 0.3]]

    monkeypatch.setattr("app.rag.retriever.embedding_service.embed", embed_query)
    results = await RagRetriever().search(
        "Kyoto winter",
        filters={"destination": "Kyoto"},
        db=FakeSession(),
    )

    assert [result["chunk_id"] for result in results] == [1]
    assert results[0]["similarity"] == 0.88


def test_context_construction_retains_citation_metadata():
    context, sources = build_context(
        [
            {
                "chunk_id": 12,
                "document_id": 3,
                "title": "Kyoto Seasonal Guide",
                "source": "Local Tourism Office",
                "url": "https://example.test/kyoto",
                "destination": "Kyoto",
                "country": "Japan",
                "category": "seasonal",
                "document_type": "guide",
                "publication_date": None,
                "update_date": None,
                "similarity": 0.83,
                "content": "December is cold; wear layers.",
            }
        ]
    )

    assert "December is cold" in context
    assert sources[0]["source_type"] == "RAG KNOWLEDGE"
    assert sources[0]["chunk_id"] == 12
    assert sources[0]["url"] == "https://example.test/kyoto"


def test_chat_response_exposes_persisted_source_metadata():
    response = ChatMessageResponse(
        id=1,
        conversation_id=2,
        sender="assistant",
        content="Wear layers [1].",
        actions_taken={
            "sources": [{"source_type": "RAG KNOWLEDGE", "title": "Kyoto guide", "chunk_id": 12}]
        },
        created_at=datetime.now(timezone.utc),
    )

    assert response.model_dump()["sources"][0]["chunk_id"] == 12


@pytest.mark.asyncio
async def test_no_relevant_results_abstains_instead_of_inventing(monkeypatch):
    service = RagService()
    monkeypatch.setattr("app.rag.rag_service.embedding_service.is_configured", lambda: True)
    monkeypatch.setattr(service, "retrieve", _empty_results)
    monkeypatch.setattr("app.rag.rag_service.web_search_service.search", _empty_web_results)

    answer = await service.answer("What should I wear tomorrow?")

    assert answer["sources"] == []
    assert answer["grounded"] is False
    assert "couldn't find sufficient" in answer["answer"]


async def _empty_results(*args, **kwargs):
    return []


async def _empty_web_results(*args, **kwargs):
    return []
