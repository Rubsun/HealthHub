import logging
from uuid import UUID

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

from infrastructure.settings import settings
from infrastructure.database import async_session_maker
from infrastructure.repositories import SQLAlchemyMealRepository

logger = logging.getLogger(__name__)


def create_broker() -> RabbitBroker:
    """Create a configured RabbitBroker for consuming."""
    return RabbitBroker(settings.rabbitmq_url)


def setup_consumers(broker: RabbitBroker) -> None:
    """Set up all event consumers for nutrition-service."""
    
    users_exchange = RabbitExchange(
        name="users.events",
        type=ExchangeType.TOPIC,
        durable=True
    )
    
    user_created_queue = RabbitQueue(
        name="nutrition.user.created",
        durable=True,
        routing_key="user.created"
    )
    
    user_deleted_queue = RabbitQueue(
        name="nutrition.user.deleted",
        durable=True,
        routing_key="user.deleted"
    )
    
    @broker.subscriber(user_created_queue, users_exchange)
    async def handle_user_created(message: dict) -> None:
        """Handle user created event."""
        user_id = message.get("user_id")
        email = message.get("email")
        logger.info(f"Received user.created event for user {user_id} ({email})")
        logger.info(f"User {user_id} registered in nutrition-service")
    
    @broker.subscriber(user_deleted_queue, users_exchange)
    async def handle_user_deleted(message: dict) -> None:
        """Handle user deleted event - cleanup user nutrition data."""
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
            meal_repo = SQLAlchemyMealRepository(session)
            
            meals = await meal_repo.get_by_user_id(user_id, limit=10000)
            for meal in meals:
                await meal_repo.delete(meal.meal_id)
            
            logger.info(f"Cleaned up nutrition data for deleted user {user_id}: "
                       f"{len(meals)} meals deleted")


async def run_consumer() -> None:
    """Run the nutrition-service consumer."""
    broker = create_broker()
    setup_consumers(broker)
    app = FastStream(broker)
    
    logger.info("Starting nutrition-service consumer...")
    await app.run()

