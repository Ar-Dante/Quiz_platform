from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    user_email: str
    user_firstname: Optional[str]
    user_lastname: Optional[str]
    user_status: str
    user_city: Optional[str]
    user_phone: Optional[str]
    user_links: Optional[str]
    user_avatar: Optional[str]


class UserCreate(UserBase):
    hashed_password: str
    is_superuser: bool


class UserUpdate(UserBase):
    pass


class UserDetail(UserBase):
    pass


class UserSignInRequest(BaseModel):
    user_email: str
    password: str


class UserListResponse(BaseModel):
    users = List[UserBase]
