import logging
from typing import Optional
from uuid import UUID

from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class UserEventPublisher:
    """Publisher for user-related events."""
    
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
                name="users.events",
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
                logger.info("UserEventPublisher connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._connected and self._broker:
            try:
                await self._broker.close()
                self._connected = False
                logger.info("UserEventPublisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish_user_created(
        self,
        user_id: UUID,
        email: str,
        full_name: Optional[str] = None
    ) -> None:
        """Publish user created event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "user.created",
            "user_id": str(user_id),
            "email": email,
            "full_name": full_name
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="user.created"
            )
            logger.info(f"Published user.created event for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish user.created event: {e}")
    
    async def publish_user_updated(
        self,
        user_id: UUID,
        full_name: Optional[str] = None
    ) -> None:
        """Publish user updated event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "user.updated",
            "user_id": str(user_id),
            "full_name": full_name
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="user.updated"
            )
            logger.info(f"Published user.updated event for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish user.updated event: {e}")
    
    async def publish_user_deleted(self, user_id: UUID) -> None:
        """Publish user deleted event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "user.deleted",
            "user_id": str(user_id)
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="user.deleted"
            )
            logger.info(f"Published user.deleted event for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish user.deleted event: {e}")


_publisher: Optional[UserEventPublisher] = None


def get_publisher() -> UserEventPublisher:
    """Get or create the global publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = UserEventPublisher()
    return _publisher


async def shutdown_publisher() -> None:
    """Shutdown the global publisher."""
    global _publisher
    if _publisher:
        await _publisher.disconnect()
        _publisher = None

