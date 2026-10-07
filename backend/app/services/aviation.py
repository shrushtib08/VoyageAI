import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class AviationService:
    def __init__(self):
        self.api_key = settings.AVIATIONSTACK_API_KEY
        self.base_url = "http://api.aviationstack.com/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    async def search_flights(self, origin: str, destination: str) -> Dict[str, Any]:
        """Attempts to call AviationStack API; falls back gracefully if unconfigured or unsuccessful."""
        if not self.is_configured():
            return {
                "is_live_data": False,
                "api_status_note": "AviationStack API key not configured. Using researched airline and route estimates.",
                "routes": [],
            }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = client.get(
                    f"{self.base_url}/flights",
                    params={
                        "access_key": self.api_key,
                        "dep_iata": origin[:3].upper() if len(origin) == 3 else None,
                        "arr_iata": destination[:3].upper() if len(destination) == 3 else None,
                        "limit": 5,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    flights_data = data.get("data", [])
                    if flights_data:
                        live_routes = []
                        for f in flights_data:
                            airline_name = f.get("airline", {}).get("name", "Commercial Airline")
                            flight_num = f.get("flight", {}).get("iata", "N/A")
                            live_routes.append({
                                "airline": airline_name,
                                "flight_number": flight_num,
                                "departure_airport": f.get("departure", {}).get("airport", origin),
                                "arrival_airport": f.get("arrival", {}).get("airport", destination),
                                "departure_time": f.get("departure", {}).get("estimated", "Scheduled"),
                                "arrival_time": f.get("arrival", {}).get("estimated", "Scheduled"),
                                "is_live_data": True,
                                "notes": f"Status: {f.get('flight_status', 'scheduled')}"
                            })
                        return {
                            "is_live_data": True,
                            "api_status_note": "Live AviationStack flight schedule retrieved.",
                            "routes": live_routes,
                        }
                    else:
                        return {
                            "is_live_data": False,
                            "api_status_note": "No active live flights returned for route; using researched airline route estimates.",
                            "routes": [],
                        }
                else:
                    logger.warning(f"AviationStack responded with status {response.status_code}")
                    return {
                        "is_live_data": False,
                        "api_status_note": f"AviationStack API returned status {response.status_code}. Using researched estimates.",
                        "routes": [],
                    }
        except Exception as e:
            logger.warning(f"AviationStack request error: {e}")
            return {
                "is_live_data": False,
                "api_status_note": "External flight API connection unavailable. Using researched estimates.",
                "routes": [],
            }


aviation_service = AviationService()
