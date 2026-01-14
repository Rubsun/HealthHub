import logging
from uuid import UUID

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

from infrastructure.settings import settings
from infrastructure.database import async_session_maker
from infrastructure.repositories import (
    SQLAlchemyHealthMetricRepository,
    SQLAlchemyActivityRepository,
    SQLAlchemyRecommendationRepository
)

logger = logging.getLogger(__name__)


def create_broker() -> RabbitBroker:
    """Create a configured RabbitBroker for consuming."""
    return RabbitBroker(settings.rabbitmq_url)


def setup_consumers(broker: RabbitBroker) -> None:
    """Set up all event consumers for health-service."""
    
    users_exchange = RabbitExchange(
        name="users.events",
        type=ExchangeType.TOPIC,
        durable=True
    )
    
    integrations_exchange = RabbitExchange(
        name="integrations.events",
        type=ExchangeType.TOPIC,
        durable=True
    )
    
    user_created_queue = RabbitQueue(
        name="health.user.created",
        durable=True,
        routing_key="user.created"
    )
    
    user_deleted_queue = RabbitQueue(
        name="health.user.deleted",
        durable=True,
        routing_key="user.deleted"
    )
    
    weather_updated_queue = RabbitQueue(
        name="health.weather.updated",
        durable=True,
        routing_key="weather.updated"
    )
    
    @broker.subscriber(user_created_queue, users_exchange)
    async def handle_user_created(message: dict) -> None:
        """Handle user created event - prepare user health profile."""
        user_id = message.get("user_id")
        email = message.get("email")
        logger.info(f"Received user.created event for user {user_id} ({email})")
        # TODO: мб что то сюда
        logger.info(f"User {user_id} registered in health-service")
    
    @broker.subscriber(user_deleted_queue, users_exchange)
    async def handle_user_deleted(message: dict) -> None:
        """Handle user deleted event - cleanup user health data."""
        user_id_str = message.get("user_id")
        if not user_id_str:
            logger.warning("Received user.deleted event without user_id")
            return
        
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.error(f"Invalid user_id format: {user_id_str}")
            return
        
        logger.info(f"Received user.deleted event for user {user_id}")
        
        async with async_session_maker() as session:
            metric_repo = SQLAlchemyHealthMetricRepository(session)
            activity_repo = SQLAlchemyActivityRepository(session)
            recommendation_repo = SQLAlchemyRecommendationRepository(session)
            
            metrics = await metric_repo.get_by_user_id(user_id, limit=10000)
            for metric in metrics:
                await metric_repo.delete(metric.metric_id)
            
            activities = await activity_repo.get_by_user_id(user_id, limit=10000)
            for activity in activities:
                await activity_repo.delete(activity.activity_id)
            
            logger.info(f"Cleaned up health data for deleted user {user_id}: "
                       f"{len(metrics)} metrics, {len(activities)} activities")
    
    @broker.subscriber(weather_updated_queue, integrations_exchange)
    async def handle_weather_updated(message: dict) -> None:
        """Handle weather updated event - can trigger weather-based recommendations."""
        city = message.get("city")
        temperature = message.get("temperature")
        description = message.get("description")
        
        logger.info(f"Received weather.updated event for {city}: "
                   f"{temperature}°C, {description}")
        
        # TODO: добавить возможные рекомендации


async def run_consumer() -> None:
    """Run the health-service consumer."""
    broker = create_broker()
    setup_consumers(broker)
    app = FastStream(broker)
    
    logger.info("Starting health-service consumer...")
    await app.run()

