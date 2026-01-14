import logging
from typing import Optional
from datetime import datetime

from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class IntegrationsEventPublisher:
    """Publisher for integrations-related events."""
    
    def __init__(self):
        self._broker: Optional[RabbitBroker] = None
        self._exchange: Optional[RabbitExchange] = None
        self._connected = False
    
    @property
    def broker(self) -> RabbitBroker:
        if self._broker is None:
            self._broker = RabbitBroker(settings.rabbitmq_url)
        return self._broker
    
    @property
    def exchange(self) -> RabbitExchange:
        if self._exchange is None:
            self._exchange = RabbitExchange(
                name="integrations.events",
                type=ExchangeType.TOPIC,
                durable=True
            )
        return self._exchange
    
    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        if not self._connected:
            try:
                await self.broker.connect()
                self._connected = True
                logger.info("IntegrationsEventPublisher connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._connected and self._broker:
            try:
                await self._broker.close()
                self._connected = False
                logger.info("IntegrationsEventPublisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish_weather_updated(
        self,
        city: str,
        temperature: float,
        description: str,
        humidity: Optional[int] = None,
        wind_speed: Optional[float] = None,
        recorded_at: Optional[datetime] = None
    ) -> None:
        """Publish weather updated event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "weather.updated",
            "city": city,
            "temperature": temperature,
            "description": description,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "recorded_at": recorded_at.isoformat() if recorded_at else None
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="weather.updated"
            )
            logger.info(f"Published weather.updated event for {city}")
        except Exception as e:
            logger.error(f"Failed to publish weather.updated event: {e}")


_publisher: Optional[IntegrationsEventPublisher] = None


def get_publisher() -> IntegrationsEventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = IntegrationsEventPublisher()
    return _publisher


async def shutdown_publisher() -> None:
    global _publisher
    if _publisher:
        await _publisher.disconnect()
        _publisher = None

