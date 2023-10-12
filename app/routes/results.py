from fastapi import APIRouter, Depends

from app.repository.dependencies import results_service, users_service, company_service, comp_memb_service
from app.schemas.results_schemas import GetResultsByFormat, AverageSystemModel, AverageCompanyModel
from app.services.auth import auth_service
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.redis import redis_service
from app.services.results import ResultsService
from app.services.users import UsersService

route = APIRouter(prefix="/results", tags=["Results"])


@route.get("/{user_id}/system-average-rating", response_model=AverageSystemModel)
async def get_system_average_rating(user_id: int,
                                    users_service: UsersService = Depends(users_service),
                                    results_srvice: ResultsService = Depends(results_service)):
    user = await users_service.get_user_by_id(user_id)
    return AverageSystemModel(system_average_rating=await results_srvice.get_system_average_rating(user.id))


@route.get("/{company_id}/{user_id}/average-rating", response_model=AverageCompanyModel)
async def company_average_rating(company_id: int,
                                 user_id: int,
                                 users_service: UsersService = Depends(users_service),
                                 results_srvice: ResultsService = Depends(results_service),
                                 comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                                 companies_service: CompanyService = Depends(company_service),
                                 current_user: dict = Depends(auth_service.get_current_user)):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    user = await users_service.get_user_by_id(user_id)
    return AverageCompanyModel(company_average_rating=await results_srvice.get_user_average_rating_in_company(user.id,
                                                                                                              company.id,
                                                                                                              member,
                                                                                                              company,
                                                                                                              current_user.id))


@route.post("/user_results/{user_id}")
async def get_user_results(user_id: int, upload_format: GetResultsByFormat,
                           users_service: UsersService = Depends(users_service),
                           current_user: dict = Depends(auth_service.get_current_user)):
    user = await users_service.get_user_by_id(user_id)
    return await redis_service.get_user_results(user.id, current_user.id, upload_format.save_format)


@route.post("/user_company_results/{user_id}/{company_id}")
async def get_user_results_for_company(user_id: int,
                                       company_id: int,
                                       upload_format: GetResultsByFormat,
                                       current_user: dict = Depends(auth_service.get_current_user),
                                       users_service: UsersService = Depends(users_service),
                                       comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                                       companies_service: CompanyService = Depends(company_service)):
    user = await users_service.get_user_by_id(user_id)
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    return await redis_service.get_user_results_for_company(user.id,
                                                            current_user.id,
                                                            member,
                                                            company,
                                                            upload_format.save_format)


@route.post("/all_company_results/{company_id}")
async def get_all_results_for_company(company_id: int,
                                      upload_format: GetResultsByFormat,
                                      current_user: dict = Depends(auth_service.get_current_user),
                                      comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                                      companies_service: CompanyService = Depends(company_service)):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    return await redis_service.get_all_results_for_company(company.id,
                                                           current_user.id,
                                                           member,
                                                           company,
                                                           upload_format.save_format)


@route.post("/quizz_company_results/{company_id}/{quizz_id}")
async def get_quiz_results_for_company(company_id: int,
                                       quiz_id: int,
                                       upload_format: GetResultsByFormat,
                                       current_user: dict = Depends(auth_service.get_current_user),
                                       comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                                       companies_service: CompanyService = Depends(company_service)):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    return await redis_service.get_quiz_results_for_company(quiz_id,
                                                            current_user.id,
                                                            member,
                                                            company,
                                                            upload_format.save_format)
