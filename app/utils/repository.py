from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, List, Optional

from aioredis import Redis
from sqlalchemy import insert, select, update, delete

from app.db.db import async_session


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> int:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_filter(self, filter_by: dict):
        raise NotImplementedError

    @abstractmethod
    async def filter_by(self, limit: int, offset: int, filter_by: dict) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def filter(self, filter_by: dict) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def update_by_filter(self, filter_by: dict, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, record_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_filter(self, filter_by: dict) -> None:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with async_session() as session:
            statement = insert(self.model).values(**data).returning(self.model.id)
            res = await session.execute(statement)
            await session.commit()
            return res.scalar_one()

    async def find_all(self, limit: int, offset: int) -> list:
        async with async_session() as session:
            statement = select(self.model)
            statement = statement.limit(limit).offset(offset)
            res = await session.execute(statement)
            return res.scalars().all()

    async def filter_by(self, limit: int, offset: int, filter_by: dict) -> list:
        async with async_session() as session:
            statement = select(self.model).filter_by(**filter_by).limit(limit).offset(offset)
            res = await session.execute(statement)
            return res.scalars().all()

    async def filter(self, filter_by: dict) -> list:
        async with async_session() as session:
            statement = select(self.model).filter_by(**filter_by)
            res = await session.execute(statement)
            return res.scalars().all()

    async def find_by_filter(self, filter_by: dict):
        async with async_session() as session:
            statement = select(self.model).filter_by(**filter_by)
            res = await session.execute(statement)
            return res.scalar_one_or_none()

    async def update_by_filter(self, filter_by: dict, data: dict) -> None:
        async with async_session() as session:
            statement = update(self.model).filter_by(**filter_by).values(**data)
            await session.execute(statement)
            await session.commit()

    async def delete_by_id(self, record_id: int) -> None:
        async with async_session() as session:
            statement = delete(self.model).where(self.model.id == record_id)
            await session.execute(statement)
            await session.commit()

    async def delete_by_filter(self, filter_by: dict) -> None:
        async with async_session() as session:
            statement = delete(self.model).filter_by(**filter_by)
            await session.execute(statement)
            await session.commit()


class RedisDataRepository:
    async def store_data(self, redis: Redis, key: str, data: str, expiration_hours: int = 48):
        await redis.set(key, data)
        await redis.expire(key, timedelta(hours=expiration_hours))

    async def get_data(self, redis: Redis, key: str):
        return await redis.get(key)

    async def delete_data(self, redis: Redis, key: str):
        return await redis.delete(key)
