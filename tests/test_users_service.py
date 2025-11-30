import pytest
from uuid import uuid4
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "users-service"))

from domain.entities import User
from domain.use_cases import CreateUserUseCase, GetUserUseCase
from application.services import UserService


class MockUserRepository:
    def __init__(self):
        self.users = {}

    async def create(self, user: User) -> User:
        self.users[user.user_id] = user
        return user

    async def get_by_id(self, user_id):
        return self.users.get(user_id)

    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def update(self, user: User) -> User:
        self.users[user.user_id] = user
        return user

    async def delete(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


@pytest.mark.asyncio
async def test_create_user_use_case():
    repository = MockUserRepository()
    use_case = CreateUserUseCase(repository)
    
    user = await use_case.execute("test@example.com", "hashed_password", "Test User")
    
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.password_hash == "hashed_password"


@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    repository = MockUserRepository()
    use_case = CreateUserUseCase(repository)
    
    await use_case.execute("test@example.com", "hashed_password", "Test User")
    
    with pytest.raises(ValueError, match="User with this email already exists"):
        await use_case.execute("test@example.com", "another_password", "Another User")


@pytest.mark.asyncio
async def test_get_user_use_case():
    repository = MockUserRepository()
    create_use_case = CreateUserUseCase(repository)
    get_use_case = GetUserUseCase(repository)
    
    created_user = await create_use_case.execute("test@example.com", "hashed_password")
    retrieved_user = await get_use_case.execute(created_user.user_id)
    
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_user_service_password_hashing():
    service = UserService()
    
    password = "testpassword123"
    hashed = service.get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0


@pytest.mark.asyncio
async def test_user_service_verify_password():
    service = UserService()
    
    password = "testpassword123"
    hashed = service.get_password_hash(password)
    
    assert service.verify_password(password, hashed) is True
    assert service.verify_password("wrongpassword", hashed) is False


def test_user_entity():
    user = User(
        email="test@example.com",
        password_hash="hashed",
        full_name="Test User"
    )
    
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed"
    assert user.full_name == "Test User"
    assert user.user_id is not None
    assert user.created_at is not None


def test_user_update():
    user = User(
        email="test@example.com",
        password_hash="hashed",
        full_name="Old Name"
    )
    
    original_updated_at = user.updated_at
    user.update(full_name="New Name")
    
    assert user.full_name == "New Name"
    assert user.updated_at != original_updated_at

