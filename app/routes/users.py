import logging

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.db import get_db
from app.repository import users
from app.schemas.user_schemas import SignUpRequestModel, UserDetail, UserUpdate

route = APIRouter(prefix="/users", tags=["Users"])


@route.post("/SingUp", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
async def create_user(body: SignUpRequestModel, db: AsyncSession = Depends(get_db)):
    user_email = await users.get_by_email(body.user_email, db)
    if user_email is not None:
        raise HTTPException(status_code=422, detail="User with this email already exists")
    user = await users.create(body, db)
    logging.info(f"User {user.user_id} was created")
    return user


@route.get("/")
async def get_users(limit: int = Query(10, le=300), offset: int = 0, db: AsyncSession = Depends(get_db)):
    user = await users.get(limit, offset, db)
    return user


@route.get("/{user_id}", response_model=UserDetail)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users.get_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@route.put("/{user_id}", response_model=UserUpdate)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    updated_user = await users.update(user_id, user_update, db)

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"User {updated_user.user_id} was changed")
    return updated_user


@route.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted_user = await users.delete(user_id, db)

    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"User {deleted_user.user_id} was deleted")
    return deleted_user
