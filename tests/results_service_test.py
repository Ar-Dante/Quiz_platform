from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.conf.messages import ERROR_USER_NOT_FOUND, ERROR_MEMBER_NOT_FOUND, ERROR_ACCESS
from app.db.models import Result, Company, Quiz, CompanyMembers
from app.repository.results import ResultsRepository
from app.services.results import ResultsService

result_service = ResultsService(ResultsRepository)


@pytest.mark.asyncio
async def test_add_results():
    quiz_id = 1
    company_id = 1
    current_user = 1
    correct_count = 5
    total_count = 7
    result_service.results_repo.add_one = AsyncMock()

    await result_service.add_results(quiz_id, company_id, current_user, correct_count, total_count)


@pytest.mark.asyncio
async def test_calculate_average_rating():
    result1 = Result(result_right_count=1, result_total_count=2)
    result2 = Result(result_right_count=1, result_total_count=2)
    user_results = [result1, result2]
    average_rating = await result_service.calculate_average_rating(user_results)

    assert average_rating == 0.5


@pytest.mark.asyncio
async def test_get_user_average_rating_in_company_success():
    user_id = 1
    company_id = 1
    member = {"member_data": "value"}
    company = {"company_data": "value"}
    current_user = 1

    result_service.calculate_average_rating = AsyncMock(return_value=0.675)

    average_rating = await result_service.get_user_average_rating_in_company(user_id, company_id, member, company,
                                                                             current_user)

    assert average_rating == 0.675


@pytest.mark.asyncio
async def test_get_user_average_rating_in_company_user_not_found():
    user_id = 1
    company_id = 2
    member = {"member_data": "value"}
    company = {"company_data": "value"}
    current_user = 1
    with pytest.raises(HTTPException) as exc_info:
        await result_service.get_user_average_rating_in_company(user_id, company_id, member, company, current_user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == ERROR_USER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_average_rating_in_company_user_not_member():
    user_id = 1
    company_id = 2
    member = None
    company = Company(id=1, owner_id=2)
    current_user = 1

    with pytest.raises(HTTPException) as exc_info:
        await result_service.get_user_average_rating_in_company(user_id, company_id, member, company, current_user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == ERROR_MEMBER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_system_average_rating_success():
    user_id = 1

    result1 = Result(result_right_count=4, result_total_count=5)
    result2 = Result(result_right_count=7, result_total_count=10)
    user_results = [result1, result2]
    result_service.calculate_average_rating = AsyncMock(return_value=0.675)
    result_service.results_repo.filter = AsyncMock(return_value=user_results)

    average_rating = await result_service.get_system_average_rating(user_id)

    assert average_rating == 0.675


@pytest.mark.asyncio
async def test_get_system_average_rating_user_not_found():
    user_id = 1

    result_service.results_repo.filter = AsyncMock(return_value=[])

    with pytest.raises(HTTPException) as exc_info:
        await result_service.get_system_average_rating(user_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == ERROR_USER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_last_attempt_times_for_all_quizzes_success():
    quizzes = [
        Quiz(id=1, quiz_name="Quiz 1"),
        Quiz(id=2, quiz_name="Quiz 2"),
        Quiz(id=3, quiz_name="Quiz 3"),
    ]

    result_service.results_repo.get_max_by_filter = AsyncMock(
        side_effect=[datetime(2023, 10, 15, 10, 0, 0), datetime(2023, 10, 16, 15, 0, 0), None]
    )

    last_attempt_times = await result_service.get_last_attempt_times_for_all_quizzes(quizzes)

    expected_times = [
        {"quiz_id": 1, "quiz_name": "Quiz 1", "last_attempt_date": datetime(2023, 10, 15, 10, 0, 0)},
        {"quiz_id": 2, "quiz_name": "Quiz 2", "last_attempt_date": datetime(2023, 10, 16, 15, 0, 0)},
        {"quiz_id": 3, "quiz_name": "Quiz 3", "last_attempt_date": None},
    ]

    assert last_attempt_times == expected_times


@pytest.mark.asyncio
async def test_get_average_quiz_by_time_success():
    quizzes = [
        Quiz(id=1, quiz_name="Quiz 1"),
        Quiz(id=2, quiz_name="Quiz 2"),
    ]

    result1 = Result(result_quiz_id=1, created_at=datetime(2023, 10, 15, 10, 0, 0))
    result2 = Result(result_quiz_id=2, created_at=datetime(2023, 10, 16, 15, 0, 0))

    user_results1 = [result1]
    user_results2 = [result2]
    result_service.results_repo.get_max_by_filter = AsyncMock(
        side_effect=[datetime(2023, 10, 15, 10, 0, 0), datetime(2023, 10, 16, 15, 0, 0)]
    )
    result_service.results_repo.filter = AsyncMock(
        side_effect=[user_results1, user_results2]
    )
    result_service.calculate_average_rating = AsyncMock(
        side_effect=[1.0, 0.5]
    )
    average_quizzes = await result_service.get_average_quiz_by_time(quizzes)

    expected_average_quizzes = [
        {"quiz_id": 1, "average_quizz": 1.0, "last_attempt_date": datetime(2023, 10, 15, 10, 0, 0)},
        {"quiz_id": 2, "average_quizz": 0.5, "last_attempt_date": datetime(2023, 10, 16, 15, 0, 0)}
    ]

    assert average_quizzes == expected_average_quizzes


@pytest.mark.asyncio
async def test_get_last_attempt_times_for_all_users_success():
    users = [
        CompanyMembers(user_id=1),
        CompanyMembers(user_id=2),
        CompanyMembers(user_id=3),
    ]

    result_service.results_repo.get_max_by_filter = AsyncMock(side_effect=[
        datetime(2023, 10, 15, 10, 0, 0),
        datetime(2023, 10, 16, 15, 0, 0),
        None
    ])
    result_service.valid_result_access = AsyncMock()

    user_last_attempt_times = await result_service.get_last_attempt_times_for_all_users(users, 1, {}, {})

    expected_last_attempt_times = [
        {"user_id": 1, "last_attempt_date": datetime(2023, 10, 15, 10, 0, 0)},
        {"user_id": 2, "last_attempt_date": datetime(2023, 10, 16, 15, 0, 0)},
        {"user_id": 3, "last_attempt_date": None},
    ]

    assert user_last_attempt_times == expected_last_attempt_times


@pytest.mark.asyncio
async def test_get_last_attempt_times_for_all_users_error_access():
    users = [
        CompanyMembers(user_id=1),
        CompanyMembers(user_id=2),
        CompanyMembers(user_id=3),
    ]
    company = Company(owner_id=2)
    member = CompanyMembers(user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await result_service.get_last_attempt_times_for_all_users(users, 1, member, company)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_average_users_by_time_success():
    users = [
        CompanyMembers(user_id=1),
        CompanyMembers(user_id=2)
    ]
    result_service.results_repo.get_max_by_filter = AsyncMock(side_effect=[
        datetime(2023, 10, 15, 10, 0, 0),
        datetime(2023, 10, 16, 15, 0, 0)
    ])
    result_service.calculate_average_rating = AsyncMock(side_effect=[0.8, 0.7])
    result_service.valid_result_access = AsyncMock()

    average_users = await result_service.get_average_users_by_time(users, 1, {}, {})

    expected_average_users = [
        {"user_id": 1, "average_user": 0.8, "last_attempt_date": datetime(2023, 10, 15, 10, 0, 0)},
        {"user_id": 2, "average_user": 0.7, "last_attempt_date": datetime(2023, 10, 16, 15, 0, 0)}
    ]

    assert average_users == expected_average_users


@pytest.mark.asyncio
async def test_get_average_quizz_for_user_in_company_by_time_success():
    quizzes = [
        Quiz(id=1),
        Quiz(id=2)
    ]
    users_id = 1
    current_user = 1
    member = {}
    company = Company(id=1)
    result_service.results_repo.get_max_by_filter = AsyncMock(side_effect=[
        datetime(2023, 10, 15, 10, 0, 0),
        datetime(2023, 10, 16, 15, 0, 0)
    ])
    result_service.results_repo.filter = AsyncMock(side_effect=[
        [
            Result(result_user_id=1, result_quiz_id=1, result_company_id=1, result_right_count=4, result_total_count=5),
            Result(result_user_id=1, result_quiz_id=2, result_company_id=1, result_right_count=3, result_total_count=5)
        ],
        [
            Result(result_user_id=1, result_quiz_id=1, result_company_id=1, result_right_count=3, result_total_count=5),
            Result(result_user_id=1, result_quiz_id=2, result_company_id=1, result_right_count=2, result_total_count=5)
        ]
    ])
    result_service.calculate_average_rating = AsyncMock(side_effect=[0.8, 0.6, 0.6, 0.4])
    result_service.valid_result_access = AsyncMock()
    average_quizzes = await result_service.get_average_quizz_for_user_in_company_by_time(
        users_id, quizzes, current_user, member, company)

    expected_average_quizzes = [
        {"user_id": 1, "company_id": 1, "result_quiz_id": 1, "average_user": 0.8, "last_attempt_date": datetime(2023, 10, 15, 10, 0, 0)},
        {"user_id": 1, "company_id": 1, "result_quiz_id": 2, "average_user": 0.6, "last_attempt_date": datetime(2023, 10, 16, 15, 0, 0)}
    ]
    assert average_quizzes == expected_average_quizzes