from fastapi import HTTPException
from passlib.context import CryptContext

from app.conf.messages import ERROR_USER_NOT_FOUND
from app.schemas.user_schemas import SignUpRequestModel, UserUpdate
from app.utils.repository import AbstractRepository

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersService:
    def __init__(self, users_repo: AbstractRepository):
        self.users_repo: AbstractRepository = users_repo()

    async def add_user(self, user: SignUpRequestModel):
        user_dict = user.model_dump()
        user_dict["hashed_password"] = self._hash_password(user_dict["hashed_password"])
        return await self.users_repo.add_one(user_dict)

    async def get_users(self, limit: int, offset: int):
        return await self.users_repo.find_all(limit, offset)

    async def get_user_by_id(self, user_id: int):
        filter_by = {"id": user_id}
        user = await self.users_repo.find_by_filter(filter_by)
        if user is None:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate):
        user_dict = user_data.model_dump()
        filter_by = {"id": user_id}
        user = await self.users_repo.find_by_filter(filter_by)
        if user is None:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        return await self.users_repo.update_by_filter(filter_by, user_dict)

    async def delete_user(self, user_id: int):
        filter_by = {"id": user_id}
        user = await self.users_repo.find_by_filter(filter_by)
        if user is None:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        await self.users_repo.delete_by_id(user_id)

    async def find_user_by_email(self, email: str):
        filter_by = {"user_email": email}
        return await self.users_repo.find_by_filter(filter_by)

    def _hash_password(self, password: str):
        return password_context.hash(password)
