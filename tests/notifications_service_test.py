import pytest
from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_ACCESS
from app.repository.company_members import CompanyMembersRepository
from app.repository.notifications import NotificationsRepository
from app.services.company_members import CompanyMembersService
from app.services.notifications import NotificationsService

notifications_service = NotificationsService(NotificationsRepository)
comp_memb_service = CompanyMembersService(CompanyMembersRepository)


@pytest.mark.asyncio
async def test_add_notifications_about_create_quizz():
    company_id = 1
    members = await comp_memb_service.get_all_members(company_id)
    quiz_id = 2

    result = await notifications_service.add_notifications_about_create_quizz(members, quiz_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_notifications():
    user_id = 1
    current_user = 1
    result = await notifications_service.get_notifications(user_id, current_user)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_notifications_user_id_not_equal_current_user():
    user_id = 1
    current_user = 2

    with pytest.raises(HTTPException) as exc_info:
        await notifications_service.get_notifications(user_id, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_read_notifications_user_id_not_equal_current_user():
    user_id = 1
    current_user = 2
    notification_id = 1

    with pytest.raises(HTTPException) as exc_info:
        await notifications_service.read_notification(notification_id, user_id, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_read_notifications_about_create_quizz():
    current_user = 1
    user_id = 1
    notification_id = 1

    result = await notifications_service.read_notification(notification_id, user_id, current_user)

    assert result is None
