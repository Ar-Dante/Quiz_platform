import random
import string

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from app.conf.messages import ERROR_USER_NOT_FOUND, ERROR_ACCOUNT_EXISTS, ERROR_ACCESS
from app.schemas.user_schemas import SignUpRequestModel, UserUpdate
from app.utils.repository import AbstractRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersService:
    def __init__(self, users_repo: AbstractRepository):
        self.users_repo: AbstractRepository = users_repo()

    async def add_user(self, user: SignUpRequestModel):
        user_email = await self.find_user_by_email(user.user_email)
        if user_email is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ERROR_ACCOUNT_EXISTS)
        user_dict = user.model_dump()
        return await self.users_repo.add_one(user_dict)

    async def get_users(self, limit: int, offset: int):
        return await self.users_repo.find_all(limit, offset)

    async def get_user_by_id(self, user_id: int):
        filter_by = {"id": user_id}
        user = await self.users_repo.find_by_filter(filter_by)
        if user is None:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        return await self.users_repo.find_by_filter(filter_by)

    async def update_user(self, user_id: int, user_data: UserUpdate, current_user: int):
        user_dict = user_data.model_dump()
        filter_by = {"id": user_id}
        user = await self.users_repo.find_by_filter(filter_by)
        if user is None:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        return await self.users_repo.update_by_filter(filter_by, user_dict)

    async def delete_user(self, user_id: int, current_user: int):
        filter_by = {"id": user_id}
        user = await self.users_repo.find_by_filter(filter_by)
        if user is None:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
        await self.users_repo.delete_by_id(user_id)

    async def find_user_by_email(self, email: str):
        filter_by = {"user_email": email}
        return await self.users_repo.find_by_filter(filter_by)

    async def create_user_from_auth0(self, email: str):
        random_chars = ''.join(random.choices(string.ascii_letters.upper() + string.digits, k=10))
        random_password = f"fake_password{random_chars}"
        hash_pass = pwd_context.hash(random_password)
        user_data = {
            "user_email": email,
            "hashed_password": hash_pass
        }
        return await self.users_repo.add_one(user_data)
