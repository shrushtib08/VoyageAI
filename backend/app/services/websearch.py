import logging
import httpx
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class WebSearchService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.endpoint = "https://api.tavily.com/search"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Queries Tavily Web Search API. Returns list of sources with title, url, snippet."""
        if not self.is_configured():
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    self.endpoint,
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": max_results,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for item in data.get("results", []):
                        results.append({
                            "title": item.get("title", "Web Source"),
                            "url": item.get("url", ""),
                            "snippet": item.get("content", "")[:350],
                        })
                    return results
                else:
                    logger.warning(f"Tavily search returned status code {resp.status_code}")
                    return []
        except Exception as e:
            logger.warning(f"Tavily search exception: {e}")
            return []


web_search_service = WebSearchService()
