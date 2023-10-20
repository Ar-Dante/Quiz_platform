import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.conf.config import conf

SQL_ALCHEMY_URL_PROD = f"postgresql+asyncpg://{conf.db_user_prod}:{conf.db_password_prod}@{conf.db_endpoint_prod}:{conf.db_port_prod}"
engine = create_async_engine(SQL_ALCHEMY_URL_PROD, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_redis():
    return redis.Redis(host=conf.redis_endpoint_prod, db=0)




async def get_db():
    async with async_session() as db:
        yield db
