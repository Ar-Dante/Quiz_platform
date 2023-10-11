from app.db.models import Question
from app.utils.repository import SQLAlchemyRepository


class QuestionsRepository(SQLAlchemyRepository):
    model = Question
