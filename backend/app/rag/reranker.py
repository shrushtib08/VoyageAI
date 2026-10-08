import re
from typing import Any, Dict, List


def rerank_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    query_terms = set(re.findall(r"\w+", query.casefold()))
    if not query_terms:
        return results

    for result in results:
        content_terms = set(re.findall(r"\w+", result.get("content", "").casefold()))
        lexical_score = len(query_terms & content_terms) / len(query_terms)
        semantic_score = float(result.get("similarity", 0.0))
        result["lexical_score"] = lexical_score
        result["rerank_score"] = semantic_score * 0.85 + lexical_score * 0.15
    return sorted(results, key=lambda item: item["rerank_score"], reverse=True)
