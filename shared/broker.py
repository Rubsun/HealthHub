import logging
from typing import Optional
from contextlib import asynccontextmanager

from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

from shared.events import Exchanges, Queues

logger = logging.getLogger(__name__)


def create_broker(rabbitmq_url: str) -> RabbitBroker:
    """Create a configured RabbitBroker instance."""
    return RabbitBroker(
        rabbitmq_url,
        logger=logger,
    )


def get_users_exchange() -> RabbitExchange:
    """Get the users exchange configuration."""
    return RabbitExchange(
        name=Exchanges.USERS,
        type=ExchangeType.TOPIC,
        durable=True
    )


def get_health_exchange() -> RabbitExchange:
    """Get the health exchange configuration."""
    return RabbitExchange(
        name=Exchanges.HEALTH,
        type=ExchangeType.TOPIC,
        durable=True
    )


def get_nutrition_exchange() -> RabbitExchange:
    """Get the nutrition exchange configuration."""
    return RabbitExchange(
        name=Exchanges.NUTRITION,
        type=ExchangeType.TOPIC,
        durable=True
    )


def get_integrations_exchange() -> RabbitExchange:
    """Get the integrations exchange configuration."""
    return RabbitExchange(
        name=Exchanges.INTEGRATIONS,
        type=ExchangeType.TOPIC,
        durable=True
    )


def get_health_user_created_queue() -> RabbitQueue:
    """Queue for health service to receive user created events."""
    return RabbitQueue(
        name=Queues.HEALTH_USER_CREATED,
        durable=True,
        routing_key="user.created"
    )


def get_health_user_deleted_queue() -> RabbitQueue:
    """Queue for health service to receive user deleted events."""
    return RabbitQueue(
        name=Queues.HEALTH_USER_DELETED,
        durable=True,
        routing_key="user.deleted"
    )


def get_health_weather_updated_queue() -> RabbitQueue:
    """Queue for health service to receive weather updates."""
    return RabbitQueue(
        name=Queues.HEALTH_WEATHER_UPDATED,
        durable=True,
        routing_key="weather.updated"
    )


def get_nutrition_user_created_queue() -> RabbitQueue:
    """Queue for nutrition service to receive user created events."""
    return RabbitQueue(
        name=Queues.NUTRITION_USER_CREATED,
        durable=True,
        routing_key="user.created"
    )


def get_nutrition_user_deleted_queue() -> RabbitQueue:
    """Queue for nutrition service to receive user deleted events."""
    return RabbitQueue(
        name=Queues.NUTRITION_USER_DELETED,
        durable=True,
        routing_key="user.deleted"
    )


def get_integrations_weather_fetch_queue() -> RabbitQueue:
    """Queue for integrations service to receive weather fetch requests."""
    return RabbitQueue(
        name=Queues.INTEGRATIONS_WEATHER_FETCH,
        durable=True,
        routing_key="weather.fetch"
    )


def get_integrations_activity_created_queue() -> RabbitQueue:
    """Queue for integrations to receive activity events (for weather recommendations)."""
    return RabbitQueue(
        name=Queues.INTEGRATIONS_ACTIVITY_CREATED,
        durable=True,
        routing_key="activity.created"
    )


def get_recommendations_generate_queue() -> RabbitQueue:
    """Queue for recommendation generation requests."""
    return RabbitQueue(
        name=Queues.RECOMMENDATIONS_GENERATE,
        durable=True,
        routing_key="recommendation.generate"
    )


class BrokerManager:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self._broker: Optional[RabbitBroker] = None
        self._connected = False
    
    @property
    def broker(self) -> RabbitBroker:
        if self._broker is None:
            self._broker = create_broker(self.rabbitmq_url)
        return self._broker
    
    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        if not self._connected:
            await self.broker.connect()
            self._connected = True
            logger.info("Connected to RabbitMQ")
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._connected and self._broker:
            await self._broker.close()
            self._connected = False
            logger.info("Disconnected from RabbitMQ")
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager for broker lifecycle."""
        await self.connect()
        try:
            yield self.broker
        finally:
            await self.disconnect()
    
    async def publish(
        self,
        message: dict,
        exchange: RabbitExchange,
        routing_key: str
    ) -> None:
        """Publish a message to an exchange."""
        if not self._connected:
            await self.connect()
        
        await self.broker.publish(
            message,
            exchange=exchange,
            routing_key=routing_key
        )
        logger.debug(f"Published message to {exchange.name} with key {routing_key}")

