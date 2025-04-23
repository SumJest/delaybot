from enum import Enum
from sys import prefix

from aiogram.filters.callback_data import CallbackData


class QueueAction(str, Enum):
    JOIN = 'join'
    LEAVE = 'leave'
    CLEAR = 'clear'
    DELETE = 'delete'
    OPEN = 'open'
    CLOSE = 'close'

class QueueActionCallbackFactory(CallbackData, prefix='queue'):
    action: QueueAction
    queue_id: int
