from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS
from app.utils.repository import AbstractRepository


class NotificationsService:
    def __init__(self, notifications_repo: AbstractRepository):
        self.notifications_repo: AbstractRepository = notifications_repo()

    async def _validate_notification_access(self, user_id: int, current_user: int):
        if user_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)

    async def add_notifications_about_create_quizz(self, members: list, quiz_id: int):
        for user in members:
            await self.notifications_repo.add_one({"user_id": user.user_id,
                                                   "text": f"Quiz {quiz_id} was created, you can submit it!!!"})

    async def get_notifications(self, user_id: int, current_user: int):
        await self._validate_notification_access(user_id, current_user)
        return await self.notifications_repo.filter({"user_id": user_id})

    async def read_notification(self, notification_id: int, user_id: int, current_user: int):
        await self._validate_notification_access(user_id, current_user)
        await self.notifications_repo.update_by_filter({"id": notification_id}, {"is_read": True})
