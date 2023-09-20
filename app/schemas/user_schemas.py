from pydantic import BaseModel


class UserBase(BaseModel):
    user_email: str
    user_firstname: str
    user_lastname: str
    user_status: str
    user_city: str
    user_phone: str
    user_links: str
    user_avatar: str


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
    pass
