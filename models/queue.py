import peewee
from peewee import IntegerField, ForeignKeyField, BooleanField, CharField

from .base import BaseModel
from .chat import Chat
from .fields.queue import QueueField
from .user import User


class Queue(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255)
    chat = ForeignKeyField(Chat,
                           on_delete="cascade",
                           related_name="queues")
    msg_id = IntegerField()
    owner = ForeignKeyField(User,
                            on_delete="cascade",
                            related_name="queues")
    closed = BooleanField(default=False)
    members = QueueField(default=[])
