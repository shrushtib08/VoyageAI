import logging
from typing import List, Sequence

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingError(RuntimeError):
    """Raised when an embedding provider is unavailable or returns invalid data."""


class EmbeddingService:
    def __init__(self) -> None:
        self.endpoint = settings.EMBEDDING_API_BASE_URL
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.api_key = settings.EMBEDDING_API_KEY

    def is_configured(self) -> bool:
        return bool(self.api_key.strip() and self.endpoint.strip() and self.model.strip())

    async def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []
        if not self.is_configured():
            raise EmbeddingError("RAG embeddings are unavailable: configure EMBEDDING_API_KEY.")
        if self.dimensions <= 0:
            raise EmbeddingError("EMBEDDING_DIMENSIONS must be greater than zero.")

        headers = {"Authorization": f"Bearer {self.api_key.strip()}"}
        vectors: List[List[float]] = []
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                for offset in range(0, len(texts), 64):
                    payload = {
                        "model": self.model,
                        "input": list(texts[offset:offset + 64]),
                        "dimensions": self.dimensions,
                    }
                    response = await client.post(self.endpoint, headers=headers, json=payload)
                    response.raise_for_status()
                    items = sorted(response.json()["data"], key=lambda item: item["index"])
                    vectors.extend(item["embedding"] for item in items)
        except httpx.HTTPError as exc:
            logger.exception("Embedding provider request failed.")
            raise EmbeddingError("The configured embedding provider request failed.") from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise EmbeddingError("The embedding provider returned an invalid response.") from exc
        if len(vectors) != len(texts) or any(
            len(vector) != self.dimensions or not all(isinstance(value, (int, float)) for value in vector)
            for vector in vectors
        ):
            raise EmbeddingError(
                f"The embedding provider must return {len(texts)} vectors of {self.dimensions} dimensions."
            )
        return [[float(value) for value in vector] for vector in vectors]


embedding_service = EmbeddingService()
