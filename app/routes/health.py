import logging


from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db, get_redis

route = APIRouter(tags=["healthcheck"])


@route.get("/")
async def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@route.get("/check_db_connection")
async def check_db_connection(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if result is None:
            logging.error("PostgreSQL is not configured correctly")
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"status_code": 200, "detail": "ok", "result": "working"}
    except Exception as e:
        logging.error("Some problems with connection to PostgreSQL")
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@route.get("/check_redis")
async def check_redis_connection(redis: Redis = Depends(get_redis)):
    try:
        await redis.ping()
        logging.info("Connection to Redis was successful")
        return {"status_code": 200, "detail": "ok", "result": "working"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
