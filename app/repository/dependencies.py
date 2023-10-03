from app.repository.companies import CompanyRepository
from app.repository.users import UsersRepository
from app.services.companies import CompanyService
from app.services.users import UsersService


def users_service():
    return UsersService(UsersRepository)


def company_service():
    return CompanyService(CompanyRepository)
