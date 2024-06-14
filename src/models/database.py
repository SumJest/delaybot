from peewee import SqliteDatabase

db = SqliteDatabase("databases/database.db",
                    pragmas={'foreign_keys': 1})
