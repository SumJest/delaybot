from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

# TODO: Use environment variables, PRAGMA only for sqlite

database_url = 'postgresql+asyncpg://delaybot:delaybot@localhost:5432/delaybot'
engine = create_async_engine(url=database_url)
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
