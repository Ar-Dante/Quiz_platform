import pytest
from fastapi import Depends
from starlette.testclient import TestClient

from app.main import app
from app.repository.dependencies import users_service
from app.services.auth import auth_service


@pytest.fixture
def client():
    return TestClient(app)
