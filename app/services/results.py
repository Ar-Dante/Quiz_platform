from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_MEMBER_NOT_FOUND, ERROR_USER_NOT_FOUND, ERROR_MEMBER_NOT_EXISTS, ERROR_ACCESS
from app.db.models import Result
from app.utils.repository import AbstractRepository


class ResultsService:
    def __init__(self, results_repo: AbstractRepository):
        self.results_repo: AbstractRepository = results_repo()

    async def valid_result_access(self, current_user: int, member: dict, company: dict):
        if not member and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_NOT_EXISTS)
        if company.owner_id != current_user and not member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)

    async def calculate_average_rating(self, user_results):
        total_right_count = sum(result.result_right_count for result in user_results)
        total_total_count = sum(result.result_total_count for result in user_results)
        return total_right_count / total_total_count if total_total_count > 0 else 0.0

    async def add_results(self,
                          quiz_id: int,
                          company_id: int,
                          current_user: int,
                          correct_count: int,
                          total_count: int):
        await self.results_repo.add_one({
            "result_user_id": current_user,
            "result_company_id": company_id,
            "result_quiz_id": quiz_id,
            "result_right_count": correct_count,
            "result_total_count": total_count,
        })

    async def get_user_average_rating_in_company(self,
                                                 user_id: int,
                                                 company_id: int,
                                                 member: dict,
                                                 company: dict,
                                                 current_user: int) -> int:
        if member is None and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)

        user_results = await self.results_repo.filter(
            {
                "result_user_id": user_id,
                "result_company_id": company_id,
            }
        )
        if not user_results:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        return await self.calculate_average_rating(user_results)

    async def get_system_average_rating(self,
                                        user_id: int) -> int:
        user_results = await self.results_repo.filter(
            {
                "result_user_id": user_id,
            }
        )
        if not user_results:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        return await self.calculate_average_rating(user_results)

    async def get_last_attempt_times_for_all_quizzes(self, quizzes: list):
        quiz_last_attempt_times = []

        for quiz in quizzes:
            last_attempt_date = await self.results_repo.get_max_by_filter(Result.created_at,
                                                                          {"result_quiz_id": quiz.id})

            quiz_last_attempt_times.append({
                "quiz_id": quiz.id,
                "quiz_name": quiz.quiz_name,
                "last_attempt_date": last_attempt_date,
            })

        return quiz_last_attempt_times

    async def get_average_quiz_by_time(self, quizzes: list):
        average_quiz = []

        for quiz in quizzes:
            last_attempt_date = await self.results_repo.get_max_by_filter(Result.created_at,
                                                                          {"result_quiz_id": quiz.id})
            quizz = await self.results_repo.filter({"result_quiz_id": quiz.id})
            average_quizz = await self.calculate_average_rating(quizz)

            average_quiz.append({
                "quiz_id": quiz.id,
                "average_quizz": average_quizz,
                "last_attempt_date": last_attempt_date,
            })

        return average_quiz

    async def get_last_attempt_times_for_all_users(self, users: list, current_user: int, member: dict, company: dict):
        await self.valid_result_access(current_user, member, company)
        user_last_attempt_times = []

        for user in users:
            last_attempt_date = await self.results_repo.get_max_by_filter(Result.created_at,
                                                                          {"result_user_id": user.id})

            user_last_attempt_times.append({
                "user_id": user.user_id,
                "last_attempt_date": last_attempt_date,
            })

        return user_last_attempt_times

    async def get_average_users_by_time(self, users: list, current_user: int, member: dict, company: dict):
        await self.valid_result_access(current_user, member, company)
        average_users = []

        for user in users:
            last_attempt_date = await self.results_repo.get_max_by_filter(Result.created_at,
                                                                          {"result_user_id": user.user_id})
            userss = await self.results_repo.filter({"result_user_id": user.user_id})
            average_user = await self.calculate_average_rating(userss)

            average_users.append({
                "user_id": user.user_id,
                "average_user": average_user,
                "last_attempt_date": last_attempt_date,
            })

        return average_users

    async def get_average_quizz_for_user_in_company_by_time(self,
                                                            users_id: int,
                                                            quizzes: list,
                                                            current_user: int,
                                                            member: dict,
                                                            company: dict):
        await self.valid_result_access(current_user, member, company)
        average_quiz = []

        for quiz in quizzes:
            last_attempt_date = await self.results_repo.get_max_by_filter(Result.created_at,
                                                                          {"result_quiz_id": quiz.id})
            userss = await self.results_repo.filter({"result_quiz_id": quiz.id,
                                                     "result_user_id": users_id,
                                                     "result_company_id": company.id})
            average_user = await self.calculate_average_rating(userss)

            average_quiz.append({
                "user_id": users_id,
                "company_id": company.id,
                "result_quiz_id": quiz.id,
                "average_user": average_user,
                "last_attempt_date": last_attempt_date,
            })

        return average_quiz
