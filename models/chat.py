from peewee import TextField, BigIntegerField

from .base import BaseModel


class Chat(BaseModel):
    peer_id = BigIntegerField(primary_key=True)
    name = TextField()