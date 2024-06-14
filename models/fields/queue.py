from playhouse.sqlite_ext import JSONField


class QueueField(JSONField):
    def db_value(self, value):
        if not isinstance(value, list):
            raise ValueError("Queue field must be list")
        return super().db_value(value)

    def python_value(self, value):
        from_db = super().python_value(value)
        if not isinstance(from_db, list):
            raise ValueError("Queue field must be list")
        return from_db
