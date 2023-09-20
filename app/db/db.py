import aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.conf.config import sqlalchemy_database_url, redis_url

SQLALCHEMY_DATABASE_URL = sqlalchemy_database_url

engine = create_async_engine(sqlalchemy_database_url, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_redis_pool():
    redis_pool = await aioredis.from_url(redis_url)
    return redis_pool


async def get_redis(redis_pool=Depends(create_redis_pool)):
    return redis_pool


async def get_db():
    async with AsyncSession(engine) as db:
        yield db
