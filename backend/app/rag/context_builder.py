from typing import Any, Dict, List, Tuple


def build_context(results: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    blocks = []
    sources = []
    for result in results:
        source = {
            "source_type": "RAG KNOWLEDGE",
            "chunk_id": result["chunk_id"],
            "document_id": result["document_id"],
            "title": result["title"],
            "source": result["source"],
            "url": result.get("url"),
            "destination": result.get("destination"),
            "country": result.get("country"),
            "category": result.get("category"),
            "document_type": result.get("document_type"),
            "publication_date": str(result["publication_date"]) if result.get("publication_date") else None,
            "update_date": str(result["update_date"]) if result.get("update_date") else None,
            "similarity": float(result["similarity"]),
        }
        sources.append(source)
        blocks.append(
            f"[{len(sources)}] {source['title']} | {source['source']} "
            f"(chunk {source['chunk_id']})\n{result['content']}"
        )
    return "\n\n".join(blocks), sources
