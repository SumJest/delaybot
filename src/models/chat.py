from peewee import TextField, BigIntegerField, ForeignKeyField

from .user import User
from .base import BaseModel


class Chat(BaseModel):
    peer_id = BigIntegerField(primary_key=True)
    name = TextField(default="")
    owner = ForeignKeyField(User,
                            null=True,
                            default=None,
                            on_delete="SET NULL",
                            related_name="chats")
