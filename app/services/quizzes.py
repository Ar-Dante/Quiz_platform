from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_ACCESS, ERROR_MEMBER_NOT_EXISTS, ERROR_QUIZ_NOT_FOUND, ERROR_NOT_ENOUGH_QUESTIONS, \
    ERROR_MEMBER_NOT_FOUND
from app.schemas.quizzes_schemas import QuizCreateModel, QuizUpdateModel
from app.utils.repository import AbstractRepository


class QuizService:
    def __init__(self, quizzes_repo: AbstractRepository):
        self.quizzes_repo: AbstractRepository = quizzes_repo()

    async def create_quiz(self, company: dict, data: QuizCreateModel, member: dict, current_user: int):
        await self.valid_quiz_access(current_user, member, company)
        quiz_dict = data.model_dump()
        quiz_dict.update({
            "quiz_company_id": company.id,
            "created_by": current_user
        })
        return await self.quizzes_repo.add_one(quiz_dict)

    async def get_quizzes(self, company_id: int, limit: int, offset: int):
        return await self.quizzes_repo.filter_by(limit, offset, {"quiz_company_id": company_id})

    async def get_quiz_by_id(self, quiz_id: int):
        quiz = await self.quizzes_repo.find_by_filter({"id": quiz_id})
        if quiz is None:
            raise HTTPException(status_code=404, detail=ERROR_QUIZ_NOT_FOUND)
        return quiz

    async def update_quiz(self, quiz_id: int, company: dict, data: QuizUpdateModel, member: dict, current_user: int):
        await self.valid_quiz_access(current_user, member, company)
        await self.get_quiz_by_id(quiz_id, company.id)
        quiz_dict = data.model_dump()
        quiz_dict.update({
            "updated_by": current_user
        })
        await self.quizzes_repo.update_by_filter({"id": quiz_id}, quiz_dict)

    async def remove_quiz(self, quiz_id: int, company: dict, member: dict, current_user: int):
        await self.valid_quiz_access(current_user, member, company)
        await self.get_quiz_by_id(quiz_id, company.id)
        return await self.quizzes_repo.delete_by_id(quiz_id)

    async def valid_quiz_access(self, current_user: int, member: dict, company: dict):
        if not member and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_NOT_EXISTS)
        if company.owner_id != current_user and not member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)

    async def quizz_submit(self,
                           questions: list[dict],
                           user_answer: list[str],
                           member: dict,
                           company: dict,
                           current_user: int) -> dict:
        if member is None and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEMBER_NOT_FOUND)
        if len(questions) < 2:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_NOT_ENOUGH_QUESTIONS)
        correct_answers = 0
        for i, question in enumerate(questions):
            if i < len(user_answer):
                if user_answer[i] == question.question_correct_answer:
                    correct_answers += 1
        return {"correct_answers": correct_answers, "total_answers": len(questions)}
