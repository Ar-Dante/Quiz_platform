from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    user_email: str
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None


class UserCreate(BaseModel):
    password: str


class UserUpdate(BaseModel):
    user_email: EmailStr
    user_firstname: str
    user_lastname: str
    user_city: str
    user_phone: str


class UserDetail(BaseModel):
    user_id: int
    user_firstname: str
    user_lastname: str


class SignInRequest(BaseModel):
    user_email: EmailStr
    hashed_password: str


class SignUpRequestModel(BaseModel):
    user_email: EmailStr
    user_firstname: str
    user_lastname: str
    hashed_password: str


class UsersListResponse(BaseModel):
    users: list[UserDetail]


class UserDetailResponse(BaseModel):
    user: UserDetail
