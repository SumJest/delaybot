import json

from sqlalchemy import TypeDecorator, JSON


class ListField(TypeDecorator):
    """
    Custom field for SQLAlchemy that stores a Python list as JSON in the database.
    """
    impl = JSON  # Use the JSON type for storing data in the database

    def process_bind_param(self, value, dialect):
        """Converts a Python list to JSON before saving it to the database."""
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """Converts JSON back to a Python list when retrieving it from the database."""
        if value is not None:
            return json.loads(value)
        return value
    