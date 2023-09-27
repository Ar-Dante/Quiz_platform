import logging

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from app.conf.messages import ERROR_USER_NOT_FOUND
from app.repository.dependencies import users_service
from app.schemas.user_schemas import UserUpdate
from app.services.users import UsersService

route = APIRouter(prefix="/users", tags=["Users"])


@route.get("/")
async def get_users(
        limit: int = Query(10, le=300),
        offset: int = 0,
        users_service: UsersService = Depends(users_service),
):
    user = await users_service.get_users(limit, offset)
    return user


@route.get("/{user_id}")
async def read_user(user_id: int, users_service: UsersService = Depends(users_service)):
    user = await users_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    return user


@route.put("/{user_id}")
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        users_service: UsersService = Depends(users_service),
):
    user = await users_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    await users_service.update_user(user_id, user_update)
    update_user = await users_service.get_user_by_id(user_id)
    logging.info(f"User {user_id} was changed")
    return update_user


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
