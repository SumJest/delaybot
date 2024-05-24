from peewee import IntegerField, BooleanField

from .base import BaseModel


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    is_blocked = BooleanField(default=False)