from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import User
from domain.repositories import UserRepository
from infrastructure.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            user_id=model.user_id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            user_id=entity.user_id,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user.user_id)
        )
        model = result.scalar_one()
        model.email = user.email
        model.password_hash = user.password_hash
        model.full_name = user.full_name
        model.updated_at = user.updated_at
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True



