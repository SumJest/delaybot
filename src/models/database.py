from peewee import SqliteDatabase

db = SqliteDatabase("database.db",
                    pragmas={'foreign_keys': 1})
