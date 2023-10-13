import pytest
from fastapi import HTTPException
from starlette import status

from app.conf.messages import ERROR_NOT_ENOUGH_OPTIONS, ERROR_QUESTION_NOT_FOUND
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
    data = QuestionCreateModel(
        question_text="What is 2 + 2?",
        question_answers=["3", "4"],
        question_correct_answer="4"
    )
    quiz = await quizz_service.get_quiz_by_id(15)
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    current_user = 1

    result = await question_service.create_question(quiz, data, member, company, current_user)

    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_create_question_not_enough_options():
    data = QuestionCreateModel(
        question_text="What is 2 + 2?",
        question_answers=["3"],
        question_correct_answer="4"
    )
    quiz = await quizz_service.get_quiz_by_id(1)
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await question_service.create_question(quiz, data, member, company, current_user)

    assert exc_info.value.status_code == 400
    assert str(exc_info.value.detail) == ERROR_NOT_ENOUGH_OPTIONS


@pytest.mark.asyncio
async def test_update_question():
    data = QuestionUpdateModel(
        question_text="What is 3 + 3?",
        question_answers=["6", "9", "7"],
        question_correct_answer="6"
    )
    question_id = 1
    quiz_id = 1
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    current_user = 1

    result = await question_service.update_question(question_id, quiz_id, company, data, member, current_user)

    assert result is None


@pytest.mark.asyncio
async def test_update_question_not_enough_options():
    data = QuestionUpdateModel(
        question_text="What is 3 + 3?",
        question_answers=["6"],
        question_correct_answer="6"
    )
    question_id = 1
    quiz_id = 1
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    current_user = 1
    with pytest.raises(HTTPException) as exc_info:
        await question_service.update_question(question_id, quiz_id, company, data, member, current_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert str(exc_info.value.detail) == ERROR_NOT_ENOUGH_OPTIONS


@pytest.mark.asyncio
async def test_remove_question_success():
    question_id = 1
    quiz_id = 1
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    current_user = 1

    result = await question_service.remove_question(question_id, quiz_id, company, member, current_user)

    assert result is None


@pytest.mark.asyncio
async def test_remove_question_not_found():
    question_id = 999
    quiz_id = 1
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await question_service.remove_question(question_id, quiz_id, company, member, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc_info.value.detail) == ERROR_QUESTION_NOT_FOUND


@pytest.mark.asyncio
async def test_get_question_by_id():
    quiz_id = 1
    question_id = 2

    result = await question_service.get_question_by_id(quiz_id, question_id)

    assert result is not None


@pytest.mark.asyncio
async def test_get_question_by_id_not_found():
    quiz_id = 1
    question_id = 999

    with pytest.raises(HTTPException) as exc_info:
        await question_service.get_question_by_id(quiz_id, question_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc_info.value.detail) == ERROR_QUESTION_NOT_FOUND


@pytest.mark.asyncio
async def test_get_questions_success():
    quiz_id = 1
    limit = 10
    offset = 0
    result = await question_service.get_questions(quiz_id, limit, offset)
    assert result is not None


@pytest.mark.asyncio
async def test_get_questions_no_questions_found():
    quiz_id = 999
    limit = 10
    offset = 0

    result = await question_service.get_questions(quiz_id, limit, offset)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_quizz_submit_not_enough_questions():
    questions = [{"question_correct_answer": "4"}]
    user_answer = ["4"]
    member = {"id": 1}  # Replace with the actual member data
    company = {"id": 1, "owner_id": 1}  # Replace with the actual company data and owner ID
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await quiz_service.quizz_submit(questions, user_answer, member, company, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
