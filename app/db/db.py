import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.conf.config import conf

engine = create_async_engine(conf.sqlalchemy_database_url, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_redis():
    return await aioredis.Redis(host=conf.redis_host, port=conf.redis_port, db=0)


async def get_db():
    async with async_session() as db:
        yield db
