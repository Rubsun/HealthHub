import pytest
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def sample_user_id():
    return uuid4()


@pytest.fixture
def sample_email():
    return "test@example.com"


@pytest.fixture
def sample_password():
    return "testpassword123"


@pytest.fixture
def sample_user_data(sample_email, sample_password):
    return {
        "email": sample_email,
        "password": sample_password,
        "full_name": "Test User"
    }



