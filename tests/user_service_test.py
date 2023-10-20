from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCOUNT_EXISTS, ERROR_USER_NOT_FOUND, ERROR_ACCESS
from app.db.models import User
from app.repository.users import UsersRepository
from app.schemas.user_schemas import SignUpRequestModel, UserUpdate
from app.services.users import UsersService

user_service = UsersService(UsersRepository)


@pytest.mark.asyncio
async def test_add_user_success():
    test_user = SignUpRequestModel(
        hashed_password="1234567A",
        user_email="test@example.com",
        user_firstname="John",
        user_lastname="Doe"
    )
    user_service.find_user_by_email = AsyncMock(return_value=None)
    user_service.users_repo.add_one = AsyncMock(return_value=1)
    result = await user_service.add_user(test_user)
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_add_user_account_exist():
    test_user = SignUpRequestModel(
        hashed_password="1234567A",
        user_email="test@example.com",
        user_firstname="John",
        user_lastname="Doe"
    )
    user_service.find_user_by_email = AsyncMock(return_value=1)
    user_service.users_repo.add_one = AsyncMock(return_value=1)
    with pytest.raises(HTTPException) as exc_info:
        await user_service.add_user(test_user)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == ERROR_ACCOUNT_EXISTS


@pytest.mark.asyncio
async def test_get_users():
    users_data = [
        {"id": 1, "name": "User1"},
        {"id": 2, "name": "User2"},

    ]
    user_service.users_repo.find_all = AsyncMock(return_value=users_data)
    result = await user_service.get_users(10, 0)
    assert result == users_data


@pytest.mark.asyncio
async def test_get_user_by_id_success():
    user_id = 1
    user_data = {"id": user_id, "name": "User1"}
    user_service.users_repo.find_by_filter = AsyncMock(return_value=user_data)
    result = await user_service.get_user_by_id(user_id)
    assert result == user_data


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    user_id = 2
    user_service.users_repo.find_by_filter = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_user_by_id(user_id)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_FOUND


@pytest.mark.asyncio
async def test_update_user_success():
    user_id = 1
    user_data = UserUpdate(
        hashed_password="1234567A",
        user_firstname="NewFirstName",
        user_lastname="NewLastName",
        user_city="NewCity",
        user_phone="NewPhone"
    )

    user_data_existing = {
        "id": user_id,
        "user_firstname": "ExistingFirstName",
        "user_lastname": "ExistingLastName",
        "user_city": "ExistingCity",
        "user_phone": "ExistingPhone"
    }
    user_service.users_repo.find_by_filter = AsyncMock(return_value=user_data_existing)

    user_service.users_repo.update_by_filter = AsyncMock(return_value=1)

    current_user = User(id=user_id)
    result = await user_service.update_user(user_id, user_data, current_user)
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_update_user_forbidden():
    user_id = 2
    user_data = UserUpdate(
        hashed_password="1234567A",
        user_firstname="NewFirstName",
        user_lastname="NewLastName",
        user_city="NewCity",
        user_phone="NewPhone"
    )

    current_user = User(id=1)
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(user_id, user_data, current_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_update_user_not_found():
    user_id = 2
    user_data = UserUpdate(
        hashed_password="1234567A",
        user_firstname="NewFirstName",
        user_lastname="NewLastName",
        user_city="NewCity",
        user_phone="NewPhone"
    )
    user_service.users_repo.find_by_filter = AsyncMock(return_value=None)
    current_user = User(id=1)

    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(user_id, user_data, current_user)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_user_success():
    user_id = 1
    user_data_existing = {"id": user_id, "name": "User1"}
    user_service.users_repo.find_by_filter = AsyncMock(return_value=user_data_existing)
    user_service.users_repo.delete_by_id = AsyncMock()

    current_user = User(id=user_id)
    result = await user_service.delete_user(user_id, current_user)
    assert result is None


@pytest.mark.asyncio
async def test_delete_user_not_found():
    user_id = 2
    user_service.users_repo.find_by_filter = AsyncMock(return_value=None)
    current_user = User(id=1)
    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete_user(user_id, current_user)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_user_forbidden():
    user_id = 2
    user_data_existing = {"id": user_id, "name": "User2"}
    user_service.users_repo.find_by_filter = AsyncMock(return_value=user_data_existing)

    current_user = User(id=1)
    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete_user(user_id, current_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_find_user_by_email_success():
    email = "test@example.com"
    user_data = {"id": 1, "user_email": email}
    user_service.users_repo.find_by_filter = AsyncMock(return_value=user_data)

    result = await user_service.find_user_by_email(email)
    assert result == user_data["id"]


@pytest.mark.asyncio
async def test_create_user_from_auth0_success():
    email = "test@example.com"
    user_service.users_repo.add_one = AsyncMock(return_value=1)
    result = await user_service.create_user_from_auth0(email)
    assert isinstance(result, int)
