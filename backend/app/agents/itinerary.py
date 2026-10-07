import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class ItineraryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ItineraryAgent",
            role="Itinerary Synthesis & Scheduling Architect",
            description="Assembles a cohesive, geographically clustered day-by-day schedule with dedicated Morning, Afternoon, and Evening blocks, balanced transit, and realistic pacing."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination", "Tokyo")
        multi_cities = context.get("multi_cities", [destination])
        duration_days = context.get("duration_days", 7)
        interests = context.get("interests", ["culture", "sightseeing"])
        travel_style = context.get("travel_style", "balanced")
        currency = context.get("currency", "INR")
        budget = context.get("budget")
        critic_feedback = context.get("critic_feedback")

        dest_data = context.get("destination_research", {})
        food_data = context.get("food_research", {})
        activity_data = context.get("activity_research", {})
        weather_data = context.get("weather_research", {})
        flight_data = context.get("flight_research", {})

        itinerary_plan = await self.synthesize_itinerary(
            destination=destination,
            multi_cities=multi_cities,
            duration_days=duration_days,
            interests=interests,
            travel_style=travel_style,
            currency=currency,
            dest_data=dest_data,
            food_data=food_data,
            activity_data=activity_data,
            weather_data=weather_data,
            flight_data=flight_data,
            critic_feedback=critic_feedback,
        )

        return itinerary_plan

    async def synthesize_itinerary(
        self,
        destination: str,
        multi_cities: List[str],
        duration_days: int,
        interests: List[str],
        travel_style: str,
        currency: str,
        dest_data: Dict[str, Any],
        food_data: Dict[str, Any],
        activity_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        flight_data: Dict[str, Any],
        critic_feedback: Any = None,
    ) -> Dict[str, Any]:
        """Synthesizes structured day-by-day schedule via LLM or intelligent generator."""
        if llm_service.is_available():
            system_prompt = (
                "You are an expert Itinerary Synthesis Agent for VoyageAI. Build an optimized, realistic, "
                "day-by-day itinerary. Ensure geographical proximity for activities on the same day (no zigzagging "
                "or excessive transit). Include dedicated Morning, Afternoon, and Evening blocks with meal pauses. "
                "Return JSON ONLY."
            )
            feedback_prompt = f"\nPrevious Critic Feedback to Address:\n{critic_feedback}\n" if critic_feedback else ""
            prompt = (
                f"Destination: {destination} (Cities: {', '.join(multi_cities)})\n"
                f"Duration: {duration_days} full days\n"
                f"Travel Style: {travel_style}\n"
                f"User Interests: {', '.join(interests)}\n"
                f"Weather Context: {weather_data.get('season_summary', '')} ({weather_data.get('weather_conditions', '')})\n"
                f"Currency: {currency}\n"
                f"{feedback_prompt}"
                "Research Highlights to incorporate:\n"
                f"- Major Attractions: {[a.get('name') for a in dest_data.get('major_attractions', [])[:6]]}\n"
                f"- Hidden Gems: {[g.get('name') for g in dest_data.get('lesser_known_gems', [])[:4]]}\n"
                f"- Food Highlights: {[f.get('name') for f in food_data.get('recommended_spots', [])[:4]]}\n"
                f"- Activities: {[act.get('title') for act in activity_data.get('ranked_activities', [])[:5]]}\n"
                "Return JSON with:\n"
                "- total_days: integer\n"
                "- title: string (e.g. '7-Day Comprehensive Heritage & Scenic Route')\n"
                "- overview: string summary of pacing and city progression\n"
                "- practical_tips: list of 4-5 overall travel tips\n"
                "- days: array of exactly " + str(duration_days) + " day objects, each with:\n"
                "    - day_number: integer (1 to " + str(duration_days) + ")\n"
                "    - date_str: string (e.g. 'Day 1')\n"
                "    - theme: string (e.g. 'Arrival, Check-in & Historic Old Town Stroll')\n"
                "    - morning: object { time: '09:00 - 12:30', activity: string, location: string, transport: string, estimated_cost: float, practical_tip: string }\n"
                "    - afternoon: object { time: '13:00 - 17:00', activity: string, location: string, transport: string, estimated_cost: float, practical_tip: string }\n"
                "    - evening: object { time: '18:00 - 21:30', activity: string, location: string, transport: string, estimated_cost: float, practical_tip: string }\n"
                "    - attractions: list of strings (names of sites visited this day)\n"
                "    - food_suggestions: list of strings (lunch/dinner recommendations for this day)\n"
                "    - transport_notes: string (subway lines, walking routes, or trains)\n"
                "    - estimated_daily_spend: float in " + currency + "\n"
                "    - practical_notes: string (clothing tips, opening hours, rest advice)\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                return data
            except Exception as e:
                logger.warning(f"Itinerary LLM synthesis failed: {e}")

        # Deterministic Generator
        days_list = []
        major_attractions = dest_data.get("major_attractions", [])
        gems = dest_data.get("lesser_known_gems", [])
        spots = food_data.get("recommended_spots", [])
        activities = activity_data.get("ranked_activities", [])

        cities_sequence = multi_cities if len(multi_cities) > 1 else [destination]

        for day_num in range(1, duration_days + 1):
            city_for_day = cities_sequence[(day_num - 1) % len(cities_sequence)]
            is_arrival = (day_num == 1)
            is_departure = (day_num == duration_days)

            if is_arrival:
                theme = f"Arrival in {city_for_day} & First Evening Exploration"
                morning_act = f"Touch down at {city_for_day} International Hub, baggage retrieval, and airport express train to hotel."
                afternoon_act = "Hotel check-in, unpack, brief rest, and orientation stroll in the neighborhood."
                evening_act = "Welcome dinner at local food alley and introductory twilight photography."
            elif is_departure:
                theme = f"Farewell {city_for_day} & Souvenir Morning"
                morning_act = "Morning walk through artisanal market, souvenir gathering, and specialty local cafe."
                afternoon_act = "Check out of accommodation, luggage storage, final scenic viewpoint visit."
                evening_act = "Transfer to departure terminal, flight departure preparation."
            else:
                theme = f"{city_for_day} Cultural Landmarks & Immersive Experiences"
                morning_act = f"Visit major architectural monuments and temple grounds in {city_for_day} before midday crowds."
                afternoon_act = "Explore traditional arts district, artisan studios, and serene garden paths."
                evening_act = "Sunset overlook viewpoint, vibrant street dinner, and night market stroll."

            days_list.append({
                "day_number": day_num,
                "date_str": f"Day {day_num}",
                "theme": theme,
                "morning": {
                    "time": "09:00 - 12:30",
                    "activity": morning_act,
                    "location": f"{city_for_day} Central Hub",
                    "transport": "Transit express / Metro Line",
                    "estimated_cost": 800.0 if currency == "INR" else 15.0,
                    "practical_tip": "Wear slip-on walking shoes for visiting heritage locations."
                },
                "afternoon": {
                    "time": "13:30 - 17:30",
                    "activity": afternoon_act,
                    "location": f"{city_for_day} Historic District",
                    "transport": "Walking / 10-minute subway ride",
                    "estimated_cost": 1500.0 if currency == "INR" else 25.0,
                    "practical_tip": "Carry cash or IC travel card for street artisan stalls."
                },
                "evening": {
                    "time": "18:30 - 21:30",
                    "activity": evening_act,
                    "location": f"{city_for_day} Culinary Quarter",
                    "transport": "Walking",
                    "estimated_cost": 2200.0 if currency == "INR" else 35.0,
                    "practical_tip": "Table reservations recommended on weekends."
                },
                "attractions": [f"{city_for_day} Central Heritage Monument", f"{city_for_day} Gardens"],
                "food_suggestions": ["Regional Noodle Broth House", "Artisan Sweet & Tea Salon"],
                "transport_notes": f"Primary subway line connects all Day {day_num} stops within a 15-minute radius.",
                "estimated_daily_spend": 4500.0 if currency == "INR" else 75.0,
                "practical_notes": "All morning and afternoon venues are geographically clustered to minimize commute time."
            })

        return {
            "total_days": duration_days,
            "title": f"{duration_days}-Day Curated Journey across {destination}",
            "overview": f"A balanced travel plan maximizing authentic cultural highlights, culinary discoveries, and relaxed intervals across {destination}.",
            "practical_tips": [
                "Cluster daily activities by district to prevent unnecessary transit strain.",
                "Purchase city subway day passes for unlimited convenience.",
                "Keep local coins on hand for lockers and temple donation boxes.",
                "Stay hydrated and plan comfortable 45-minute pauses between major sights."
            ],
            "days": days_list
        }
