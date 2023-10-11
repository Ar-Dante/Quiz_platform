from app.db.models import Quiz
from app.utils.repository import SQLAlchemyRepository


class QuizzesRepository(SQLAlchemyRepository):
    model = Quiz
