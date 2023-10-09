from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_MEMBER_NOT_EXISTS, ERROR_ACCESS, ERROR_QUESTION_NOT_FOUND, ERROR_NOT_ENOUGH_OPTIONS
from app.schemas.questions_schemas import QuestionCreateModel, QuestionUpdateModel
from app.utils.repository import AbstractRepository


class QuestionService:
    def __init__(self, questions_repo: AbstractRepository):
        self.questions_repo: AbstractRepository = questions_repo()

    async def create_question(self,
                              quiz: dict,
                              data: QuestionCreateModel,
                              member: dict,
                              company: dict,
                              current_user: int):
        await self.valid_question_access(current_user, member, company)
        if len(data.question_answers) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=ERROR_NOT_ENOUGH_OPTIONS)
        question_dict = data.model_dump()
        question_dict.update({
            "question_quiz_id": quiz.id,
            "question_company_id": quiz.quiz_company_id,
            "created_by": current_user
        })
        return await self.questions_repo.add_one(question_dict)

    async def update_question(self,
                              question_id: int,
                              quiz_id: int,
                              company: dict,
                              data: QuestionUpdateModel,
                              member: dict,
                              current_user: int):
        await self.valid_question_access(current_user, member, company)
        await self.get_question_by_id(quiz_id, question_id)
        if len(data.question_answers) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=ERROR_NOT_ENOUGH_OPTIONS)
        quiz_dict = data.model_dump()
        quiz_dict.update({
            "updated_by": current_user
        })
        await self.questions_repo.update_by_filter({"id": question_id}, quiz_dict)

    async def remove_question(self,
                              question_id: int,
                              quiz_id: int,
                              company: dict,
                              member: dict,
                              current_user: int):
        await self.valid_question_access(current_user, member, company)
        await self.get_question_by_id(quiz_id, question_id)
        await self.questions_repo.delete_by_id(question_id)

    async def get_question_by_id(self,
                                 quiz_id: int,
                                 question_id: int):
        question = await self.questions_repo.find_by_filter({"id": question_id, "question_quiz_id": quiz_id})
        if question is None:
            raise HTTPException(status_code=404, detail=ERROR_QUESTION_NOT_FOUND)
        return question

    async def get_questions(self, quizz_id: int, limit: int = 100, offset: int = 0):
        return await self.questions_repo.filter_by(limit, offset, {"question_quiz_id": quizz_id})

    async def valid_question_access(self,
                                    current_user: int,
                                    member: dict,
                                    company: dict):
        if not member and company.owner_id != current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MEMBER_NOT_EXISTS)
        if company.owner_id != current_user and not member.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS)
