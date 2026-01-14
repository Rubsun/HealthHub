import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class NutritionEventPublisher:
    """Publisher for nutrition-related events."""
    
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
                name="nutrition.events",
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
                logger.info("NutritionEventPublisher connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._connected and self._broker:
            try:
                await self._broker.close()
                self._connected = False
                logger.info("NutritionEventPublisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish_food_created(
        self,
        food_id: UUID,
        name: str,
        barcode: Optional[str] = None,
        calories_per_100g: Optional[float] = None
    ) -> None:
        """Publish food created event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "food.created",
            "food_id": str(food_id),
            "name": name,
            "barcode": barcode,
            "calories_per_100g": calories_per_100g
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="food.created"
            )
            logger.info(f"Published food.created event for food {food_id}")
        except Exception as e:
            logger.error(f"Failed to publish food.created event: {e}")
    
    async def publish_meal_logged(
        self,
        meal_id: UUID,
        user_id: UUID,
        food_id: UUID,
        quantity_grams: float,
        consumed_at: Optional[datetime] = None
    ) -> None:
        """Publish meal logged event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "meal.logged",
            "meal_id": str(meal_id),
            "user_id": str(user_id),
            "food_id": str(food_id),
            "quantity_grams": quantity_grams,
            "consumed_at": consumed_at.isoformat() if consumed_at else None
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="meal.logged"
            )
            logger.info(f"Published meal.logged event for meal {meal_id}")
        except Exception as e:
            logger.error(f"Failed to publish meal.logged event: {e}")


_publisher: Optional[NutritionEventPublisher] = None


def get_publisher() -> NutritionEventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = NutritionEventPublisher()
    return _publisher


async def shutdown_publisher() -> None:
    global _publisher
    if _publisher:
        await _publisher.disconnect()
        _publisher = None

