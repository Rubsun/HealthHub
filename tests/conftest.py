import pytest
import sys
from uuid import uuid4
from datetime import datetime


def pytest_configure(config):
    modules_to_clear = [key for key in sys.modules.keys() if key.startswith('domain')]
    for mod in modules_to_clear:
        del sys.modules[mod]


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
