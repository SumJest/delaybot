import logging
import traceback

from .base import BaseModel
from .chat import Chat
from .user import User
from .queue import Queue
from .database import db

try:
    db.create_tables([Chat, User, Queue])
except Exception as ex:
    logging.error(ex)