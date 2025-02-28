from sqlalchemy import event, Engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

# TODO: Use environment variables, PRAGMA only for sqlite

database_url = 'sqlite+aiosqlite:///db.sqlite3'
engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
