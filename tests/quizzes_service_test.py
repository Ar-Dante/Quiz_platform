from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi import status

from app.conf.messages import ERROR_MEMBER_NOT_EXISTS, ERROR_QUIZ_NOT_FOUND, ERROR_ACCESS
from app.db.models import Company, CompanyMembers, Quiz, Question
from app.repository.companies import CompanyRepository
from app.repository.company_members import CompanyMembersRepository
from app.repository.questions import QuestionsRepository
from app.repository.quizzes import QuizzesRepository
from app.schemas.quizzes_schemas import QuizCreateModel, QuizUpdateModel
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.questions import QuestionService
from app.services.quizzes import QuizService

question_service = QuestionService(QuestionsRepository)
company_members_service = CompanyMembersService(CompanyMembersRepository)
company_service = CompanyService(CompanyRepository)
quizz_service = QuizService(QuizzesRepository)


@pytest.mark.asyncio
async def test_create_quiz_successful():
    data = QuizCreateModel(quiz_name="New Quiz", quiz_frequency=7)
    member = CompanyMembers(user_id=1, company_id=2, is_admin=True)
    company = Company(id=2, owner_id=2)
    current_user = 1

    quizz_service.quizzes_repo.add_one = AsyncMock(return_value={"quiz_id": 1})

    result = await quizz_service.create_quiz(company, data, member, current_user)
    assert result == {"quiz_id": 1}


@pytest.mark.asyncio
async def test_create_quiz_member_not_exists():
    data = QuizCreateModel(quiz_name="New Quiz", quiz_frequency=7)
    member = None
    company = Company(id=2, owner_id=2)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.create_quiz(company, data, member, current_user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_MEMBER_NOT_EXISTS


@pytest.mark.asyncio
async def test_get_quizzes_successful():
    company_id = 1
    limit = 10
    offset = 0
    quizzes = [
        Quiz(id=1, quiz_company_id=1, quiz_name="Quiz 1"),
        Quiz(id=2, quiz_company_id=1, quiz_name="Quiz 2"),
    ]
    quizz_service.quizzes_repo.filter_by = AsyncMock(return_value=quizzes)
    result = await quizz_service.get_quizzes(company_id, limit, offset)
    assert result == quizzes


@pytest.mark.asyncio
async def test_get_all_quizzes():
    limit = 10
    offset = 0
    expected_quizzes = [Quiz(id=1, quiz_company_id=1), Quiz(id=2, quiz_company_id=1)]
    quizz_service.quizzes_repo.find_all = AsyncMock(return_value=expected_quizzes)

    result = await quizz_service.get_all_quizzes(limit, offset)

    assert result == expected_quizzes


@pytest.mark.asyncio
async def test_get_quiz_by_id():
    quiz_id = 1

    expected_quiz = Quiz(id=quiz_id, quiz_company_id=1)
    quizz_service.quizzes_repo.find_by_filter = AsyncMock(return_value=expected_quiz)

    result = await quizz_service.get_quiz_by_id(quiz_id)

    assert result == expected_quiz


@pytest.mark.asyncio
async def test_get_quiz_by_id_error():
    quiz_id = 1
    quizz_service.quizzes_repo.find_by_filter = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.get_quiz_by_id(quiz_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == ERROR_QUIZ_NOT_FOUND


@pytest.mark.asyncio
async def test_update_quiz():
    quiz_id = 1
    company = {"company_data": "value"}
    data = QuizUpdateModel(quiz_name="Updated Quiz Name", quiz_description="Updated Description",
                           quiz_title="Updated Title", quiz_frequency=7)
    member = {"member_data": "value"}
    current_user = 1
    quizz_service.valid_quiz_access = AsyncMock()
    quizz_service.get_quiz_by_id = AsyncMock()
    quizz_service.quizzes_repo.update_by_filter = AsyncMock()

    result = await quizz_service.update_quiz(quiz_id, company, data, member, current_user)

    assert result is None


@pytest.mark.asyncio
async def test_remove_quiz():
    quiz_id = 1
    company = {"company_data": "value"}
    member = {"member_data": "value"}
    current_user = 1
    quizz_service.valid_quiz_access = AsyncMock()
    quizz_service.get_quiz_by_id = AsyncMock()
    quizz_service.quizzes_repo.delete_by_id = AsyncMock()

    result = await quizz_service.remove_quiz(quiz_id, company, member, current_user)

    assert result is not None


@pytest.mark.asyncio
async def test_remove_quiz_with_error():
    quiz_id = 1
    company = {"company_data": "value"}
    member = {"member_data": "value"}
    current_user = 1
    quizz_service.valid_quiz_access = AsyncMock(
        side_effect=HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ACCESS))
    quizz_service.get_quiz_by_id = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.remove_quiz(quiz_id, company, member, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_quizz_submit_success():
    questions = [
        Question(question_correct_answer="A"),
        Question(question_correct_answer="B"),
        Question(question_correct_answer="C")
    ]
    user_answer = ["A", "B", "C"]
    member = {"member_data": "value"}
    company = {"company_data": "value"}
    current_user = 1

    result = await quizz_service.quizz_submit(questions, user_answer, member, company, current_user)

    assert result == {"correct_answers": 3, "total_answers": 3}


@pytest.mark.asyncio
async def test_quizz_submit_not_enough_questions_and_member_not_found():
    questions = [
        Question(question_correct_answer="A")
    ]
    user_answer = ["A"]
    member = None
    company = Company(owner_id=2)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.quizz_submit(questions, user_answer, member, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_quizz_submit_no_member_and_owner_not_current_user():
    questions = [
        Question(question_correct_answer="A"),
        Question(question_correct_answer="B"),
        Question(question_correct_answer="C")
    ]
    user_answer = ["A", "B", "C"]
    member = None
    company = Company(owner_id=2)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.quizz_submit(questions, user_answer, member, company, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
