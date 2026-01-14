import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

from infrastructure.settings import settings

logger = logging.getLogger(__name__)


class HealthEventPublisher:
    """Publisher for health-related events."""
    
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
                name="health.events",
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
                logger.info("HealthEventPublisher connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self._connected and self._broker:
            try:
                await self._broker.close()
                self._connected = False
                logger.info("HealthEventPublisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish_health_metric_created(
        self,
        metric_id: UUID,
        user_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        recorded_at: Optional[datetime] = None
    ) -> None:
        """Publish health metric created event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "health.metric.created",
            "metric_id": str(metric_id),
            "user_id": str(user_id),
            "steps": steps,
            "calories": calories,
            "heart_rate": heart_rate,
            "sleep_hours": sleep_hours,
            "recorded_at": recorded_at.isoformat() if recorded_at else None
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="health.metric.created"
            )
            logger.info(f"Published health.metric.created event for metric {metric_id}")
        except Exception as e:
            logger.error(f"Failed to publish health.metric.created event: {e}")
    
    async def publish_activity_created(
        self,
        activity_id: UUID,
        user_id: UUID,
        activity_type: str,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None,
        started_at: Optional[datetime] = None
    ) -> None:
        """Publish activity created event."""
        if not self._connected:
            await self.connect()
        
        message = {
            "event_type": "activity.created",
            "activity_id": str(activity_id),
            "user_id": str(user_id),
            "activity_type": activity_type,
            "duration_minutes": duration_minutes,
            "calories_burned": calories_burned,
            "distance_km": distance_km,
            "started_at": started_at.isoformat() if started_at else None
        }
        
        try:
            await self.broker.publish(
                message,
                exchange=self.exchange,
                routing_key="activity.created"
            )
            logger.info(f"Published activity.created event for activity {activity_id}")
        except Exception as e:
            logger.error(f"Failed to publish activity.created event: {e}")
    
    async def publish_recommendation_generated(
        self,
        recommendation_id: UUID,
        user_id: UUID,
        message: str
    ) -> None:
        """Publish recommendation generated event."""
        if not self._connected:
            await self.connect()
        
        event_message = {
            "event_type": "recommendation.generated",
            "recommendation_id": str(recommendation_id),
            "user_id": str(user_id),
            "message": message
        }
        
        try:
            await self.broker.publish(
                event_message,
                exchange=self.exchange,
                routing_key="recommendation.generated"
            )
            logger.info(f"Published recommendation.generated event for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish recommendation.generated event: {e}")


_publisher: Optional[HealthEventPublisher] = None


def get_publisher() -> HealthEventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = HealthEventPublisher()
    return _publisher


async def shutdown_publisher() -> None:
    global _publisher
    if _publisher:
        await _publisher.disconnect()
        _publisher = None

