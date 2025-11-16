from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import WeatherLog
from domain.repositories import WeatherLogRepository
from infrastructure.models import WeatherLogModel


class SQLAlchemyWeatherLogRepository(WeatherLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: WeatherLogModel) -> WeatherLog:
        return WeatherLog(
            log_id=model.log_id,
            city=model.city,
            temperature=model.temperature,
            description=model.description,
            humidity=model.humidity,
            wind_speed=model.wind_speed,
            recorded_at=model.recorded_at,
            created_at=model.created_at
        )

    def _to_model(self, entity: WeatherLog) -> WeatherLogModel:
        return WeatherLogModel(
            log_id=entity.log_id,
            city=entity.city,
            temperature=entity.temperature,
            description=entity.description,
            humidity=entity.humidity,
            wind_speed=entity.wind_speed,
            recorded_at=entity.recorded_at,
            created_at=entity.created_at
        )

    async def create(self, log: WeatherLog) -> WeatherLog:
        model = self._to_model(log)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_latest_by_city(self, city: str) -> Optional[WeatherLog]:
        result = await self.session.execute(
            select(WeatherLogModel)
            .where(WeatherLogModel.city == city)
            .order_by(WeatherLogModel.recorded_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_city(self, city: str, limit: int = 10) -> List[WeatherLog]:
        result = await self.session.execute(
            select(WeatherLogModel)
            .where(WeatherLogModel.city == city)
            .order_by(WeatherLogModel.recorded_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]



