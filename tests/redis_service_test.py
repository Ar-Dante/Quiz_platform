import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.conf.messages import ERROR_MEMBER_NOT_EXISTS, ERROR_ACCESS
from app.db.models import Company, CompanyMembers
from app.repository.companies import CompanyRepository
from app.services.companies import CompanyService
from app.services.redis import redis_service, RedisService

company_service = CompanyService(CompanyRepository)


@pytest.mark.asyncio
async def test_save_data_json():
    data = {"example": "data"}
    key = "example_key"
    save_format = "json"
    json_loader_instance = AsyncMock()
    json_loader_instance.save = AsyncMock()
    redis_service.JSONDataLoader = json_loader_instance
    await redis_service._save_data(data, key, save_format)


@pytest.mark.asyncio
async def test_store_results():
    with patch.object(redis_service, 'redis', AsyncMock()), \
            patch.object(redis_service, 'store_data', return_value=None):
        quiz_id = 123
        company_id = 456
        current_user = 789
        correct_count = 3
        total_count = 5
        redis_service.store_results(quiz_id, company_id, current_user, correct_count, total_count)


@pytest.mark.asyncio
async def test_get_user_results():
    user_id = 123
    current_user = 123
    upload_format = "json"
    redis_instance = AsyncMock()
    redis_instance.keys = AsyncMock()
    redis_instance.close = AsyncMock()
    redis_service.redis = redis_instance
    get_data_mock = AsyncMock()
    redis_service.get_data = get_data_mock
    save_data_mock = AsyncMock()
    redis_service._save_data = save_data_mock
    expected_keys = [f"quiz_answers:1:{user_id}:1", f"quiz_answers:2:{user_id}:1"]
    redis_instance.keys.return_value = expected_keys
    data1 = {
        "quiz_id": 1,
        "company_id": 1,
        "user_id": user_id,
        "correct_count": 5,
        "total_count": 10,
    }
    data2 = {
        "quiz_id": 2,
        "company_id": 1,
        "user_id": user_id,
        "correct_count": 7,
        "total_count": 10,
    }
    get_data_mock.side_effect = [json.dumps(data1), json.dumps(data2)]
    redis_service.get_user_results(user_id, current_user, upload_format)


@pytest.mark.asyncio
async def test_valid_access_member_not_exists():
    current_user = 56
    member = None
    company = Company(owner_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await redis_service._valid_access(current_user, member, company)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_MEMBER_NOT_EXISTS


@pytest.mark.asyncio
async def test_valid_access_member_not_admin():
    current_user = 1
    member = CompanyMembers(is_admin=False)
    company = Company(owner_id=4)

    with pytest.raises(HTTPException) as exc_info:
        await redis_service._valid_access(current_user, member, company)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_user_results_access_error():
    user_id = 123
    current_user = 456
    upload_format = "json"

    with pytest.raises(HTTPException) as exc_info:
        await redis_service.get_user_results(user_id, current_user, upload_format)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_user_results_for_company_access_error():
    user_id = 123
    current_user = 456
    member = CompanyMembers(is_admin=False)
    company = Company(id=499)
    upload_format = "json"

    with pytest.raises(HTTPException) as exc_info:
        await redis_service.get_user_results_for_company(user_id, current_user, member, company, upload_format)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_user_results_for_company_access_granted():
    user_id = 123
    current_user = 123
    member = {"is_admin": False}
    company = {"id": 123}
    upload_format = "json"
    with patch.object(RedisService, '_valid_access', return_value=None):
        results = redis_service.get_user_results_for_company(user_id, current_user, member, company, upload_format)

    assert results is not None


@pytest.mark.asyncio
async def test_get_all_results_for_company_access_error():
    company_id = 123
    current_user = 456
    member = CompanyMembers(is_admin=False)
    company = Company(id=499)
    upload_format = "json"

    with pytest.raises(HTTPException) as exc_info:
        await redis_service.get_all_results_for_company(company_id, current_user, member, company, upload_format)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_all_results_for_company_access_granted():
    company_id = 123
    current_user = 123
    member = {"is_admin": False}
    company = {"id": 123}
    upload_format = "json"
    with patch.object(RedisService, '_valid_access', return_value=None):
        with patch.object(RedisService, 'get_data', return_value='{"result": "some data"}'):
            results = redis_service.get_all_results_for_company(company_id, current_user, member, company,
                                                                upload_format)

    assert results is not None


@pytest.mark.asyncio
async def test_get_quiz_results_for_company_access_error():
    quiz_id = 123
    current_user = 456
    member = CompanyMembers(is_admin=False)
    company = Company(id=499)
    upload_format = "json"

    with pytest.raises(HTTPException) as exc_info:
        await redis_service.get_quiz_results_for_company(quiz_id, current_user, member, company, upload_format)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ERROR_ACCESS


@pytest.mark.asyncio
async def test_get_quiz_results_for_company_access_error():
    quiz_id = 123
    current_user = 456
    member = {"is_admin": False}
    company = {"id": 789}
    upload_format = "json"
    with patch.object(RedisService, '_valid_access', return_value=None):
        with patch.object(RedisService, 'get_data', return_value='{"result": "some data"}'):
            results = redis_service.get_quiz_results_for_company(quiz_id, current_user, member, company,
                                                                 upload_format)


    assert results is not None

