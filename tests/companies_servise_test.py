from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_COMPANY_NOT_FOUND, ERROR_ACCESS
from app.db.models import Company
from app.repository.companies import CompanyRepository
from app.schemas.company_schemas import CompanyCreate, CompanyUpdate
from app.services.companies import CompanyService

company_service = CompanyService(CompanyRepository)


@pytest.mark.asyncio
async def test_create_company():
    company = CompanyCreate(
        company_name="Test Company",
        company_description="A test company",
    )
    owner_id = 1

    company_service.companies_repo.add_one = AsyncMock(return_value=1)

    result = await company_service.create_company(company, owner_id)

    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_get_companies():
    limit = 10
    offset = 0
    current_user = 1

    companies = [
        Company(id=1, is_visible=True, owner_id=1),
        Company(id=2, is_visible=False, owner_id=2),
        Company(id=3, is_visible=True, owner_id=3),
    ]

    company_service.companies_repo.find_all = AsyncMock(return_value=companies)

    result = await company_service.get_companies(limit, offset, current_user)

    assert len(result) == 2
    assert all(company.is_visible or current_user == company.owner_id for company in result)


@pytest.mark.asyncio
async def test_get_company_by_id():
    company_id = 1
    current_user = 1
    company = Company(id=1, is_visible=True, owner_id=1)
    company_service.companies_repo.find_by_filter = AsyncMock(return_value=company)
    result = await company_service.get_company_by_id(company_id, current_user)

    assert result == company


@pytest.mark.asyncio
async def test_get_company_by_id_not_found():
    company_id = 1
    current_user = 1

    company_service.companies_repo.find_by_filter = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await company_service.get_company_by_id(company_id, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_COMPANY_NOT_FOUND


@pytest.mark.asyncio
async def test_update_company_exists():
    company_id = 1
    current_user = 1
    company_data = CompanyUpdate(
        company_name="New Name",
        company_title="New Title",
        company_description="New Description",
        company_city="New City",
        company_phone="New Phone",
        is_visible=True
    )

    company = Company(
        id=1,
        owner_id=1,
        company_name="Old Name",
        company_title="Old Title",
        company_description="Old Description",
        company_city="Old City",
        company_phone="Old Phone",
        is_visible=False
    )

    company_service.companies_repo.find_by_filter = AsyncMock(return_value=company)
    company_service.companies_repo.update_by_filter = AsyncMock(return_value=1)

    result = await company_service.update_company(company_id, company_data, current_user)

    assert isinstance(result, int)
    assert result == 1


@pytest.mark.asyncio
async def test_update_company_exists_not_owner():
    company_id = 1
    current_user = 2
    company_data = CompanyUpdate(
        company_name="New Name",
        company_title="New Title",
        company_description="New Description",
        company_city="New City",
        company_phone="New Phone",
        is_visible=True
    )

    company = Company(
        id=1,
        owner_id=1,
        company_name="Old Name",
        company_title="Old Title",
        company_description="Old Description",
        company_city="Old City",
        company_phone="Old Phone",
        is_visible=False
    )

    company_service.companies_repo.find_by_filter = AsyncMock(return_value=company)

    with pytest.raises(HTTPException) as exc_info:
        await company_service.update_company(company_id, company_data, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_delete_company_exists_and_owner():
    company_id = 1
    current_user = 1

    company = Company(
        id=1,
        owner_id=1
    )

    company_service.companies_repo.find_by_filter = AsyncMock(return_value=company)
    company_service.companies_repo.delete_by_id = AsyncMock()

    await company_service.delete_company(company_id, current_user)


@pytest.mark.asyncio
async def test_delete_company_exists_not_owner():
    company_id = 1
    current_user = 2

    company = Company(
        id=1,
        owner_id=1
    )

    company_service.companies_repo.find_by_filter = AsyncMock(return_value=company)

    with pytest.raises(HTTPException) as exc_info:
        await company_service.delete_company(company_id, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS
