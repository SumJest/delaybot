from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.application import alchemy
from containers import ServicesContainer

DatabaseSession = Annotated[AsyncSession, Depends(alchemy.provide_session())]


async def get_services(
        session: DatabaseSession,
) -> ServicesContainer:
    # FastAPI вызовет alchemy.provide_session ровно один раз за запрос
    # Устанавливаем таймаут захвата блокировок в 5 секунд
    await session.execute(text("SET lock_timeout = '10s'"))
    try:
        yield ServicesContainer(session)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
