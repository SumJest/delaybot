from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.application import alchemy
from containers import ServicesContainer

DatabaseSession = Annotated[AsyncSession, Depends(alchemy.provide_session())]


async def get_services(
        session: DatabaseSession,
) -> ServicesContainer:
    # FastAPI вызовет alchemy.provide_session ровно один раз за запрос
    yield ServicesContainer(session)
