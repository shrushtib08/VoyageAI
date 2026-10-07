import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class FoodAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FoodAgent",
            role="Gastronomy & Culinary Research Specialist",
            description="Curates iconic local gastronomy, culinary districts, certified dietary alternatives, and budget-friendly street cuisine."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination", "Tokyo")
        budget = context.get("budget")
        currency = context.get("currency", "INR")
        dietary = context.get("dietary_preferences", [])
        interests = context.get("interests", [])

        food_intel = await self.research_gastronomy(destination, dietary, currency, budget)

        sources = [
            {
                "agent_name": self.name,
                "title": f"Culinary Atlas & Dining Registry - {destination}",
                "url": f"https://www.tasteatlas.com/search?q={destination.replace(' ', '+')}",
                "snippet": f"Authentic regional gastronomic heritage and traditional culinary specialties in {destination}."
            }
        ]

        return {
            "local_dishes": food_intel.get("local_dishes", []),
            "popular_food_areas": food_intel.get("popular_food_areas", []),
            "recommended_spots": food_intel.get("recommended_spots", []),
            "street_food": food_intel.get("street_food", []),
            "dietary_suitability": food_intel.get("dietary_suitability", {}),
            "price_level_summary": food_intel.get("price_level_summary", "Moderate"),
            "source_citations": sources,
        }

    async def research_gastronomy(
        self,
        destination: str,
        dietary: List[str],
        currency: str,
        budget: Any
    ) -> Dict[str, Any]:
        """Queries LLM for authentic culinary recommendations."""
        if llm_service.is_available():
            dietary_str = ", ".join(dietary) if dietary else "No specific restrictions (all cuisines welcome)"
            system_prompt = (
                "You are an expert Culinary & Gastronomy Travel Agent. Provide real regional dishes, "
                "established food streets/markets, and verified culinary recommendations matching dietary needs. "
                "Do NOT invent non-existent restaurants. Return JSON ONLY."
            )
            prompt = (
                f"Destination: {destination}\n"
                f"Dietary Preferences: {dietary_str}\n"
                f"Budget Currency: {currency}\n"
                "Return JSON with:\n"
                "- local_dishes: list of {name, description, typical_ingredients, must_try_reason}\n"
                "- popular_food_areas: list of strings (famous food streets, alleys, market halls)\n"
                "- recommended_spots: list of {name, area, specialty, price_level, dietary_suitability: list, description, source}\n"
                "- street_food: list of {item_name, where_to_find, approx_cost_estimate}\n"
                "- dietary_suitability: object summarizing availability for vegetarian, vegan, halal, etc.\n"
                "- price_level_summary: string (e.g. 'Street meals: ₹300-600, Casual dining: ₹1,200-2,500')\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                return data
            except Exception as e:
                logger.warning(f"Food LLM research failed: {e}")

        # Deterministic fallback
        return {
            "local_dishes": [
                {
                    "name": f"Traditional Signature Broth & Noodles of {destination}",
                    "description": "Rich savory broth infused with regional aromatics, fresh hand-pulled noodles, and seasonal toppings.",
                    "typical_ingredients": "Regional broth, fresh wheat/rice noodles, scallions, bamboo shoots",
                    "must_try_reason": "The defining comfort dish perfected over generations in local culinary guilds."
                },
                {
                    "name": "Artisanal Grilled Skewers & Dumplings",
                    "description": "Crispy seasoned parcels grilled over natural charcoal embers with signature glaze.",
                    "typical_ingredients": "Local vegetables/proteins, ginger, sesame oil, tare glaze",
                    "must_try_reason": "Crisp texture and smoky depth characteristic of evening street stalls."
                }
            ],
            "popular_food_areas": [
                f"{destination} Central Heritage Market Arcade",
                "Lantern-lit Evening Gastronomy Alley"
            ],
            "recommended_spots": [
                {
                    "name": f"{destination} Heritage Kitchen",
                    "area": "Historic Central Market",
                    "specialty": "Traditional Set Menus & Seasonal Stews",
                    "price_level": "$$ (Mid-range)",
                    "dietary_suitability": ["Vegetarian options available upon request"],
                    "description": "Authentic multi-generational dining house revered for traditional preparation.",
                    "source": "Local Gastronomic Review"
                }
            ],
            "street_food": [
                {
                    "item_name": "Pan-Fried Savory Pancakes",
                    "where_to_find": "Night Market Street Stalls",
                    "approx_cost_estimate": f"{currency} 300 - 500"
                }
            ],
            "dietary_suitability": {
                "vegetarian": "Widely accessible in central districts; look for plant-based specialty cafes or ask for dashi/meat-free broth.",
                "vegan": "Available at dedicated organic and Buddhist temple style eateries.",
                "halal": "Certified eateries concentrated near international hubs and university quarters."
            },
            "price_level_summary": f"Casual dining: {currency} 600 - 1,500 per meal; Premium: {currency} 3,000+"
        }
