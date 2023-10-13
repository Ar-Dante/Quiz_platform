from fastapi import APIRouter, Depends

from app.repository.dependencies import results_service, quizzes_service, company_service, comp_memb_service
from app.services.auth import auth_service
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.quizzes import QuizService
from app.services.results import ResultsService

route = APIRouter(prefix="/analitics", tags=["Analitics"])


@route.get("/get_last_attempt_times_for_all_quizzes")
async def get_last_attempt_times_for_all_quizzes(results_srvice: ResultsService = Depends(results_service),
                                                 quizzes_service: QuizService = Depends(quizzes_service)
                                                 ):
    quizzes = await quizzes_service.get_all_quizzes()
    return await results_srvice.get_last_attempt_times_for_all_quizzes(quizzes)


@route.get("/get_average_quiz_by_time")
async def get_average_quiz_by_time(results_srvice: ResultsService = Depends(results_service),
                                   quizzes_service: QuizService = Depends(quizzes_service)
                                   ):
    quizzes = await quizzes_service.get_all_quizzes()
    return await results_srvice.get_average_quiz_by_time(quizzes)


@route.get("/get_last_attempt_times_for_all_users/{company_id}")
async def get_last_attempt_times_for_all_users(company_id: int,
                                               results_srvice: ResultsService = Depends(results_service),
                                               comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                                               companies_service: CompanyService = Depends(company_service),
                                               current_user: dict = Depends(auth_service.get_current_user),
                                               ):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    users = await comp_memb_service.get_company_members(company.id)
    return await results_srvice.get_last_attempt_times_for_all_users(users, current_user.id, member, company)


@route.get("/get_average_users_by_time/{company_id}")
async def get_average_users_by_time(company_id: int,
                                    results_srvice: ResultsService = Depends(results_service),
                                    comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                                    companies_service: CompanyService = Depends(company_service),
                                    current_user: dict = Depends(auth_service.get_current_user),
                                    ):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    users = await comp_memb_service.get_company_members(company.id)
    return await results_srvice.get_average_users_by_time(users, current_user.id, member, company)


@route.get("/get_average_quizz_for_user_in_company_by_time/{company_id}/{user_id}")
async def get_average_quizz_for_user_in_company_by_time(user_id: int,
                                                        company_id: int,
                                                        results_srvice: ResultsService = Depends(results_service),
                                                        comp_memb_service: CompanyMembersService = Depends(
                                                            comp_memb_service),
                                                        companies_service: CompanyService = Depends(company_service),
                                                        quizzes_service: QuizService = Depends(quizzes_service),
                                                        current_user: dict = Depends(auth_service.get_current_user),
                                                        ):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(user_id, company_id)
    quizzes = await quizzes_service.get_all_quizzes()
    return await results_srvice.get_average_quizz_for_user_in_company_by_time(user_id,
                                                                              quizzes,
                                                                              current_user.id,
                                                                              member,
                                                                              company)
