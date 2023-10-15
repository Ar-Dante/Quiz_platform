from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_NOT_ENOUGH_OPTIONS, ERROR_QUESTION_NOT_FOUND, ERROR_MEMBER_NOT_EXISTS
from app.db.models import Quiz, Question, Company
from app.repository.companies import CompanyRepository
from app.repository.company_members import CompanyMembersRepository
from app.repository.questions import QuestionsRepository
from app.repository.quizzes import QuizzesRepository
from app.schemas.questions_schemas import QuestionCreateModel, QuestionUpdateModel
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.questions import QuestionService
from app.services.quizzes import QuizService

question_service = QuestionService(QuestionsRepository)
company_members_service = CompanyMembersService(CompanyMembersRepository)
company_service = CompanyService(CompanyRepository)
quizz_service = QuizService(QuizzesRepository)


@pytest.mark.asyncio
async def test_create_question():
    quiz = Quiz(id=1, quiz_company_id=1)
    data = QuestionCreateModel(question_text="What is 2+2?", question_answers=["3", "4"], question_correct_answer="4")
    member = {"member_data": "value"}
    company = {"company_data": "value"}
    current_user = 1

    question_service.valid_question_access = AsyncMock()
    question_service.questions_repo.add_one = AsyncMock(return_value={"question_id": 1})

    result = await question_service.create_question(quiz, data, member, company, current_user)

    assert result == {"question_id": 1}


@pytest.mark.asyncio
async def test_create_question_not_enough_options():
    quiz = Quiz(id=1, quiz_company_id=1)
    data = QuestionCreateModel(question_text="What is 2+2?", question_answers=["4"], question_correct_answer="4")
    member = {"member_data": "value"}
    company = {"company_data": "value"}
    current_user = 1

    question_service.valid_question_access = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await question_service.create_question(quiz, data, member, company, current_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == ERROR_NOT_ENOUGH_OPTIONS


@pytest.mark.asyncio
async def test_update_question():
    question_id = 1
    quiz_id = 2
    company = {"company_data": "value"}
    data = QuestionUpdateModel(question_text="What is 2+2?", question_answers=["3", "4"], question_correct_answer="4")
    member = {"member_data": "value"}
    current_user = 1

    question_service.valid_question_access = AsyncMock()
    question_service.get_question_by_id = AsyncMock()
    question_service.questions_repo.update_by_filter = AsyncMock()

    await question_service.update_question(question_id, quiz_id, company, data, member, current_user)


@pytest.mark.asyncio
async def test_update_question_errors():
    question_id = 1
    quiz_id = 2
    company = {"company_data": "value"}
    data = QuestionUpdateModel(question_text="What is 2+2?", question_answers=["3"], question_correct_answer="4")
    member = {"member_data": "value"}
    current_user = 1

    question_service.valid_question_access = AsyncMock()
    question_service.get_question_by_id = AsyncMock()
    question_service.questions_repo.update_by_filter = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await question_service.update_question(question_id, quiz_id, company, data, member, current_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == ERROR_NOT_ENOUGH_OPTIONS


@pytest.mark.asyncio
async def test_remove_question():
    question_id = 1
    quiz_id = 1
    company = None
    member = None
    current_user = 1

    question_service.valid_question_access = AsyncMock()
    question_service.get_question_by_id = AsyncMock()
    question_service.questions_repo.delete_by_id = AsyncMock()
    await question_service.remove_question(question_id, quiz_id, company, member, current_user)


@pytest.mark.asyncio
async def test_get_question_by_id_found():
    quiz_id = 1
    question_id = 1
    expected_question = {"id": question_id, "question_quiz_id": quiz_id, "text": "Sample question"}

    question_service.questions_repo.find_by_filter = AsyncMock(return_value=expected_question)

    result = await question_service.get_question_by_id(quiz_id, question_id)

    assert result == expected_question


@pytest.mark.asyncio
async def test_get_question_by_id_not_found():
    quiz_id = 1
    question_id = 1

    question_service.questions_repo.find_by_filter = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await question_service.get_question_by_id(quiz_id, question_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == ERROR_QUESTION_NOT_FOUND


@pytest.mark.asyncio
async def test_get_questions():
    quiz_id = 1
    limit = 10
    offset = 0
    expected_questions = [
        Question(id=1, question_quiz_id=quiz_id, question_text="Question 1"),
        Question(id=2, question_quiz_id=quiz_id, question_text="Question 2"),
    ]

    question_service.questions_repo.filter_by = AsyncMock(return_value=expected_questions)

    result = await question_service.get_questions(quiz_id, limit, offset)

    assert result == expected_questions


@pytest.mark.asyncio
async def test_valid_question_access_member_not_exists():
    current_user = 1
    member = None
    company = Company(id=1, owner_id=2)

    with pytest.raises(HTTPException) as exc_info:
        await question_service.valid_question_access(current_user, member, company)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_MEMBER_NOT_EXISTS
