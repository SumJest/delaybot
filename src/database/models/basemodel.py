from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Query

from database.connection import connection, async_session_maker


class BaseModel(AsyncAttrs, DeclarativeBase, ):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @classmethod
    @connection
    async def get(cls, session: AsyncSession, id: int):
        return await session.get(cls, id)

    @classmethod
    @connection
    async def create(cls, session: AsyncSession, **kwargs):
        obj = cls(**kwargs)
        await obj.save(session=session)
        return obj

    @classmethod
    @connection
    async def get_or_create(cls, session: AsyncSession, defaults: Optional[dict] = None, **kwargs):
        if defaults is None:
            defaults = {}
        obj = await cls.get(session=session, **kwargs)
        created = False
        if obj is None:
            obj = cls(**kwargs, **defaults)
            await obj.save(session=session)
            created = True
        return obj, created

    @classmethod
    @connection
    async def update_or_create(cls, session: AsyncSession, defaults: Optional[dict] = None, **kwargs):
        if defaults is None:
            defaults = {}
        obj = await cls.get(session=session, **kwargs)
        created = False
        if obj is None:
            obj = cls(**kwargs, **defaults)
            created = True
        else:
            for k, v in defaults.items():
                setattr(obj, k, v)
        await obj.save(session=session)
        return obj, created

    @connection
    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)

    @connection
    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    @classmethod
    @connection
    async def filter(cls, session: AsyncSession, **kwargs):
        stmt = select(cls).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    @connection
    async def all(cls, session: AsyncSession):
        stmt = select(cls)
        result = await session.execute(stmt)
        return result.scalars().all()
