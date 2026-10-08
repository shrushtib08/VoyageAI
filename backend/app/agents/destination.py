import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.websearch import web_search_service
from app.services.llm import llm_service
from app.rag.rag_service import rag_service

logger = logging.getLogger(__name__)


class DestinationResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DestinationAgent",
            role="Destination & Cultural Research Specialist",
            description="Investigates top landmarks, authentic cultural monuments, hidden local gems, distinctive neighborhoods, and essential local navigation logistics."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination", "Japan")
        multi_cities = context.get("multi_cities", [destination])
        interests = context.get("interests", ["culture", "photography", "nature"])
        knowledge = await rag_service.agent_knowledge(
            query=f"Destination guide, attractions, customs, transport and local tips for {destination}; interests: {', '.join(interests)}",
            destination=destination,
        )

        # 1. Web research via Tavily if available
        web_sources = []
        if web_search_service.is_configured():
            query = f"top attractions hidden gems culture visiting tips {destination}"
            raw_sources = await web_search_service.search(query, max_results=3)
            for s in raw_sources:
                web_sources.append({
                    "agent_name": self.name,
                    "title": s.get("title", f"Destination Guide: {destination}"),
                    "url": s.get("url"),
                    "snippet": s.get("snippet"),
                    "source_type": "WEB RESEARCH",
                })

        # 2. Extract structured destination highlights
        dest_data = await self.research_destination(
            destination, multi_cities, interests, web_sources, knowledge["context"]
        )

        all_sources = web_sources + [
            {"agent_name": self.name, **source} for source in knowledge["sources"]
        ]

        return {
            "major_attractions": dest_data.get("major_attractions", []),
            "cultural_sites": dest_data.get("cultural_sites", []),
            "lesser_known_gems": dest_data.get("lesser_known_gems", []),
            "neighborhoods": dest_data.get("neighborhoods", []),
            "local_tips": dest_data.get("local_tips", []),
            "practical_info": dest_data.get("practical_info", {}),
            "source_citations": all_sources,
        }

    async def research_destination(
        self,
        destination: str,
        multi_cities: List[str],
        interests: List[str],
        web_sources: List[Dict[str, Any]],
        rag_context: str = "",
    ) -> Dict[str, Any]:
        """Queries LLM for curated landmark and district data."""
        if llm_service.is_available():
            system_prompt = (
                "You are an expert Destination Research Agent for VoyageAI. Provide accurate landmarks, cultural monuments, "
                "hidden gems, and distinct neighborhoods for the requested location. "
                "Include approximate visiting times in hours. Return JSON ONLY."
            )
            sources_summary = "\n".join([f"- {s.get('title')}: {s.get('snippet')}" for s in web_sources])
            prompt = (
                f"Destination: {destination} (Cities: {', '.join(multi_cities)})\n"
                f"User Interests: {', '.join(interests)}\n"
                f"Context from research:\n{sources_summary}\n"
                f"RAG KNOWLEDGE (stable reference material):\n{rag_context}\n"
                "Return JSON with:\n"
                "- major_attractions: list of {name, category, description, approx_visit_time_hours, opening_hours, tips, source}\n"
                "- cultural_sites: list of {name, category, description, approx_visit_time_hours, tips, source}\n"
                "- lesser_known_gems: list of {name, category, description, approx_visit_time_hours, tips, source}\n"
                "- neighborhoods: list of {name, vibe, highlights}\n"
                "- local_tips: list of 4-6 concise practical cultural tips (etiquette, transit passes, currency exchange)\n"
                "- practical_info: object with {transit_pass_recommendation, sim_card_advice, emergency_number, best_way_to_commute}\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                return data
            except Exception as e:
                logger.warning(f"Destination LLM research failed: {e}")

        # Deterministic fallback
        return {
            "major_attractions": [
                {
                    "name": f"Historic Central Landmark of {destination}",
                    "category": "Landmark & Sightseeing",
                    "description": f"The iconic cultural landmark defining the skyline and history of {destination}.",
                    "approx_visit_time_hours": 2.5,
                    "opening_hours": "09:00 - 17:00",
                    "tips": "Visit early in the morning for fewer crowds and best lighting.",
                    "source": "Official Tourism Bureau"
                },
                {
                    "name": f"{destination} National Museum & Gardens",
                    "category": "Culture & Heritage",
                    "description": "Expansive exhibits showcasing local art, ancient artifacts, and tranquil gardens.",
                    "approx_visit_time_hours": 3.0,
                    "opening_hours": "09:30 - 18:00",
                    "tips": "Book entry tickets online in advance to skip the main queue.",
                    "source": "Museum Council"
                }
            ],
            "cultural_sites": [
                {
                    "name": f"Ancient Temple & Shrine Quarter",
                    "category": "Spiritual & Architectural Heritage",
                    "description": "Centuries-old stone paths lined with sacred architecture, incense pavilions, and traditional courtyards.",
                    "approx_visit_time_hours": 2.0,
                    "tips": "Dress respectfully covering shoulders and knees.",
                    "source": "Heritage Trust"
                }
            ],
            "lesser_known_gems": [
                {
                    "name": "Artisanal Waterfront Promenade",
                    "category": "Hidden Gem & Scenic Viewpoint",
                    "description": "A tranquil local riverside pathway lined with independent coffee roasters and artisan workshops.",
                    "approx_visit_time_hours": 1.5,
                    "tips": "Sunset offers the most breathtaking photographic vantage point.",
                    "source": "Local Explorer Journal"
                }
            ],
            "neighborhoods": [
                {"name": "Old Town Quarter", "vibe": "Historic, pedestrian-friendly, timeless", "highlights": "Cobblestone alleys, heritage cafes"},
                {"name": "Modern District", "vibe": "Energetic, luminous, modern", "highlights": "High-tech transit, architecture, shopping"}
            ],
            "local_tips": [
                "Acquire a reloadable IC/transit card upon arrival at the central station.",
                "Tipping is not customary in many local establishments; respectful appreciation is preferred.",
                "Carry a small portable coin purse and battery pack for day-long exploration."
            ],
            "practical_info": {
                "transit_pass_recommendation": "All-access Metro 72-hour tourist pass",
                "sim_card_advice": "eSIM activation at airport terminal or prior to departure",
                "emergency_number": "112 / 110",
                "best_way_to_commute": "Subway / Train network"
            }
        }
