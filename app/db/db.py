import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.conf.config import conf

engine = create_async_engine(conf.sqlalchemy_database_url, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_redis():
    redis_pool = await aioredis.from_url(conf.redis_url)
    yield redis_pool


async def get_db():
    async with AsyncSession(engine) as db:
        yield db
