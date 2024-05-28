from enum import Enum


class QueueAction(str, Enum):
    JOIN = 'join'
    LEAVE = 'leave'
    CLEAR = 'clear'
    DELETE = 'delete'
    OPEN = 'open'
    CLOSE = 'close'
