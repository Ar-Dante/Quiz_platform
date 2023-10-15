from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS
from app.db.models import CompanyMembers
from app.repository.company_members import CompanyMembersRepository
from app.repository.notifications import NotificationsRepository
from app.services.company_members import CompanyMembersService
from app.services.notifications import NotificationsService

notifications_service = NotificationsService(NotificationsRepository)
comp_memb_service = CompanyMembersService(CompanyMembersRepository)


@pytest.mark.asyncio
async def test_add_notifications_about_create_quizz():
    members = [
        CompanyMembers(user_id=1, company_id=1, is_admin=True),
        CompanyMembers(user_id=2, company_id=1, is_admin=False),
        CompanyMembers(user_id=3, company_id=1, is_admin=False),
    ]
    quiz_id = 1

    notifications_service.notifications_repo.add_one = AsyncMock()

    await notifications_service.add_notifications_about_create_quizz(members, quiz_id)


@pytest.mark.asyncio
async def test_get_notifications():
    user_id = 1
    current_user = 1

    notifications_service.notifications_repo.filter = AsyncMock(return_value=[{"notification": "content"}])

    notifications = await notifications_service.get_notifications(user_id, current_user)

    assert notifications == [{"notification": "content"}]


@pytest.mark.asyncio
async def test_read_notification():
    notification_id = 1
    user_id = 1
    current_user = 1

    notifications_service.notifications_repo.update_by_filter = AsyncMock()

    await notifications_service.read_notification(notification_id, user_id, current_user)


@pytest.mark.asyncio
async def test_read_notification_access_denied():
    notification_id = 1
    user_id = 1
    current_user = 2

    with pytest.raises(HTTPException) as exc_info:
        await notifications_service.read_notification(notification_id, user_id, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS
