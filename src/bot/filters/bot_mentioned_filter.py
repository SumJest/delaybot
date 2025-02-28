import re

from vkwave.bots import SimpleBotEvent
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching.filters.base import FilterResult
from vkwave.bots.core.dispatching.filters.builtin import is_message_event


class BotMentionedFilter(BaseFilter):
    """
    Проверяет упомянут ли бот в сообщении
    """

    group_id: int

    def __init__(self, group_id: int):
        self.group_id = group_id

    async def check(self, event: SimpleBotEvent) -> FilterResult:
        is_message_event(event)
        matches = re.findall(rf"\[club{self.group_id}\|\S+]", event.object.object.message.text)
        return FilterResult(bool(matches))