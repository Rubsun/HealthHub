import logging
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
from infrastructure.messaging import get_publisher

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")


class UserService:
    """Service for user management operations."""
    
    def __init__(self):
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    async def create_user(self, email: str, password: str, full_name: Optional[str] = None):
        """Create a new user and publish created event."""
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = CreateUserUseCase(repository)
            password_hash = pwd_context.hash(password)
            user = await use_case.execute(email, password_hash, full_name)
        
        try:
            await self.publisher.publish_user_created(
                user_id=user.user_id,
                email=user.email,
                full_name=user.full_name
            )
        except Exception as e:
            logger.warning(f"Failed to publish user.created event: {e}")
        
        return user
    
    async def get_user(self, user_id: UUID):
        """Get user by ID."""
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = GetUserUseCase(repository)
            return await use_case.execute(user_id)
    
    async def get_user_by_email(self, email: str):
        """Get user by email."""
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = GetUserByEmailUseCase(repository)
            return await use_case.execute(email)
    
    async def update_user(self, user_id: UUID, full_name: Optional[str] = None):
        """Update user and publish updated event."""
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = UpdateUserUseCase(repository)
            user = await use_case.execute(user_id, full_name)
        
        try:
            await self.publisher.publish_user_updated(
                user_id=user.user_id,
                full_name=user.full_name
            )
        except Exception as e:
            logger.warning(f"Failed to publish user.updated event: {e}")
        
        return user
    
    async def delete_user(self, user_id: UUID):
        """Delete user and publish deleted event."""
        async with async_session_maker() as session:
            repository = SQLAlchemyUserRepository(session)
            use_case = DeleteUserUseCase(repository)
            deleted = await use_case.execute(user_id)
        
        if deleted:
            try:
                await self.publisher.publish_user_deleted(user_id=user_id)
            except Exception as e:
                logger.warning(f"Failed to publish user.deleted event: {e}")
        
        return deleted
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
