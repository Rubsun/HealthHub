import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from application.services import WeatherService

logger = logging.getLogger(__name__)

weather_service = WeatherService()


def setup_consumers(app: FastStream):
    broker = app.broker

    @broker.subscriber("weather.fetch")
    async def handle_weather_fetch(city: str):
        logger.info(f"Received weather fetch request for city: {city}")
        try:
            weather_log = await weather_service.fetch_and_save_weather(city)
            if weather_log:
                logger.info(f"Weather data saved for {city}: {weather_log.temperature}°C")
            else:
                logger.warning(f"Failed to fetch weather for {city}")
        except Exception as e:
            logger.error(f"Error processing weather fetch for {city}: {e}")



