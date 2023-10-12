import logging
from typing import List

from fastapi import APIRouter, Depends, Query

from app.repository.dependencies import company_service, quizzes_service, comp_memb_service, questions_service, \
    results_service
from app.schemas.questions_schemas import QuestionCreateModel, QuestionUpdateModel, QuestionDetail
from app.schemas.quizzes_schemas import QuizCreateModel, QuizDetail, QuizUpdateModel
from app.schemas.result_schemas import AverageSystemModel, AverageCompanyModel
from app.services.auth import auth_service, users_service
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.questions import QuestionService
from app.services.quizzes import QuizService
from app.services.results import ResultsService
from app.services.users import UsersService

route = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@route.post("/createQuiz")
async def create_quiz(company_id: int,
                      body: QuizCreateModel,
                      companies_service: CompanyService = Depends(company_service),
                      quizzes_service: QuizService = Depends(quizzes_service),
                      comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                      current_user: dict = Depends(auth_service.get_current_user)
                      ):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    quiz = await quizzes_service.create_quiz(company, body, member, current_user.id)
    logging.info(f"Quiz:{quiz} was created")
    return f"Quiz id:{quiz}"


@route.post("/createQuestion")
async def create_question(company_id: int,
                          quizz_id: int,
                          body: QuestionCreateModel,
                          companies_service: CompanyService = Depends(company_service),
                          quizzes_service: QuizService = Depends(quizzes_service),
                          questions_service: QuestionService = Depends(questions_service),
                          comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                          current_user: dict = Depends(auth_service.get_current_user)
                          ):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    quiz = await quizzes_service.get_quiz_by_id(quizz_id)
    question = await questions_service.create_question(quiz, body, member, company, current_user.id)
    logging.info(f"Question:{question} was created")
    return f"Question id:{question}"


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


@route.post("/SubmitQuestion")
async def submit_quizz(company_id: int,
                       quiz_id: int,
                       body: list[str],
                       companies_service: CompanyService = Depends(company_service),
                       quizzes_service: QuizService = Depends(quizzes_service),
                       questions_service: QuestionService = Depends(questions_service),
                       comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
                       results_srvice: ResultsService = Depends(results_service),
                       current_user: dict = Depends(auth_service.get_current_user)
                       ):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    quiz = await quizzes_service.get_quiz_by_id(quiz_id)
    question = await questions_service.get_questions(quiz.id)
    results = await quizzes_service.quizz_submit(question, body, member, company, current_user.id)
    await results_srvice.add_results(quiz_id, company.id, current_user.id, results["correct_answers"],
                                     results["total_answers"])
    logging.info(f"Total score for user {current_user.id} is {results}")
    return f"Total score for user {current_user.id} is {results}"


@route.get("/Quizzes", response_model=List[QuizDetail])
async def get_quizzes(
        company_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        companies_service: CompanyService = Depends(company_service),
        quizzes_service: QuizService = Depends(quizzes_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    return await quizzes_service.get_quizzes(company.id, limit, offset)


@route.get("/Questions", response_model=List[QuestionDetail])
async def get_questions(
        company_id: int,
        quiz_id: int,
        limit: int = Query(10, le=300),
        offset: int = 0,
        companies_service: CompanyService = Depends(company_service),
        questions_service: QuestionService = Depends(questions_service),
        quizzes_service: QuizService = Depends(quizzes_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    await companies_service.get_company_by_id(company_id, current_user.id)
    quiz = await quizzes_service.get_quiz_by_id(quiz_id)
    return await questions_service.get_questions(quiz.id, limit, offset)


@route.put("/UpdateQuiz/{company_id}/{quiz_id}")
async def update_quiz(
        quiz_id: int,
        company_id: int,
        data: QuizUpdateModel,
        quizzes_service: QuizService = Depends(quizzes_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    logging.info(f"Quiz {quiz_id} was changed")
    await quizzes_service.update_quiz(quiz_id, company, data, member, current_user.id)
    return f"Quiz {quiz_id} was changed"


@route.put("/UpdateQuestion/{quiz_id}/{question_id}")
async def update_question(
        quiz_id: int,
        question_id: int,
        company_id: int,
        data: QuestionUpdateModel,
        quizzes_service: QuizService = Depends(quizzes_service),
        questions_service: QuestionService = Depends(questions_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    quizz = await quizzes_service.get_quiz_by_id(quiz_id, company.id)
    await questions_service.update_question(question_id, quizz.id, company, data, member, current_user.id)
    logging.info(f"Quiz {quiz_id} was changed")
    return f"Quiz {quiz_id} was changed"


@route.delete("/RemoveQuestion/{company_id}/{quiz_id}/{question_id}")
async def remove_question(
        company_id: int,
        quiz_id: int,
        question_id: int,
        quizzes_service: QuizService = Depends(quizzes_service),
        questions_service: QuestionService = Depends(questions_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    quiz = await quizzes_service.get_quiz_by_id(quiz_id, company.id)
    logging.info(f"Question {question_id} was removed")
    await questions_service.remove_question(question_id, quiz.id, company, member, current_user.id)
    return f"Question id:{question_id} was removed"


@route.delete("/RemoveQuiz/{company_id}/{quiz_id}")
async def remove_quiz(
        quiz_id: int,
        company_id: int,
        quizzes_service: QuizService = Depends(quizzes_service),
        comp_memb_service: CompanyMembersService = Depends(comp_memb_service),
        companies_service: CompanyService = Depends(company_service),
        current_user: dict = Depends(auth_service.get_current_user)
):
    company = await companies_service.get_company_by_id(company_id, current_user.id)
    member = await comp_memb_service.get_member(current_user.id, company_id)
    logging.info(f"Quiz {quiz_id} was removed")
    await quizzes_service.remove_quiz(quiz_id, company, member, current_user.id)
    return f"Quiz id:{quiz_id} was removed"
