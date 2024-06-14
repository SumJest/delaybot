from typing import List

from vkwave.bots import SimpleBotEvent
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching.filters.base import FilterResult


class CallbackKeysFilter(BaseFilter):
    """
    Проверяет прикреплена ли к сообщению гео-метка
    """
    keys: List[str]

    def __init__(self, keys: List[str]):
        self.keys = keys

    async def check(self, event: SimpleBotEvent) -> FilterResult:
        if event.object.type == "message_event" and event.object.object.payload is not None:
            such = True
            for key in self.keys:
                if key not in event.object.object.payload.keys():
                    such = False
            return FilterResult(such)
        else:
            return FilterResult(False)
