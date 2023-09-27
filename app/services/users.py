from app.schemas.user_schemas import SignUpRequestModel, UserUpdate
from app.utils.repository import AbstractRepository


class UsersService:
    def __init__(self, users_repo: AbstractRepository):
        self.users_repo: AbstractRepository = users_repo()

    async def add_user(self, user: SignUpRequestModel):
        user_dict = user.model_dump()
        return await self.users_repo.add_one(user_dict)

    async def get_users(self, limit: int, offset: int):
        return await self.users_repo.find_all(limit, offset)

    async def get_user_by_id(self, user_id: int):
        filter_by = {"id": user_id}
        return await self.users_repo.find_by_filter(filter_by)

    async def update_user(self, user_id: int, user_data: UserUpdate):
        user_dict = user_data.model_dump()
        filter_by = {"id": user_id}
        return await self.users_repo.update_by_filter(filter_by, user_dict)

    async def delete_user(self, user_id: int):
        await self.users_repo.delete_by_id(user_id)

    async def find_user_by_email(self, email: str):
        filter_by = {"user_email": email}
        return await self.users_repo.find_by_filter(filter_by)

    async def update_user_token(self, email: str, token: str | None):
        filter_by = {"user_email": email}
        data = {"refresh_token": token}
        return await self.users_repo.update_by_filter(filter_by, data)
