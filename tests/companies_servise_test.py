import pytest
from fastapi import HTTPException

from app.db.models import Company
from app.repository.companies import CompanyRepository
from app.schemas.company_schemas import CompanyCreate, CompanyUpdate
from app.services.companies import CompanyService

company_service = CompanyService(CompanyRepository)


@pytest.mark.asyncio
async def test_create_company():
    company_data = CompanyCreate(
        company_name="Test Company",
        company_title="Test Title",
        company_description="Test Description",
        company_city="Test City",
        company_phone="123-456-7890"
    )
    result = await company_service.create_company(company_data, 1)
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_get_companies():
    result = await company_service.get_companies(limit=10, offset=0, current_user={"id": 1})
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_company_by_id():
    company_id = 1
    current_user = 1
    result = await company_service.get_company_by_id(company_id, current_user)
    assert isinstance(result, Company)


@pytest.mark.asyncio
async def test_get_company_by_id_with_none():
    company_id = 1
    current_user = 1

    async def mock_find_by_filter(filter_by):
        return None

    company_service.companies_repo.find_by_filter = mock_find_by_filter
    with pytest.raises(HTTPException) as exc_info:
        await company_service.get_company_by_id(company_id, current_user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_company_success():
    company_id = 1
    current_user = 1
    company_data = CompanyUpdate(
        company_name="Updated Company Name",
        company_title="Updated Company Title",
        company_description="Updated Company Description",
        company_city="Updated Company City",
        company_phone="Updated Company Phone",
        is_visible=True
    )

    async def mock_update_by_filter(filter_by, company_dict):
        updated_company = {
            "company_name": company_data.company_name,
            "company_title": company_data.company_title,
            "company_description": company_data.company_description,
            "company_city": company_data.company_city,
            "company_phone": company_data.company_phone,
            "is_visible": company_data.is_visible
        }
        return updated_company

    company_service.companies_repo.update_by_filter = mock_update_by_filter

    result = await company_service.update_company(company_id, company_data, current_user)

    assert result["company_name"] == "Updated Company Name"
    assert result["company_title"] == "Updated Company Title"
    assert result["company_description"] == "Updated Company Description"
    assert result["company_city"] == "Updated Company City"
    assert result["company_phone"] == "Updated Company Phone"
    assert result["is_visible"] == True


@pytest.mark.asyncio
async def test_update_company_not_found():
    company_service = CompanyService(CompanyRepository)

    company_id = 2
    current_user = 1
    company_data = CompanyUpdate(
        company_name="Updated Company Name",
        company_title="Updated Company Title",
        company_description="Updated Company Description",
        company_city="Updated Company City",
        company_phone="Updated Company Phone",
        is_visible=True
    )

    async def mock_find_by_filter(filter_by):
        if filter_by.get("id") == 1:
            return {"id": 1, "owner_id": 1}
        else:
            return None

    company_service.companies_repo.find_by_filter = mock_find_by_filter

    with pytest.raises(HTTPException) as exc_info:
        await company_service.update_company(company_id, company_data, current_user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_company_success():
    company_id = 1
    current_user = 1

    async def mock_delete_by_id(company_id):
        if company_id == 1:
            return True
        else:
            return False

    company_service.companies_repo.delete_by_id = mock_delete_by_id

    result = await company_service.delete_company(company_id, current_user)
    assert result == None


@pytest.mark.asyncio
async def test_delete_company_not_found():
    company_id = 2
    current_user = 1

    async def mock_find_by_filter(filter_by):
        if filter_by.get("id") == 1:
            return {"id": 1, "owner_id": 1}
        else:
            return None

    company_service.companies_repo.find_by_filter = mock_find_by_filter

    with pytest.raises(HTTPException) as exc_info:
        await company_service.delete_company(company_id, current_user)
    assert exc_info.value.status_code == 404
