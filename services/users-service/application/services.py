from passlib.context import CryptContext
from typing import Optional
from uuid import UUID

from domain.use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    GetUserByEmailUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase
)
from infrastructure.repositories import SQLAlchemyUserRepository
from infrastructure.database import async_session_maker


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")


class UserService:
    def __init__(self):
        self.create_user_use_case = None
        self.get_user_use_case = None
        self.get_user_by_email_use_case = None
        self.update_user_use_case = None
        self.delete_user_use_case = None

    async def _get_repository(self):
        async with async_session_maker() as session:
            return SQLAlchemyUserRepository(session)

    async def create_user(self, email: str, password: str, full_name: Optional[str] = None):
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = CreateUserUseCase(repository)
            password_hash = pwd_context.hash(password)
            return await use_case.execute(email, password_hash, full_name)

    async def get_user(self, user_id: UUID):
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = GetUserUseCase(repository)
            return await use_case.execute(user_id)

    async def get_user_by_email(self, email: str):
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = GetUserByEmailUseCase(repository)
            return await use_case.execute(email)

    async def update_user(self, user_id: UUID, full_name: Optional[str] = None):
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = UpdateUserUseCase(repository)
            return await use_case.execute(user_id, full_name)

    async def delete_user(self, user_id: UUID):
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = DeleteUserUseCase(repository)
            return await use_case.execute(user_id)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

