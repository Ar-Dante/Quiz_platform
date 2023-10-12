from app.db.models import Result
from app.utils.repository import SQLAlchemyRepository


class ResultsRepository(SQLAlchemyRepository):
    model = Result
