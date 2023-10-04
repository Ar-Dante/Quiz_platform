from app.repository.actions import ActionsRepository
from app.repository.companies import CompanyRepository
from app.repository.company_members import CompanyMembersRepository
from app.repository.users import UsersRepository
from app.services.actions import ActionService
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.users import UsersService


def users_service():
    return UsersService(UsersRepository)


def company_service():
    return CompanyService(CompanyRepository)


def action_service():
    return ActionService(ActionsRepository)


def comp_memb_service():
    return CompanyMembersService(CompanyMembersRepository)
