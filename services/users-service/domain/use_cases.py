from typing import Optional
from uuid import UUID

from domain.entities import User
from domain.repositories import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password_hash: str, full_name: Optional[str] = None) -> User:
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        user = User(email=email, password_hash=password_hash, full_name=full_name)
        return await self.user_repository.create(user)


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> Optional[User]:
        return await self.user_repository.get_by_id(user_id)


class GetUserByEmailUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(email)


class UpdateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID, full_name: Optional[str] = None) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.update(full_name=full_name)
        return await self.user_repository.update(user)


class DeleteUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: UUID) -> bool:
        return await self.user_repository.delete(user_id)



