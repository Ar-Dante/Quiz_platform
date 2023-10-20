import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.repository.dependencies import users_service, action_service, company_service, comp_memb_service
from app.schemas.actions_schemas import ActionBase
from app.schemas.user_schemas import UserUpdate, SignUpRequestModel, UserDetail
from app.services.actions import ActionService
from app.services.auth import auth_service
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.users import UsersService

route = APIRouter(prefix="/users", tags=["Users"])


@route.post("/SingUp", status_code=status.HTTP_201_CREATED)
async def SingUp(body: SignUpRequestModel,
                 users_service: UsersService = Depends(users_service)):
    body.hashed_password = auth_service.get_password_hash(body.hashed_password)
    user = await users_service.add_user(body)
    logging.info(f"User {user} was created")
    return f"User id:{user}"


@route.get("/", response_model=List[UserDetail])
async def get_users(
        limit: int = Query(10, le=300),
        offset: int = 0,
        users_service: UsersService = Depends(users_service),
):
    return await users_service.get_users(limit, offset)


@route.get("/{user_id}", response_model=UserDetail)
async def read_user(user_id: int, users_service: UsersService = Depends(users_service)):
    return await users_service.get_user_by_id(user_id)


@route.get("/user_invitations/{company_id}", response_model=List[ActionBase])
async def get_user_invitations(
        user_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        actions_service: ActionService = Depends(action_service),
        current_user: dict = Depends(auth_service.get_current_user),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    return await actions_service.get_user_invitations(user.id, limit, offset, current_user.id)


@route.get("/user_requests/{company_id}", response_model=List[ActionBase])
async def get_user_requests(
        user_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        actions_service: ActionService = Depends(action_service),
        current_user: dict = Depends(auth_service.get_current_user),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    return await actions_service.get_user_requests(user.id, limit, offset, current_user.id)


@route.put("/{user_id}", response_model=UserUpdate)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        users_service: UsersService = Depends(users_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    user_update.hashed_password = auth_service.get_password_hash(user_update.hashed_password)
    await users_service.update_user(user_id, user_update, current_user)
    logging.info(f"User {user_id} was changed")
    return await users_service.get_user_by_id(user_id)


@route.put("/invite_ok/{user_id}/{company_id}")
async def accept_invitation(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        actions_service: ActionService = Depends(action_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service),
        companies_service: CompanyService = Depends(company_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await actions_service.accept_invitation(user.id, company.id, current_user.id)
    await comp_memb_service.add_member(user.id, company_id)
    logging.info(f"Invitation for user: {user_id} was accepted")
    return f"Invitation for user:{user_id} was accepted"


@route.put("/invite_not/{user_id}/{company_id}")
async def refuse_invitation(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        actions_service: ActionService = Depends(action_service),
        users_service: UsersService = Depends(users_service),
        companies_service: CompanyService = Depends(company_service)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    user = await users_service.get_user_by_id(user_id)
    await actions_service.refuse_invitation(user.id, company.id, current_user.id)
    logging.info(f"Invitation for user: {user_id} was refused")
    return f"Invitation for user:{user_id} was refused"


@route.post("/request_send/{user_id}/{company_id}")
async def send_request(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        actions_service: ActionService = Depends(action_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service),
        companies_service: CompanyService = Depends(company_service),
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(user.id, company_id)
    await actions_service.send_request(user.id, company, current_user.id, member)
    logging.info(f"Request to company: {company_id} was sent")
    return f"Request to company: {company_id} was sent"


@route.put("/request_cancel/{user_id}/{company_id}")
async def cancel_request(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        actions_service: ActionService = Depends(action_service),
        companies_service: CompanyService = Depends(company_service),
        users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await actions_service.cancel_request(user.id, company, current_user.id)
    logging.info(f"Request to company: {company_id} was canceled")
    return f"Request to company: {company_id} was canceled"


@route.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        users_service: UsersService = Depends(users_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    await users_service.delete_user(user_id, current_user.id)
    logging.info(f"User {user_id} was deleted")


@route.delete("/exit_from_company/{user_id}/{company_id}")
async def exit_from_company(
        user_id: int,
        company_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        users_service: UsersService = Depends(users_service),
        companies_service: CompanyService = Depends(company_service),

):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    await comp_memb_service.exit_from_company(user.id, company.id, current_user.id)
    logging.info(f"User: {user_id} left company: {company_id}")
    return f"User: {user_id} left company: {company_id}"
