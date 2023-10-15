from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_ACCESS, ERROR_USER_INVITED, ERROR_USER_NOT_REQUESTED, ERROR_USER_NOT_INVITED
from app.db.models import User, Company
from app.repository.actions import ActionsRepository
from app.services.actions import ActionService

action_service = ActionService(ActionsRepository)


@pytest.mark.asyncio
async def test_send_invitation_success():
    user_id = 2
    company_id = 1
    current_user = User(id=1)
    company = Company(id=company_id, owner_id=current_user.id)
    action_service.get_actions = AsyncMock(return_value=None)
    action_service.actions_repo.add_one = AsyncMock(return_value=1)
    result = await action_service.send_invitation(user_id, company_id, current_user, company, None)

    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_send_invitation_forbidden():
    user_id = 2
    company_id = 1
    current_user = User(id=1)
    company = Company(id=company_id, owner_id=2)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.send_invitation(user_id, company_id, current_user, company, None)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_send_invitation_user_invited():
    user_id = 2
    company_id = 1
    current_user = User(id=1)
    company = Company(id=company_id, owner_id=1)
    action_service.get_actions = AsyncMock(return_value=[{"action": "invitation_sent"}])
    with pytest.raises(HTTPException) as exc_info:
        await action_service.send_invitation(user_id, company_id, current_user, company, None)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_USER_INVITED


@pytest.mark.asyncio
async def test_send_request_success():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = User(id=2)
    action_service.get_actions = AsyncMock(return_value=None)
    action_service.actions_repo.add_one = AsyncMock(return_value=1)
    result = await action_service.send_request(user_id, company, current_user, None)
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_send_request_forbidden():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = User(id=1)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.send_request(user_id, company, current_user, None)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_cancel_request_success():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 1
    action_service.get_actions = AsyncMock(return_value=[{"action": "request_sent"}])
    action_service.actions_repo.update_by_filter = AsyncMock(return_value=1)
    result = await action_service.cancel_request(user_id, company, current_user)
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_cancel_request_forbidden():
    user_id = 2
    company = Company(id=1, owner_id=2)
    current_user = User(id=1)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.cancel_request(user_id, company, current_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_cancel_request_not_found():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 1
    action_service.get_actions = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.cancel_request(user_id, company, current_user)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_REQUESTED


@pytest.mark.asyncio
async def test_get_company_invitations_success():
    company_id = 1
    limit = 10
    offset = 0
    current_user = 1
    action_service.actions_repo.filter_by = AsyncMock(return_value=[{"action": "invitation_sent"}])
    result = await action_service.get_company_invitations(company_id, limit, offset, current_user)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_get_company_invitations_forbidden():
    company_id = 1
    limit = 10
    offset = 0
    current_user = 2
    with pytest.raises(HTTPException) as exc_info:
        await action_service.get_company_invitations(company_id, limit, offset, current_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_user_invitations_success():
    user_id = 1
    limit = 10
    offset = 0
    current_user = 1
    action_service.actions_repo.filter_by = AsyncMock(return_value=[{"action": "invitation_sent"}])

    result = await action_service.get_user_invitations(user_id, limit, offset, current_user)

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_get_user_invitations_forbidden():
    company_id = 1
    limit = 10
    offset = 0
    current_user = 2
    with pytest.raises(HTTPException) as exc_info:
        await action_service.get_user_invitations(company_id, limit, offset, current_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_user_requests_success():
    user_id = 1
    limit = 10
    offset = 0
    current_user = 1
    action_service.actions_repo.filter_by = AsyncMock(return_value=[{"action": "request_sent"}])

    result = await action_service.get_user_requests(user_id, limit, offset, current_user)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_cancel_invitation_success():
    user_id = 1
    company = Company(id=1, owner_id=1)
    current_user = 1
    action_service.get_actions = AsyncMock(
        return_value=[{"user_id": user_id, "company_id": company.id, "action": "invitation_sent"}])

    action_service.actions_repo.update_by_filter = AsyncMock()
    result = await action_service.cancel_invitation(user_id, company, current_user)
    assert result is not None


@pytest.mark.asyncio
async def test_cancel_invitation_user_not_invited():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 2

    action_service.get_actions = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.cancel_invitation(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_INVITED


@pytest.mark.asyncio
async def test_accept_invitation_success():
    user_id = 1
    company_id = 1
    current_user = 1
    action_service.get_actions = AsyncMock(
        return_value=[{"user_id": user_id, "company_id": company_id, "action": "invitation_sent"}])
    action_service.actions_repo.update_by_filter = AsyncMock()

    result = await action_service.accept_invitation(user_id, company_id, current_user)

    assert result is not None


@pytest.mark.asyncio
async def test_accept_invitation_user_not_invited():
    user_id = 1
    company_id = 1
    current_user = 1

    action_service.get_actions = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await action_service.accept_invitation(user_id, company_id, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_INVITED


@pytest.mark.asyncio
async def test_refuse_invitation_success():
    user_id = 1
    company_id = 1
    current_user = 1
    action_service.get_actions = AsyncMock(
        return_value=[{"user_id": user_id, "company_id": company_id, "action": "invitation_sent"}])
    result = await action_service.refuse_invitation(user_id, company_id, current_user)

    assert result is not None


@pytest.mark.asyncio
async def test_refuse_invitation_access_denied():
    user_id = 1
    company_id = 1
    current_user = 2
    action_service.get_actions = AsyncMock(
        return_value=[{"user_id": user_id, "company_id": company_id, "action": "invitation_sent"}])

    with pytest.raises(HTTPException) as exc_info:
        await action_service.refuse_invitation(user_id, company_id, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_refuse_invitation_no_invitation_found():
    user_id = 1
    company_id = 1
    current_user = 1
    action_service.get_actions = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.refuse_invitation(user_id, company_id, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_INVITED


@pytest.mark.asyncio
async def test_accept_request_success():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 2

    action_service.get_actions = AsyncMock(
        return_value=[{"user_id": user_id, "company_id": company.id, "action": "request_sent"}])

    result = await action_service.accept_request(user_id, company, current_user)

    assert result is not None


@pytest.mark.asyncio
async def test_accept_request_user_not_requested():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 2
    action_service.get_actions = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.accept_request(user_id, company, current_user)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_REQUESTED


@pytest.mark.asyncio
async def test_accept_request_success():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 2

    action_service.get_actions = AsyncMock(
        return_value=[{"user_id": user_id, "company_id": company.id, "action": "request_sent"}])

    result = await action_service.accept_request(user_id, company, current_user)

    assert result is None


@pytest.mark.asyncio
async def test_accept_request_user_not_requested():
    user_id = 1
    company = Company(id=1, owner_id=2)
    current_user = 2

    action_service.get_actions = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await action_service.accept_request(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_USER_NOT_REQUESTED
