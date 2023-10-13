from datetime import datetime

from app.repository.companies import CompanyRepository
from app.repository.company_members import CompanyMembersRepository
from app.repository.notifications import NotificationsRepository
from app.repository.quizzes import QuizzesRepository
from app.repository.results import ResultsRepository
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.notifications import NotificationsService
from app.services.quizzes import QuizService
from app.services.results import ResultsService


async def schedule_notification_sender():
    companies_service = CompanyService(CompanyRepository)
    quizzes_service = QuizService(QuizzesRepository)
    comp_memb_service = CompanyMembersService(CompanyMembersRepository)
    notification_service = NotificationsService(NotificationsRepository)
    results_service = ResultsService(ResultsRepository)
    companies = await companies_service.get_all_companies()
    user_list = []
    company_list = []
    for company in companies:
        members = await comp_memb_service.get_all_members(company.id)
        quizzes = await quizzes_service.get_quizzes(company.id, 1000, 0)
        company_list.append(company.id)
        for user in members:
            for quiz in quizzes:
                last_attempt_date = await results_service.get_last_attempt_time_for_user_quiz(user.user_id, quiz.id)
                user_list.append((last_attempt_date, quiz.id, user.user_id))
                if last_attempt_date:
                    days_since_last_attempt = (datetime.utcnow() - last_attempt_date).days
                    if days_since_last_attempt >= quiz.quiz_frequency:
                        await notification_service.add_notifications_about_time_to_quizz(user.user_id, quiz.id)
