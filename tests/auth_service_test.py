from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from starlette import status

from app.conf.messages import ERROR_INVALID_CRED
from app.db.models import User
from app.repository.users import UsersRepository
from app.services.auth import Auth
from app.services.users import UsersService

auth_service = Auth()
user_service = UsersService(UsersRepository)


@pytest.mark.asyncio
async def test_verify_password():
    plain_password = "test_password"
    hashed_password = auth_service.pwd_context.hash(plain_password)

    auth_service.pwd_context.verify = AsyncMock(return_value=True)
    assert await auth_service.verify_password(plain_password, hashed_password) is True

    auth_service.pwd_context.verify = AsyncMock(return_value=False)
    assert await auth_service.verify_password("wrong_password", hashed_password) is False


@pytest.mark.asyncio
async def test_get_password_hash():
    plain_password = "test_password"

    auth_service.pwd_context.hash = AsyncMock(return_value="hashed_password")
    hashed_password = await auth_service.get_password_hash(plain_password)

    assert hashed_password == "hashed_password"


@pytest.mark.asyncio
async def test_create_access_token():
    data = {"user_id": 1, "username": "test_user"}
    expires_delta = 3600

    jwt.encode = AsyncMock(return_value="encoded_access_token")

    access_token = await auth_service.create_access_token(data, expires_delta)
    assert await access_token == "encoded_access_token"


@pytest.mark.asyncio
async def test_decode_auth0_token():
    token = "example_token"
    email = "test@example.com"

    jwt.decode = Mock(return_value={"https://example.com/email": email})
    user_service.find_user_by_email = AsyncMock(return_value={"user_email": email})
    user_service.create_user_from_auth0 = AsyncMock(return_value=1)

    result = await auth_service.decode_auth0_token(token, user_service)

    assert result == email


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    token = "valid_token"
    email = "test@example.com"

    jwt.decode = Mock(return_value={"scope": "access_token", "sub": email})
    user_service.find_user_by_email = AsyncMock(return_value={"user_email": email})

    result = await auth_service.get_current_user(token, user_service)

    assert result == {"user_email": email}


@pytest.mark.asyncio
async def test_SingIn_valid_credentials():
    body = OAuth2PasswordRequestForm(username="test@example.com", password="password")
    user = User(
        user_email="test@example.com",
        hashed_password="hashed_password"
    )

    user_service.find_user_by_email = AsyncMock(return_value=user)
    auth_service.verify_password = AsyncMock(return_value=True)
    auth_service.create_access_token = AsyncMock(return_value="access_token")

    result = await auth_service.SingIn(body, user_service)

    assert result == {"access_token": "access_token", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_SignIn_invalid_credentials():
    body = OAuth2PasswordRequestForm(username="test@example.com", password="password")

    user_service.find_user_by_email = AsyncMock(return_value=None)
    auth_service.verify_password = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.SingIn(body, user_service)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == ERROR_INVALID_CRED
