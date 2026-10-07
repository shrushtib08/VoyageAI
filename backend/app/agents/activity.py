import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class ActivityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ActivityAgent",
            role="Experience & Activities Curator",
            description="Sources and prioritizes experiential travel activities, immersive cultural workshops, nature excursions, and scenic spots tailored strictly to traveler passions."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination", "Tokyo")
        interests = context.get("interests", ["culture", "photography", "nature"])
        currency = context.get("currency", "INR")
        travel_style = context.get("travel_style", "balanced")
        duration_days = context.get("duration_days", 7)

        activity_data = await self.curate_activities(destination, interests, currency, travel_style, duration_days)

        sources = [
            {
                "agent_name": self.name,
                "title": f"Cultural Activities & Experiences Guide - {destination}",
                "url": f"https://www.getyourguide.com/s/?q={destination.replace(' ', '+')}",
                "snippet": f"Curated local tours, architectural walking trails, and cultural experiences in {destination}."
            }
        ]

        return {
            "ranked_activities": activity_data.get("ranked_activities", []),
            "source_citations": sources,
        }

    async def curate_activities(
        self,
        destination: str,
        interests: List[str],
        currency: str,
        travel_style: str,
        duration_days: int
    ) -> Dict[str, Any]:
        """Queries LLM for ranked personalized activities."""
        if llm_service.is_available():
            system_prompt = (
                "You are an Activity & Experience Curation Agent. Curate 5-8 realistic, highly engaging activities "
                "ranked in order of relevance to the user's explicit interests. "
                "Include realistic durations and costs. Return JSON ONLY."
            )
            prompt = (
                f"Destination: {destination}\n"
                f"Traveler Interests: {', '.join(interests)}\n"
                f"Travel Style: {travel_style}\n"
                f"Trip Duration: {duration_days} days\n"
                f"Currency: {currency}\n"
                "Return JSON with:\n"
                "- ranked_activities: list of {\n"
                "    rank (int starting at 1),\n"
                "    title (string),\n"
                "    category (string matching interests like Photography, Nature, Culture, Adventure),\n"
                "    description (vivid 1-2 sentence description),\n"
                "    estimated_duration_hours (float),\n"
                "    estimated_cost (float in " + currency + "),\n"
                "    best_time_of_day (string e.g. 'Morning', 'Golden Hour Afternoon', 'Evening'),\n"
                "    source (string, e.g. 'Local Heritage Council')\n"
                "  }\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                return data
            except Exception as e:
                logger.warning(f"Activity LLM curation failed: {e}")

        # Deterministic fallback
        return {
            "ranked_activities": [
                {
                    "rank": 1,
                    "title": f"Golden Hour Architectural & Photography Walking Tour",
                    "category": "Photography & Architecture",
                    "description": f"Capture majestic viewpoints, heritage timber facades, and panoramic vantage points across {destination}.",
                    "estimated_duration_hours": 3.0,
                    "estimated_cost": 1500.0 if currency == "INR" else 20.0,
                    "best_time_of_day": "Afternoon to Sunset",
                    "source": "Photographic Society Field Guide"
                },
                {
                    "rank": 2,
                    "title": "Ancient Tea & Cultural Craft Immersion",
                    "category": "Culture & Heritage",
                    "description": "Engage in an authentic hands-on masterclass led by resident artisanal masters.",
                    "estimated_duration_hours": 2.0,
                    "estimated_cost": 2500.0 if currency == "INR" else 35.0,
                    "best_time_of_day": "Morning",
                    "source": "Cultural Heritage Workshop Series"
                },
                {
                    "rank": 3,
                    "title": "Scenic Mountain Ridge or River Sanctuary Excursion",
                    "category": "Nature & Landscapes",
                    "description": "Hike tranquil forest trails adorned with native flora, stone shrines, and rushing watercourses.",
                    "estimated_duration_hours": 4.5,
                    "estimated_cost": 800.0 if currency == "INR" else 10.0,
                    "best_time_of_day": "Early Morning",
                    "source": "National Park & Trail Bureau"
                }
            ]
        }
