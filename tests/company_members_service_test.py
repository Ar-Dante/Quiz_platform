from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_MEMBER_NOT_FOUND
from app.db.models import Company, CompanyMembers
from app.repository.company_members import CompanyMembersRepository
from app.services.company_members import CompanyMembersService

company_members_service = CompanyMembersService(CompanyMembersRepository)


@pytest.mark.asyncio
async def test_add_member():
    user_id = 1
    company_id = 1

    company_members_service.comp_memb_repo.add_one = AsyncMock(return_value=1)

    result = await company_members_service.add_member(user_id, company_id)

    assert isinstance(result, int)
    assert result == 1


@pytest.mark.asyncio
async def test_exit_from_company_member_exists():
    user_id = 1
    company_id = 1
    current_user = 1

    company_members_service.get_member = AsyncMock(return_value={"user_id": user_id, "company_id": company_id})
    company_members_service.comp_memb_repo.delete_by_filter = AsyncMock()

    result = await company_members_service.exit_from_company(user_id, company_id, current_user)

    assert result is not None


@pytest.mark.asyncio
async def test_exit_from_company_member_not_found():
    user_id = 1
    company_id = 1
    current_user = 1

    company_members_service.get_member = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.exit_from_company(user_id, company_id, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_MEMBER_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_from_company_member_exists():
    user_id = 1
    current_user = 1

    company = Company(id=1, owner_id=1)

    company_members_service.get_member = AsyncMock(return_value={"user_id": user_id, "company_id": company.id})
    company_members_service.comp_memb_repo.delete_by_filter = AsyncMock()

    result = await company_members_service.delete_from_company(user_id, company, current_user)

    assert result is not None


@pytest.mark.asyncio
async def test_delete_from_company_member_not_found():
    user_id = 1
    current_user = 1

    company = Company(id=1, owner_id=1)

    company_members_service.get_member = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.delete_from_company(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_MEMBER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_member():
    user_id = 1
    company_id = 1

    company_members_service.comp_memb_repo.find_by_filter = AsyncMock(
        return_value={"user_id": user_id, "company_id": company_id})

    result = await company_members_service.get_member(user_id, company_id)

    assert result == {"user_id": user_id, "company_id": company_id}


@pytest.mark.asyncio
async def test_get_member_member_not_found():
    user_id = 1
    company_id = 1

    company_members_service.comp_memb_repo.find_by_filter = AsyncMock(return_value=None)

    result = await company_members_service.get_member(user_id, company_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_company_members():
    company_id = 1
    limit = 1000
    offset = 0

    expected_members = [
        CompanyMembers(user_id=1, company_id=company_id),
        CompanyMembers(user_id=2, company_id=company_id),
    ]

    company_members_service.comp_memb_repo.filter_by = AsyncMock(return_value=expected_members)

    result = await company_members_service.get_company_members(company_id, limit, offset)

    assert result == expected_members


@pytest.mark.asyncio
async def test_get_all_members():
    company_id = 1

    expected_members = [
        CompanyMembers(user_id=1, company_id=company_id),
        CompanyMembers(user_id=2, company_id=company_id),
    ]

    company_members_service.comp_memb_repo.filter = AsyncMock(return_value=expected_members)

    result = await company_members_service.get_all_members(company_id)

    assert result == expected_members


@pytest.mark.asyncio
async def test_add_admin_success():
    user_id = 1
    company = Company(id=1, owner_id=1)
    current_user = 1

    company_members_service.validate_access_for_admins = AsyncMock()
    company_members_service.get_member = AsyncMock(return_value=CompanyMembers(user_id=user_id, company_id=company.id))
    company_members_service.comp_memb_repo.update_by_filter = AsyncMock(return_value=True)

    result = await company_members_service.add_admin(user_id, company, current_user)

    assert result is True


@pytest.mark.asyncio
async def test_add_admin_member_not_found():
    user_id = 1
    company = Company(id=1, owner_id=1)
    current_user = 1

    company_members_service.validate_access_for_admins = AsyncMock()
    company_members_service.get_member = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.add_admin(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_admin_success():
    user_id = 1
    company = Company(id=1, owner_id=1)
    current_user = 1

    company_members_service.validate_access_for_admins = AsyncMock()
    company_members_service.get_member = AsyncMock(
        return_value=CompanyMembers(user_id=user_id, company_id=company.id, is_admin=True))
    company_members_service.comp_memb_repo.update_by_filter = AsyncMock(return_value=True)

    result = await company_members_service.remove_admin(user_id, company, current_user)

    assert result is True


@pytest.mark.asyncio
async def test_remove_admin_member_not_found():
    user_id = 1
    company = Company(id=1, owner_id=1)
    current_user = 1

    company_members_service.validate_access_for_admins = AsyncMock()
    company_members_service.get_member = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.remove_admin(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_admin_not_admin():
    user_id = 1
    company = Company(id=1, owner_id=1)
    current_user = 1

    company_members_service.validate_access_for_admins = AsyncMock()
    company_members_service.get_member = AsyncMock(
        return_value=CompanyMembers(user_id=user_id, company_id=company.id, is_admin=False))

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.remove_admin(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_company_admins():
    company_id = 1
    limit = 10
    offset = 0

    expected_result = [
        {"user_id": 1, "company_id": 1, "is_admin": True},
        {"user_id": 2, "company_id": 1, "is_admin": True},
    ]

    company_members_service.comp_memb_repo.filter_by = AsyncMock(return_value=expected_result)

    result = await company_members_service.get_company_admins(company_id, limit, offset)

    assert result == expected_result
