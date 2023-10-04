from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_COMPANY_NOT_FOUND, ERROR_ACCESS
from app.schemas.company_schemas import CompanyCreate, CompanyUpdate
from app.utils.repository import AbstractRepository


class CompanyService:
    def __init__(self, companies_repo: AbstractRepository):
        self.companies_repo: AbstractRepository = companies_repo()

    async def create_company(self, company: CompanyCreate, owner_id: int):
        company_dict = company.model_dump()
        company_dict["owner_id"] = owner_id
        return await self.companies_repo.add_one(company_dict)

    async def get_companies(self, limit: int, offset: int, current_user: int):
        companies = await self.companies_repo.find_all(limit, offset)
        return [company for company in companies if company.is_visible or current_user == company.owner_id]

    async def get_company_by_id(self, company_id: int, current_user: int):
        filter_by = {"id": company_id}
        company = await self.companies_repo.find_by_filter(filter_by)
        if company is None or (not company.is_visible and current_user != company.owner_id):
            raise HTTPException(status_code=404, detail=ERROR_COMPANY_NOT_FOUND)
        return await self.companies_repo.find_by_filter(filter_by)

    async def update_company(self, company_id: int, company_data: CompanyUpdate, current_user: int):
        company_dict = company_data.model_dump()
        filter_by = {"id": company_id}
        company = await self.companies_repo.find_by_filter(filter_by)
        if company is None:
            raise HTTPException(status_code=404, detail=ERROR_COMPANY_NOT_FOUND)
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        return await self.companies_repo.update_by_filter(filter_by, company_dict)

    async def delete_company(self, company_id: int, current_user: int):
        filter_by = {"id": company_id}
        company = await self.companies_repo.find_by_filter(filter_by)
        if company is None:
            raise HTTPException(status_code=404, detail=ERROR_COMPANY_NOT_FOUND)
        if current_user != company.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        await self.companies_repo.delete_by_id(company_id)
