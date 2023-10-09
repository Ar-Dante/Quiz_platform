from pydantic import BaseModel


class ActionBase(BaseModel):
    user_id: int
    company_id: int
    action: str
