import logging
from typing import Optional, Dict, Any
import httpx

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class OpenWeatherAPI:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_api_url
        self.timeout = 10.0

    async def get_current_weather(self, city: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/weather"
                params = {
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric"
                }
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "city": data.get("name", city),
                    "temperature": data.get("main", {}).get("temp"),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "humidity": data.get("main", {}).get("humidity"),
                    "wind_speed": data.get("wind", {}).get("speed"),
                }
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching weather for {city} from OpenWeather")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching weather for {city}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching weather for {city} from OpenWeather: {e}")
            return None



