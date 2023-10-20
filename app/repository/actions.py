from app.db.models import UsersCompaniesActions
from app.utils.repository import SQLAlchemyRepository


class ActionsRepository(SQLAlchemyRepository):
    model = UsersCompaniesActions
