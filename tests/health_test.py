from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.db import db
from app.routes.health import check_db_connection, check_redis_connection
from app.services import redis


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_check_db_connection_successful():
    db.execute = AsyncMock(return_value="1")

    response = await check_db_connection(db)

    assert response == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@pytest.mark.asyncio
async def test_check_db_connection_db_error():
    db.execute = AsyncMock(side_effect=Exception("Database error"))

    with pytest.raises(HTTPException) as exc_info:
        await check_db_connection(db)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error connecting to the database"


@pytest.mark.asyncio
async def test_check_redis_connection_successful():
    redis.ping = AsyncMock(return_value=None)

    response = await check_redis_connection(redis)

    assert response == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@pytest.mark.asyncio
async def test_check_redis_connection_redis_error():
    redis.ping = AsyncMock(side_effect=Exception("Redis error"))

    with pytest.raises(HTTPException) as exc_info:
        await check_redis_connection(redis)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error connecting to the database"