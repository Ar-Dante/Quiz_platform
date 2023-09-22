from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.user_schemas import SignUpRequestModel, UserUpdate

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return password_context.hash(password)


async def get_by_email(user_email: str, db: AsyncSession):
    query = select(User).filter_by(user_email=user_email)
    result = await db.execute(query)
    return result.scalar()


async def create(user: SignUpRequestModel, db: AsyncSession):
    password_hash = hash_password(user.hashed_password)
    db_user = User(**user.dict(exclude={"hashed_password"}), hashed_password=password_hash)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get(limit, offset, db: AsyncSession):
    query = select(User).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


async def get_by_id(user_id: int, db: AsyncSession):
    query = select(User).filter_by(user_id=user_id)
    result = await db.execute(query)
    return result.scalar()


async def update(user_id: int, user_update: UserUpdate, db: AsyncSession):
    db_user = await get_by_id(user_id, db)

    if db_user:
        for attr, value in user_update.dict().items():
            setattr(db_user, attr, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete(user_id: int, db: AsyncSession):
    db_user = await get_by_id(user_id, db)

    if db_user:
        await db.delete(db_user)

    await db.commit()
    return db_user
