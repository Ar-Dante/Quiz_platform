from app.db.models import Notification
from app.utils.repository import SQLAlchemyRepository


class NotificationsRepository(SQLAlchemyRepository):
    model = Notification
