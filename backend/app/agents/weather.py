import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.weather import weather_service
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="WeatherAgent",
            role="Meteorological & Seasonal Climate Analyst",
            description="Analyzes atmospheric conditions, temperature variations, precipitation probabilities, and derives customized wardrobe and gear packing guidance."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination", "Tokyo")
        travel_dates = context.get("start_date", "Upcoming")

        # 1. Check live OpenWeather API
        api_result = await weather_service.get_destination_weather(destination)
        is_live = api_result.get("is_live_forecast", False)
        live_data = api_result.get("data")
        api_note = api_result.get("api_status_note")

        # 2. Derive seasonal analysis and packing advice
        weather_intel = await self.analyze_climate(destination, travel_dates, live_data)

        return {
            "destination": destination,
            "season_summary": weather_intel.get("season_summary", f"Typical seasonal climate in {destination} during {travel_dates}."),
            "avg_temp_min": live_data.get("temp_min") if live_data else weather_intel.get("avg_temp_min", 12.0),
            "avg_temp_max": live_data.get("temp_max") if live_data else weather_intel.get("avg_temp_max", 22.0),
            "precipitation_probability": weather_intel.get("precipitation_probability", 20.0),
            "weather_conditions": (live_data.get("conditions") if live_data else None) or weather_intel.get("weather_conditions", "Mild and clear"),
            "travel_advice": weather_intel.get("travel_advice", "Comfortable walking shoes and lightweight layers recommended."),
            "packing_suggestions": weather_intel.get("packing_suggestions", [
                "Breathable layers (cardigans, thermals for evenings)",
                "Comfortable walking shoes with arch support",
                "Compact travel umbrella or rain shell",
                "Universal travel power adapter with surge protection"
            ]),
            "is_live_forecast": is_live,
            "api_status_note": api_note if not is_live else "Live weather readings active from OpenWeather.",
        }

    async def analyze_climate(self, destination: str, travel_dates: str, live_data: Any) -> Dict[str, Any]:
        """Queries LLM for accurate seasonal climate norms and tailored packing list."""
        if llm_service.is_available():
            system_prompt = (
                "You are a Meteorological & Climate Travel Agent. Provide realistic historical temperatures, "
                "rain probabilities, seasonal conditions, and tailored packing advice. DO NOT fabricate false forecasts. Return JSON ONLY."
            )
            prompt = (
                f"Destination: {destination}\n"
                f"Travel Season / Timing: {travel_dates}\n"
                f"Live data (if any): {live_data}\n"
                "Return JSON with:\n"
                "- season_summary (concise explanation of seasonal weather trends)\n"
                "- avg_temp_min (float in Celsius)\n"
                "- avg_temp_max (float in Celsius)\n"
                "- precipitation_probability (float percentage between 0 and 100)\n"
                "- weather_conditions (string summary, e.g. 'Crisp, sunny days with cool evenings')\n"
                "- travel_advice (actionable travel weather advice)\n"
                "- packing_suggestions (list of 5-7 specific items tailored to this destination and season)\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                return data
            except Exception as e:
                logger.warning(f"Weather LLM analysis failed: {e}")

        # Deterministic seasonal fallback
        return {
            "season_summary": f"Temperate conditions typical for {travel_dates} in {destination}.",
            "avg_temp_min": 10.0,
            "avg_temp_max": 20.0,
            "precipitation_probability": 25.0,
            "weather_conditions": "Partly cloudy with pleasant daytime walking conditions",
            "travel_advice": "Mornings and evenings can be brisk; layer appropriately to adapt comfortably throughout the day.",
            "packing_suggestions": [
                "Versatile layering garments (jackets, light sweaters)",
                "Supportive walking footwear for extensive sightseeing",
                "Compact windproof umbrella",
                "High-capacity power bank for mobile mapping and photos",
                "Moisturizer / lip balm for climate transition"
            ]
        }
