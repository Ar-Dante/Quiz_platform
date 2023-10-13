import pytest
from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_MEMBER_NOT_EXISTS, ERROR_QUIZ_NOT_FOUND, ERROR_ACCESS, ERROR_NOT_ENOUGH_QUESTIONS
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
async def test_create_quiz():
    company = await company_service.get_company_by_id(1, 1)
    data = QuizCreateModel(
        quiz_name="Math Quiz",
        quiz_description="Test your math skills",
        quiz_frequency=7
    )
    member = await company_members_service.get_member(1, 1)
    result = await quizz_service.create_quiz(company, data, member, 1)

    assert result is not None
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_create_quiz_member_not_exists():
    company = await company_service.get_company_by_id(1, 1)
    data = QuizCreateModel(
        quiz_name="Math Quiz",
        quiz_description="Test your math skills",
        quiz_frequency=7
    )
    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.create_quiz(company, data, None, 2)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert str(exc_info.value.detail) == ERROR_MEMBER_NOT_EXISTS


@pytest.mark.asyncio
async def test_get_quizzes():
    company_id = 1
    result = await quizz_service.get_quizzes(company_id, 10, 0)
    assert result is not None
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_all_quizzes():
    result = await quizz_service.get_all_quizzes(10, 0)
    assert result is not None
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_quiz_by_id():
    quiz_id = 1
    result = await quizz_service.get_quiz_by_id(quiz_id)

    assert result is not None


@pytest.mark.asyncio
async def test_get_quiz_by_id_not_found():
    quiz_id = 999

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.get_quiz_by_id(quiz_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc_info.value.detail) == ERROR_QUIZ_NOT_FOUND


@pytest.mark.asyncio
async def test_update_quiz():
    company = await company_service.get_company_by_id(1, 1)
    data = QuizUpdateModel(
        quiz_name="Updated Math Quiz",
        quiz_description="Updated math quiz description",
        quiz_frequency=14
    )
    member = await company_members_service.get_member(1, 1)
    result = await quizz_service.update_quiz(1, company, data, member, 1)

    assert result is None


@pytest.mark.asyncio
async def test_update_quiz_member_not_exists():
    company = await company_service.get_company_by_id(2, 1)
    data = QuizUpdateModel(
        quiz_name="Updated Math Quiz",
        quiz_description="Updated math quiz description",
        quiz_frequency=14
    )
    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.update_quiz(1, company, data, None, 1)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert str(exc_info.value.detail) == ERROR_MEMBER_NOT_EXISTS


@pytest.mark.asyncio
async def test_remove_quiz_success():
    quiz_id = 1
    company = await company_service.get_company_by_id(1, 1)
    member = await company_members_service.get_member(1, 1)
    current_user = 1

    result = await quizz_service.remove_quiz(quiz_id, company, member, current_user)

    assert result is None


@pytest.mark.asyncio
async def test_remove_quiz_quiz_not_found():
    quiz_id = 999
    company = await company_service.get_company_by_id(1, 1)
    member = await company_members_service.get_member(1, 1)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.remove_quiz(quiz_id, company, member, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc_info.value.detail) == ERROR_QUIZ_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_quiz_access_denied():
    quiz_id = 1
    company = await company_service.get_company_by_id(2, 1)
    member = await company_members_service.get_member(1, 1)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.remove_quiz(quiz_id, company, member, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert str(exc_info.value.detail) == ERROR_ACCESS


@pytest.mark.asyncio
async def test_quizz_submit_success():
    questions = await question_service.get_questions(15)
    user_answer = ["4", "4", "Paris"]
    company = await company_service.get_company_by_id(1, 1)
    member = await company_members_service.get_member(1, 1)
    current_user = 1

    result = await quizz_service.quizz_submit(questions, user_answer, member, company, current_user)

    assert result == {"correct_answers": 2, "total_answers": 3}


@pytest.mark.asyncio
async def test_quizz_submit_not_enough_questions():
    questions = await question_service.get_questions(14)
    user_answer = ["4", "4", "Paris"]
    company = await company_service.get_company_by_id(1, 1)
    member = await company_members_service.get_member(1, 1)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quizz_service.quizz_submit(questions, user_answer, member, company, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert str(exc_info.value.detail) == ERROR_NOT_ENOUGH_QUESTIONS
