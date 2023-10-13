import pytest
from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_MEMBER_OWNER_ADMIN, ERROR_ACCESS, ERROR_MEMBER_NOT_ADMIN
from app.repository.company_members import CompanyMembersRepository
from app.services.company_members import CompanyMembersService
from tests.companies_servise_test import company_service

company_members_service = CompanyMembersService(CompanyMembersRepository)


@pytest.mark.asyncio
async def test_add_member():
    user_id = 3
    company_id = 1
    result = await company_members_service.add_member(user_id, company_id)
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_exit_from_company_success():
    user_id = 1
    company_id = 1
    current_user = 1

    result = company_members_service.exit_from_company(user_id, company_id, current_user)
    assert result is not None


@pytest.mark.asyncio
async def test_get_member():
    user_id = 1
    company_id = 1
    result = await company_members_service.get_member(user_id, company_id)
    assert result is not None


@pytest.mark.asyncio
async def test_get_company_members():
    company_id = 1
    limit = 10
    offset = 0
    result = await company_members_service.get_company_members(company_id, limit, offset)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_company_members():
    company_id = 1
    result = await company_members_service.get_all_members(company_id)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_remove_member():
    company_id = 1
    current_user = 1
    company = await company_service.get_company_by_id(company_id, current_user)
    user_id = 2
    result = await company_members_service.delete_from_company(user_id, company, current_user)
    assert result is None


@pytest.mark.asyncio
async def test_add_admin():
    company_id = 1
    current_user = 1
    company = await company_service.get_company_by_id(company_id, current_user)
    user_id = 2
    result = await company_members_service.add_admin(user_id, company, current_user)
    assert result is None


@pytest.mark.asyncio
async def test_add_admin_user_id_equals_current_user():
    user_id = 1
    company_id = 1
    current_user = 1
    company = await company_service.get_company_by_id(company_id, current_user)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.add_admin(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_MEMBER_OWNER_ADMIN


@pytest.mark.asyncio
async def test_add_admin_current_user_not_equal_company_owner():
    user_id = 1
    company_id = 1
    current_user = 2
    company = await company_service.get_company_by_id(company_id, current_user)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.add_admin(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_remove_admin():
    user_id = 2
    company_id = 1
    current_user = 1
    company = await company_service.get_company_by_id(company_id, current_user)
    await company_members_service.add_admin(user_id, company, current_user)
    result = await company_members_service.remove_admin(user_id, company, current_user)

    assert result is None


@pytest.mark.asyncio
async def test_remove_admin_user_not_admin():
    user_id = 3
    company_id = 1
    current_user = 1
    company = await company_service.get_company_by_id(company_id, current_user)

    with pytest.raises(HTTPException) as exc_info:
        await company_members_service.remove_admin(user_id, company, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_MEMBER_NOT_ADMIN


@pytest.mark.asyncio
async def test_get_company_admins():
    company_id = 1
    limit = 10
    offset = 0

    result = await company_members_service.get_company_admins(company_id, limit, offset)

    assert isinstance(result, list)
