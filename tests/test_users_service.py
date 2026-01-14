import pytest
from uuid import uuid4
from datetime import datetime
import importlib.util
from pathlib import Path


def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service_path = Path(__file__).parent.parent / "services" / "users-service"
entities_module = load_module_from_path("users_entities", service_path / "domain" / "entities.py")

User = entities_module.User


class MockUserRepository:
    def __init__(self):
        self.users = {}

    async def create(self, user) -> object:
        self.users[user.user_id] = user
        return user

    async def get_by_id(self, user_id):
        return self.users.get(user_id)

    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def update(self, user) -> object:
        self.users[user.user_id] = user
        return user

    async def delete(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


@pytest.mark.asyncio
async def test_create_user_in_repository():
    repository = MockUserRepository()
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User"
    )
    created = await repository.create(user)
    assert created.email == "test@example.com"
    assert created.full_name == "Test User"
    assert created.password_hash == "hashed_password"


@pytest.mark.asyncio
async def test_get_user_by_id():
    repository = MockUserRepository()
    user = User(email="test@example.com", password_hash="hash")
    await repository.create(user)
    found = await repository.get_by_id(user.user_id)
    assert found is not None
    assert found.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email():
    repository = MockUserRepository()
    user = User(email="test@example.com", password_hash="hash")
    await repository.create(user)
    found = await repository.get_by_email("test@example.com")
    assert found is not None
    assert found.user_id == user.user_id


@pytest.mark.asyncio
async def test_get_user_not_found():
    repository = MockUserRepository()
    found = await repository.get_by_id(uuid4())
    assert found is None
    found = await repository.get_by_email("nonexistent@example.com")
    assert found is None


@pytest.mark.asyncio
async def test_delete_user():
    repository = MockUserRepository()
    user = User(email="test@example.com", password_hash="hash")
    await repository.create(user)
    deleted = await repository.delete(user.user_id)
    assert deleted is True
    found = await repository.get_by_id(user.user_id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_nonexistent_user():
    repository = MockUserRepository()
    deleted = await repository.delete(uuid4())
    assert deleted is False


def test_user_entity_creation():
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
    assert user.updated_at is not None


def test_user_entity_update():
    user = User(
        email="test@example.com",
        password_hash="hashed",
        full_name="Old Name"
    )
    original_updated_at = user.updated_at
    user.update(full_name="New Name")
    assert user.full_name == "New Name"
    assert user.updated_at >= original_updated_at


def test_user_entity_with_custom_id():
    custom_id = uuid4()
    user = User(
        email="test@example.com",
        password_hash="hashed",
        user_id=custom_id
    )
    assert user.user_id == custom_id
