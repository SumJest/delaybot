from typing import Type

from database.models.basemodel import BaseModel


class DatabaseError(Exception):
    pass


class ObjectNotFoundError(DatabaseError):

    def __init__(self, model: Type[BaseModel], kwargs):
        self.model = model
        self.kwargs = kwargs

    def __str__(self):
        return f"{self.__name__}: {self.model.__name__} not found with kwargs: {', '.join(self.kwargs)}"
