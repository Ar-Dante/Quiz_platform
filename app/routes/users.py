import logging
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from app.conf.messages import ERROR_USER_NOT_FOUND, ERROR_EMAIL_EXISTS
from app.repository.dependencies import users_service
from app.schemas.user_schemas import SignUpRequestModel, UserUpdate, UserBase
from app.services.users import UsersService

route = APIRouter(prefix="/users", tags=["Users"])


@route.post("/SingUp", status_code=status.HTTP_201_CREATED)
async def create_user(
        body: SignUpRequestModel,
        users_service: UsersService = Depends(users_service),
):
    user_email = await users_service.find_user_by_email(body.user_email)
    if user_email is not None:
        raise HTTPException(status_code=422, detail=ERROR_EMAIL_EXISTS)
    user = await users_service.add_user(body)
    logging.info(f"User {user} was created")
    return f"User id:{user}"


@route.get("/", response_model=List[UserBase])
async def get_users(
        limit: int = Query(10, le=300),
        offset: int = 0,
        users_service: UsersService = Depends(users_service),
):
    return await users_service.get_users(limit, offset)


@route.get("/{user_id}", response_model=UserBase)
async def read_user(user_id: int, users_service: UsersService = Depends(users_service)):
    user = await users_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    return user


@route.put("/{user_id}", response_model=UserUpdate)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        users_service: UsersService = Depends(users_service),
):
    user = await users_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    await users_service.update_user(user_id, user_update)
    logging.info(f"User {user_id} was changed")
    return await users_service.get_user_by_id(user_id)


@route.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int, users_service: UsersService = Depends(users_service)
):
    user = await users_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    await users_service.delete_user(user_id)
    logging.info(f"User {user_id} was deleted")
    return f"User {user_id} was deleted"
