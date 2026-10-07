import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    async def get_destination_weather(self, destination: str) -> Dict[str, Any]:
        """Queries OpenWeather; returns structured weather data with clear live/seasonal status."""
        if not self.is_configured():
            return {
                "is_live_forecast": False,
                "api_status_note": "OpenWeather API key not configured. Using climate & seasonal historical averages.",
                "data": None,
            }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                # 1. Get current weather / city coordinates
                resp = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": destination,
                        "appid": self.api_key,
                        "units": "metric",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    temp = data.get("main", {}).get("temp")
                    temp_min = data.get("main", {}).get("temp_min")
                    temp_max = data.get("main", {}).get("temp_max")
                    conditions = ", ".join([w.get("description", "") for w in data.get("weather", [])])
                    humidity = data.get("main", {}).get("humidity")
                    return {
                        "is_live_forecast": True,
                        "api_status_note": "Live OpenWeather current conditions retrieved.",
                        "data": {
                            "temp": temp,
                            "temp_min": temp_min,
                            "temp_max": temp_max,
                            "conditions": conditions.capitalize(),
                            "humidity": humidity,
                        },
                    }
                else:
                    logger.warning(f"OpenWeather responded with code {resp.status_code}")
                    return {
                        "is_live_forecast": False,
                        "api_status_note": f"OpenWeather returned code {resp.status_code}. Using seasonal meteorological data.",
                        "data": None,
                    }
        except Exception as e:
            logger.warning(f"OpenWeather request error: {e}")
            return {
                "is_live_forecast": False,
                "api_status_note": "OpenWeather service unreachable. Using seasonal meteorological data.",
                "data": None,
            }


weather_service = WeatherService()
