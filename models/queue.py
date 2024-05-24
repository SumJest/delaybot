import peewee
from peewee import IntegerField, ForeignKeyField

from .base import BaseModel
from .chat import Chat
from .fields.queue import QueueField
from .user import User


class Queue(BaseModel):
    id = IntegerField(primary_key=True)
    chat = ForeignKeyField(Chat,
                           on_delete="cascade",
                           related_name="queues")
    msg_id = IntegerField()
    owner = ForeignKeyField(User,
                            on_delete="cascade",
                            related_name="queues")
    closed = peewee.BooleanField(default=False)
    queue = QueueField(default=[])
