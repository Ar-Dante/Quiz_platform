from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete

from app.db.db import async_session


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def find_by_filter(self):
        raise NotImplementedError

    @abstractmethod
    async def update_by_filter(self):
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with async_session() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_all(self, limit: int, offset: int):
        async with async_session() as session:
            stmt = select(self.model)
            stmt = stmt.limit(limit).offset(offset)
            res = await session.execute(stmt)
            return [row._asdict() for row in res.all()]

    async def find_by_filter(self, filter_by):
        async with async_session() as session:
            stmt = select(self.model).filter_by(**filter_by)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def update_by_filter(self, filter_by, data: dict):
        async with async_session() as session:
            stmt = (
                update(self.model)
                .filter_by(**filter_by)
                .values(**data)
            )
            await session.execute(stmt)
            await session.commit()

    async def delete_by_id(self, record_id: int):
        async with async_session() as session:
            stmt = delete(self.model).where(self.model.id == record_id)
            await session.execute(stmt)
            await session.commit()
