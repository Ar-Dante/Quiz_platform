from pydantic import BaseModel


class MemberBase(BaseModel):
    user_id: int
    is_admin: bool
