from passlib.context import CryptContext

from app.repository.users import UsersRepository
from app.schemas.user_schemas import SignUpRequestModel, UserUpdate
from app.utils.repository import AbstractRepository

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def users_service():
    return UsersService(UsersRepository)


class UsersService:
    def __init__(self, users_repo: AbstractRepository):
        self.users_repo: AbstractRepository = users_repo()

    async def add_user(self, user: SignUpRequestModel):
        user_dict = user.model_dump()
        user_dict["hashed_password"] = self._hash_password(user_dict["hashed_password"])
        user_id = await self.users_repo.add_one(user_dict)
        return user_id

    async def get_users(self, limit: int, offset: int):
        users = await self.users_repo.find_all(limit, offset)
        return users

    async def get_user_by_id(self, user_id: int):
        user = await self.users_repo.find_by_id(user_id)
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate):
        user_dict = user_data.model_dump()
        res = await self.users_repo.update_by_id(user_id, user_dict)
        return res

    async def delete_user(self, user_id: int):
        res = await self.users_repo.delete_by_id(user_id)

    async def find_user_by_email(self, email: str):
        user = await self.users_repo.find_by_email(email)
        return user

    def _hash_password(self, password: str):
        return password_context.hash(password)
