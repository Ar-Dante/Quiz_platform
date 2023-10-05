import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.repository.dependencies import company_service, action_service, comp_memb_service, users_service
from app.schemas.actions_schemas import ActionBase
from app.schemas.company_memb_schemas import MemberBase
from app.schemas.company_schemas import CompanyCreate, CompanyDetail, CompanyUpdate
from app.services.actions import ActionService
from app.services.auth import auth_service
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.users import UsersService

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


@route.get("/company_members/{company_id}", response_model=List[MemberBase])
async def get_company_members(
        company_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    return await comp_memb_service.get_company_members(company, limit, offset)


@route.get("/company_admins/{company_id}", response_model=List[MemberBase])
async def get_company_admins(
        company_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    return await comp_memb_service.get_company_admins(company, limit, offset)


@route.get("/{company_id}", response_model=CompanyDetail)
async def read_company(company_id: int,
                       companies_service: CompanyService = Depends(company_service),
                       current_user: dict = Depends(auth_service.get_current_user)):
    return await companies_service.get_company_by_id(company_id, current_user.id)


@route.get("/company_invitations/{company_id}", response_model=List[ActionBase])
async def get_company_invitations(
        company_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        actions_service: ActionService = Depends(action_service),
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    return await actions_service.get_company_invitations(company, limit, offset, current_user.id)


@route.get("/company_requests/{company_id}", response_model=List[ActionBase])
async def get_company_requests(
        company_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        actions_service: ActionService = Depends(action_service),
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    return await actions_service.get_company_requests(company, limit, offset, current_user.id)


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


@route.post("/send_invitation/{user_id}/{company_id}")
async def send_invitation(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        actions_service: ActionService = Depends(action_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service)
):
    member = await comp_memb_service.get_member(user_id, company_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    user = await users_service.get_user_by_id(user_id)
    await actions_service.send_invitation(user.id, company_id, current_user.id, company, member)
    logging.info(f"User {user_id} was invited")
    return f"User {user_id} was invited"


@route.put("/cancel_invitation/{user_id}/{company_id}")
async def cancel_invitation(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        actions_service: ActionService = Depends(action_service),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await actions_service.cancel_invitation(user.id, company, current_user.id)
    logging.info(f"Invitation for user: {user_id} was canceled")
    return f"Invitation for user:{user_id} was canceled"


@route.put("/accept_request/{user_id}/{company_id}")
async def accept_request(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        actions_service: ActionService = Depends(action_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    user = await users_service.get_user_by_id(user_id)
    await actions_service.accept_request(user.id, company, current_user.id)
    await comp_memb_service.add_member(user_id, company_id)
    logging.info(f"Request from user: {user_id} was accepted")
    return f"Request from user: {user_id} was accepted"


@route.put("/refuse_request/{user_id}/{company_id}")
async def refuse_request(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        actions_service: ActionService = Depends(action_service),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await actions_service.refuse_request(user.id, company, current_user.id)
    logging.info(f"Request from user: {user_id} was refused")
    return f"Request from user: {user_id} was refused"


@route.put("/add_admin/{user_id}/{company_id}")
async def add_admin(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await comp_memb_service.add_admin(user.id, company, current_user.id)
    logging.info(f"User: {user_id} was named admin in company: {company_id}")
    return f"User: {user_id} was named admin in company: {company_id}"


@route.delete("/remove_member/{user_id}/{company_id}")
async def remove_member(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await comp_memb_service.delete_from_company(user.id, company, current_user.id)
    logging.info(f"User: {user_id} was removed from company: {company_id}")
    return f"User: {user_id} was removed from company: {company_id}"


@route.delete("/remove_admin/{user_id}/{company_id}")
async def remove_admin(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        companies_service: CompanyService = Depends(company_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await comp_memb_service.remove_admin(user.id, company, current_user.id)
    logging.info(f"User: {user_id} has been removed from the admins in company: {company_id}")
    return f"User: {user_id} has been removed from the admins in company: {company_id}"
