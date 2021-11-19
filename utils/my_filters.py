from vkwave.bots import SimpleBotEvent
from vkwave.bots.core.dispatching.filters import base, builtin


class payloadFilter(base.BaseFilter):
    """
    Проверяет прикреплена ли к сообщению гео-метка
    """

    async def check(self, event: SimpleBotEvent) -> base.FilterResult:
        builtin.is_message_event(event)

        return base.FilterResult(event.object.object.message.payload is not None)
