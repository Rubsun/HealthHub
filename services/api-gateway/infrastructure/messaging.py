import logging
from typing import Optional
from uuid import UUID

from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class GatewayEventPublisher:
    """Publisher for gateway commands and events."""
    
    def __init__(self):
        self._broker: Optional[RabbitBroker] = None
        self._integrations_exchange: Optional[RabbitExchange] = None
        self._connected = False
    
    @property
    def broker(self) -> RabbitBroker:
        if self._broker is None:
            self._broker = RabbitBroker(settings.rabbitmq_url)
        return self._broker
    
    @property
    def integrations_exchange(self) -> RabbitExchange:
        if self._integrations_exchange is None:
            self._integrations_exchange = RabbitExchange(
                name="integrations.commands",
                type=ExchangeType.TOPIC,
                durable=True
            )
        return self._integrations_exchange
    
    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        if not self._connected:
            try:
                await self.broker.connect()
                self._connected = True
                logger.info("GatewayEventPublisher connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._connected and self._broker:
            try:
                await self._broker.close()
                self._connected = False
                logger.info("GatewayEventPublisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def request_weather_fetch(self, city: str, user_id: Optional[UUID] = None) -> None:
        """Request weather fetch from integrations service."""
        if not self._connected:
            await self.connect()
        
        message = {
            "city": city,
            "user_id": str(user_id) if user_id else None
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.integrations_exchange,
                routing_key="weather.fetch"
            )
            logger.info(f"Published weather.fetch request for {city}")
        except Exception as e:
            logger.error(f"Failed to publish weather.fetch request: {e}")


_publisher: Optional[GatewayEventPublisher] = None


def get_publisher() -> GatewayEventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = GatewayEventPublisher()
    return _publisher


async def shutdown_publisher() -> None:
    global _publisher
    if _publisher:
        await _publisher.disconnect()
        _publisher = None

