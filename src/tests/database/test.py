from functools import wraps

from playhouse.sqlite_ext import SqliteExtDatabase


def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        async def test_db_closure(*args, **kwargs):
            test_db = SqliteExtDatabase(":memory:")
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    await func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator
