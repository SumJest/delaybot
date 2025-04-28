import json
import logging
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Optional, Callable

from advanced_alchemy.config import AsyncSessionConfig, EngineConfig
from advanced_alchemy.extensions.fastapi import SQLAlchemyAsyncConfig
from dependency_injector.resources import T
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from dependency_injector import resources

from settings import settings

logger = logging.getLogger(__name__)

database_url = settings.database.url

async_config = SQLAlchemyAsyncConfig(
    connection_string=settings.database.url,
    session_config=AsyncSessionConfig(expire_on_commit=False),
    create_all=True,
    commit_mode="autocommit",
    engine_config=EngineConfig(json_serializer=json.dumps, pool_size=10, max_overflow=0),
)

engine = create_async_engine(url=settings.database.url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

def connection(func):
    async def wrapper(*args, session: Optional[AsyncSession] = None, **kwargs):
        if session is not None:
            return await func(*args, session=session, **kwargs)
        async with async_session_maker() as session:
            print('new_session')
            try:
                return await func(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                print('session closed')
                await session.close()

    return wrapper


class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(url=db_url)
        self._session_factory = async_sessionmaker(self._engine, class_=AsyncSession)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[AsyncSession]]:
        session: AsyncSession = await self._session_factory()
        print('Сессия открыта')
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
            print('Сессия закрыта')


class SessionResource(resources.AsyncResource):
    async def init(self, *args, **kwargs) -> Optional[T]:
        print('start session')
        return async_session_maker()

    async def shutdown(self, resource: Optional[T]) -> None:
        print('close session')
        await resource.close()
