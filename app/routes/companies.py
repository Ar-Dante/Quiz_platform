import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.repository.dependencies import company_service
from app.schemas.company_schemas import CompanyCreate, CompanyDetail, CompanyUpdate
from app.services.auth import auth_service
from app.services.companies import CompanyService

route = APIRouter(prefix="/companies", tags=["Companies"])


@route.post("/CreateCompany", status_code=status.HTTP_201_CREATED)
async def create_company(body: CompanyCreate,
                         companies_service: CompanyService = Depends(company_service),
                         current_user: dict = Depends(auth_service.get_current_user)):
    company = await companies_service.create_company(body, current_user.id)
    logging.info(f"Company {company} was created")
    return f"User id:{company}"


@route.get("/", response_model=List[CompanyDetail])
async def get_companies(
        limit: int = Query(10, le=300),
        offset: int = 0,
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    return await companies_service.get_companies(limit, offset, current_user.id)


@route.get("/{company_id}", response_model=CompanyDetail)
async def read_company(company_id: int,
                       companies_service: CompanyService = Depends(company_service),
                       current_user: dict = Depends(auth_service.get_current_user)):
    return await companies_service.get_company_by_id(company_id, current_user.id)


@route.put("/{company_id}", response_model=CompanyUpdate)
async def update_company(
        company_id: int,
        company_update: CompanyUpdate,
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    await companies_service.update_company(company_id, company_update, current_user.id)
    logging.info(f"User {company_id} was changed")
    return await companies_service.get_company_by_id(company_id)


@route.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
        company_id: int,
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    await companies_service.delete_company(company_id, current_user.id)
    logging.info(f"User {company_id} was changed")
