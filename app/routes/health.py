import logging

import aioredis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.messages import ERROR_CONNECTING_TO_DB, ERROR_DB_NOT_CONFIGURED
from app.db.db import get_db, get_redis

route = APIRouter(tags=["healthcheck"])


@route.get("/")
async def health_check():
    logging.info("FastAPI works")
    return {"status_code": 200, "detail": "ok", "result": "working"}


@route.get("/check_db_connection")
async def check_db_connection(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if result is None:
            logging.error("PostgreSQL is not configured correctly")
            raise HTTPException(status_code=500, detail=ERROR_DB_NOT_CONFIGURED)
        return {"status_code": 200, "detail": "ok", "result": "working"}
    except Exception as e:
        logging.error("Some problems with connection to PostgreSQL")
        raise HTTPException(status_code=500, detail=ERROR_CONNECTING_TO_DB)


@route.get("/check_redis")
async def check_redis_connection(redis: aioredis.Redis = Depends(get_redis)):
    try:
        await redis.ping()
        return {"status_code": 200, "detail": "ok", "result": "working"}

    except Exception as e:
        logging.error("Some problems with connection to Redis")
        raise HTTPException(status_code=500, detail=ERROR_CONNECTING_TO_DB)
