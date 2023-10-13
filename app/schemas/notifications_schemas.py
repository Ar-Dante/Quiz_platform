from pydantic import BaseModel


class NotificationsDetail(BaseModel):
    id: int
    user_id: int
    text: str
    is_read: bool
