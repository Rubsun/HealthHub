import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

from infrastructure.settings import settings
from infrastructure.messaging import get_publisher
from application.services import WeatherService

logger = logging.getLogger(__name__)

weather_service = WeatherService()


def create_broker() -> RabbitBroker:
    return RabbitBroker(settings.rabbitmq_url)


def setup_consumers(broker: RabbitBroker) -> None:
    integrations_exchange = RabbitExchange(
        name="integrations.commands",
        type=ExchangeType.TOPIC,
        durable=True
    )
    
    health_exchange = RabbitExchange(
        name="health.events",
        type=ExchangeType.TOPIC,
        durable=True
    )
    
    weather_fetch_queue = RabbitQueue(
        name="integrations.weather.fetch",
        durable=True,
        routing_key="weather.fetch"
    )
    
    activity_created_queue = RabbitQueue(
        name="integrations.activity.created",
        durable=True,
        routing_key="activity.created"
    )
    
    @broker.subscriber(weather_fetch_queue, integrations_exchange)
    async def handle_weather_fetch(message: dict) -> None:
        city = message.get("city") if isinstance(message, dict) else message
        if not city:
            logger.warning("Received weather fetch request without city")
            return
        
        logger.info(f"Received weather fetch request for city: {city}")
        
        try:
            weather_log = await weather_service.fetch_and_save_weather(city)
            if weather_log:
                logger.info(f"Weather data saved for {city}: {weather_log.temperature}°C")
                
                publisher = get_publisher()
                await publisher.publish_weather_updated(
                    city=weather_log.city,
                    temperature=weather_log.temperature,
                    description=weather_log.description,
                    humidity=weather_log.humidity,
                    wind_speed=weather_log.wind_speed,
                    recorded_at=weather_log.recorded_at
                )
            else:
                logger.warning(f"Failed to fetch weather for {city}")
        except Exception as e:
            logger.error(f"Error processing weather fetch for {city}: {e}")
    
    @broker.subscriber(activity_created_queue, health_exchange)
    async def handle_activity_created(message: dict) -> None:
        user_id = message.get("user_id")
        activity_type = message.get("activity_type")
        
        logger.info(f"Received activity.created event for user {user_id}: {activity_type}")
        
        if activity_type in ["running", "walking", "cycling"]:
            logger.info(f"Outdoor activity detected for user {user_id}")


async def run_consumer() -> None:
    broker = create_broker()
    setup_consumers(broker)
    app = FastStream(broker)
    
    publisher = get_publisher()
    await publisher.connect()
    
    logger.info("Starting integrations-service consumer...")
    await app.run()
