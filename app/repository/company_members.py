from app.db.models import CompanyMembers
from app.utils.repository import SQLAlchemyRepository


class CompanyMembersRepository(SQLAlchemyRepository):
    model = CompanyMembers
