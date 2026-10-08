import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.aviation import aviation_service
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class FlightAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FlightAgent",
            role="Flight & Aviation Intelligence Specialist",
            description="Researches flight routes, major airline carriers, estimated fare ranges, and travel durations while maintaining strict distinction between live schedules and research estimates."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        origin = context.get("origin") or "Bangalore"
        destination = context.get("destination") or "Japan"
        travellers = context.get("travellers", 1)
        currency = context.get("currency", "INR")
        budget = context.get("budget")

        # 1. Attempt live aviation search if API is configured
        live_result = await aviation_service.search_flights(origin, destination)
        is_live = live_result.get("is_live_data", False)
        api_note = live_result.get("api_status_note")
        live_routes = live_result.get("routes", [])

        # 2. Researched route intelligence using LLM or structured knowledge
        flight_intel = await self.research_flight_routes(origin, destination, currency, travellers)

        sources = [
            {
                "agent_name": self.name,
                "title": f"AeroRoute & Airline Intelligence ({origin} to {destination})",
                "source_type": "ESTIMATED INFORMATION",
                "url": "https://www.iata.org/en/publications/directories/",
                "snippet": f"Estimated commercial flight routes and carrier information from {origin} to {destination}; not a live fare or availability result."
            }
        ]

        if is_live:
            sources.append({
                "agent_name": self.name,
                "title": "AviationStack Live Flight Data Feed",
                "source_type": "LIVE API DATA",
                "url": "https://aviationstack.com",
                "snippet": f"Real-time flight schedule verified via AviationStack API."
            })

        return {
            "origin_airport": flight_intel.get("origin_airport", f"{origin} International Airport"),
            "destination_airport": flight_intel.get("destination_airport", f"{destination} International Airport"),
            "route_summary": flight_intel.get("route_summary", f"Connecting and direct options available between {origin} and {destination}."),
            "direct_options": live_routes if is_live and live_routes else flight_intel.get("direct_options", []),
            "connecting_options": flight_intel.get("connecting_options", []),
            "airlines": flight_intel.get("airlines", ["Air India", "Singapore Airlines", "Japan Airlines"]),
            "fare_range_low": flight_intel.get("fare_range_low", 35000.0 if currency == "INR" else 450.0),
            "fare_range_high": flight_intel.get("fare_range_high", 65000.0 if currency == "INR" else 850.0),
            "estimated_duration_hours": flight_intel.get("estimated_duration_hours", 9.5),
            "currency": currency,
            "is_live_data": is_live,
            "api_status_note": api_note or ("Live flight API key not active. Researched commercial route estimates provided." if not is_live else "Live flight data verified."),
            "source_citations": sources,
        }

    async def research_flight_routes(self, origin: str, destination: str, currency: str, travellers: int) -> Dict[str, Any]:
        """Queries LLM for accurate flight corridor data."""
        if llm_service.is_available():
            system_prompt = (
                "You are an Aviation & Flight Research Agent. Provide realistic commercial airline routes, "
                "standard airline carriers, typical flight duration, and realistic round-trip fare ranges. "
                "DO NOT invent fake live flight numbers. Return JSON ONLY."
            )
            prompt = (
                f"Origin: {origin}\n"
                f"Destination: {destination}\n"
                f"Currency: {currency}\n"
                f"Travellers: {travellers}\n"
                "Return JSON with keys:\n"
                "- origin_airport (string, e.g. 'Kempegowda International Airport (BLR)')\n"
                "- destination_airport (string, e.g. 'Narita / Haneda (TYO)')\n"
                "- route_summary (string explanation of typical connection hubs or direct paths)\n"
                "- airlines (list of 3-5 real airlines operating this corridor)\n"
                "- direct_options (list of objects with {airline, departure_airport, arrival_airport, duration_hours, stops: 0, estimated_price, is_live_data: false, notes})\n"
                "- connecting_options (list of objects with {airline, departure_airport, arrival_airport, duration_hours, stops: 1, estimated_price, is_live_data: false, notes})\n"
                "- fare_range_low (float per person roundtrip)\n"
                "- fare_range_high (float per person roundtrip)\n"
                "- estimated_duration_hours (float)\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                return data
            except Exception as e:
                logger.warning(f"Flight LLM research failed: {e}")

        # Deterministic domain fallback
        return {
            "origin_airport": f"{origin} International Airport",
            "destination_airport": f"{destination} Major Airport Hub",
            "route_summary": f"Routes from {origin} to {destination} commonly operate via major international transit hubs.",
            "airlines": ["Singapore Airlines", "Emirates", "Qatar Airways", "Cathay Pacific"],
            "direct_options": [
                {
                    "airline": "Major International Carrier",
                    "departure_airport": f"{origin} (Main)",
                    "arrival_airport": f"{destination} (Main)",
                    "duration_hours": 9.0,
                    "stops": 0,
                    "estimated_price": 45000.0 if currency == "INR" else 550.0,
                    "is_live_data": False,
                    "notes": "Direct seasonal route estimate"
                }
            ],
            "connecting_options": [
                {
                    "airline": "Transit Partner Airline",
                    "departure_airport": f"{origin} (Main)",
                    "arrival_airport": f"{destination} (Main)",
                    "duration_hours": 12.5,
                    "stops": 1,
                    "estimated_price": 36000.0 if currency == "INR" else 430.0,
                    "is_live_data": False,
                    "notes": "1-stop transit via hub"
                }
            ],
            "fare_range_low": 35000.0 if currency == "INR" else 420.0,
            "fare_range_high": 58000.0 if currency == "INR" else 720.0,
            "estimated_duration_hours": 10.0,
        }
