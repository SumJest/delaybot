from .base import BaseModel
from .chat import Chat
from .user import User
from .queue import Queue
from .database import db

try:
    db.create_tables([Chat, User, Queue])
except:
    pass