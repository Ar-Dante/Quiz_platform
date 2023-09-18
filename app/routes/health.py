import aioredis
from fastapi import APIRouter, Depends, HTTPException
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
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@route.get("/check_redis")
async def check_redis_connection(redis: aioredis.Redis = Depends(get_redis)):
    try:
        result = await redis.ping()
        return {"message": "Redis connection is OK", "ping_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
