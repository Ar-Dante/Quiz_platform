from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_email: str
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_status: Optional[str] = 'active'
    user_city: Optional[str] = None
    user_phone: Optional[str] = None
    user_links: Optional[str] = None
    user_avatar: Optional[str] = None
    is_superuser: Optional[bool] = False


class UserCreate(BaseModel):
    password: str


class UserUpdate(BaseModel):
    user_email: str
    user_firstname: str
    user_lastname: str
    user_city: str
    user_phone: str


class UserDetail(BaseModel):
    user_id: int
    user_firstname: str
    user_lastname: str


class SignInRequest(BaseModel):
    user_email: str
    password: str


class SignUpRequestModel(BaseModel):
    user_email: str
    user_firstname: str
    user_lastname: str
    hashed_password: str


class UsersListResponse(BaseModel):
    users: list[UserDetail]


class UserDetailResponse(BaseModel):
    user: UserDetail
