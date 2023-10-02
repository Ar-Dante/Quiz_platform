from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    hashed_password: str

    @validator('hashed_password', always=True)
    def validate_password(cls, value):
        min_length = 8
        if len(value) < min_length:
            raise ValueError('Password must be at least 8 characters long. ')
        if not any(character.isupper() for character in value):
            raise ValueError('Password should contain at least one uppercase character.')
        return value


class UserCreate(BaseModel):
    password: str


class UserUpdate(UserBase):
    user_firstname: str
    user_lastname: str
    user_city: str
    user_phone: str


class UserDetail(BaseModel):
    user_email: str
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None


class SignInRequest(BaseModel):
    user_email: EmailStr
    hashed_password: str


class SignUpRequestModel(UserBase):
    user_email: EmailStr
    user_firstname: str
    user_lastname: str


class UsersListResponse(BaseModel):
    users: list[UserDetail]


class UserDetailResponse(BaseModel):
    user: UserDetail
