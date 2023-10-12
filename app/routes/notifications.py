import logging
from typing import List

from fastapi import APIRouter, Depends

from app.repository.dependencies import notifications_service
from app.schemas.notifications_schemas import NotificationsDetail
from app.services.auth import auth_service
from app.services.notifications import NotificationsService

route = APIRouter(prefix="/notifications", tags=["Notifications"])


# response_model=List[NotificationsDetail]
@route.get("/Notifications/{user_id}", response_model=List[NotificationsDetail])
async def get_notifications(
        user_id: int,
        current_user: dict = Depends(auth_service.get_current_user),
        notification_service: NotificationsService = Depends(notifications_service)):
    return await notification_service.get_notifications(user_id, current_user.id)


@route.put("/ReadNotifications/{user_id}")
async def read_notification(
        user_id: int,
        notification_id: int,
        notification_service: NotificationsService = Depends(notifications_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    logging.info(f"Notification  {notification_id} was readed")
    await notification_service.read_notification(notification_id, user_id, current_user.id)
    return f"Notification  {notification_id} was readed"
