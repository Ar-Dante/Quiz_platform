import json

import pytest

from app.db.db import get_redis
from app.repository.companies import CompanyRepository
from app.repository.company_members import CompanyMembersRepository
from app.services.companies import CompanyService
from app.services.company_members import CompanyMembersService
from app.services.redis import redis_service

company_members_service = CompanyMembersService(CompanyMembersRepository)
company_service = CompanyService(CompanyRepository)

@pytest.mark.asyncio
async def test_store_results():
    quiz_id = 2
    company_id = 2
    current_user = 1
    correct_count = 4
    total_count = 5
    await redis_service.store_results(quiz_id, company_id, current_user, correct_count, total_count)
    redis = await get_redis()
    key = f"quiz_answers:{quiz_id}:{current_user}:{company_id}"
    stored_data = await redis.get(key)
    stored_data = json.loads(stored_data)
    expected_data = {
        "quiz_id": quiz_id,
        "company_id": company_id,
        "user_id": current_user,
        "correct_count": correct_count,
        "total_count": total_count
    }

    assert stored_data == expected_data
    await redis.close()


@pytest.mark.asyncio
async def test_get_user_results():
    user_id = 1
    current_user = 1
    upload_format = "json"
    redis = await get_redis()
    data1 = json.dumps({
        "quiz_id": 1,
        "company_id": 1,
        "user_id": user_id,
        "correct_count": 5,
        "total_count": 10
    })
    data2 = json.dumps({
        "quiz_id": 2,
        "company_id": 2,
        "user_id": user_id,
        "correct_count": 4,
        "total_count": 5
    })
    results = await redis_service.get_user_results(user_id, current_user, upload_format)

    expected_results = [
        json.loads(data2),
        json.loads(data1)
    ]

    assert results == expected_results
    await redis.close()


@pytest.mark.asyncio
async def test_get_user_results_for_company():
    user_id = 1
    current_user = 1
    member = await company_members_service.get_member(1, 1)
    company = await company_service.get_company_by_id(1, 1)
    upload_format = "json"
    redis = await get_redis()
    data1 = json.dumps({
        "quiz_id": 1,
        "company_id": company.id,
        "user_id": user_id,
        "correct_count": 5,
        "total_count": 10
    })
    results = await redis_service.get_user_results_for_company(user_id, current_user, member, company, upload_format)

    expected_results = [
        json.loads(data1),
    ]

    assert results == expected_results
    await redis.close()