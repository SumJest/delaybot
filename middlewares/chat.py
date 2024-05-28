from vkwave.bots import BaseMiddleware, BotEvent, MiddlewareResult
from vkwave.types.bot_events import BotEventType

from models import User, Chat


class ChatMiddleware(BaseMiddleware):
    async def pre_process_event(self, event: BotEvent) -> MiddlewareResult:

        match event.object.type:
            case BotEventType.MESSAGE_NEW:
                from_id = event.object.object.message.from_id
                peer_id = event.object.object.message.peer_id
            case BotEventType.MESSAGE_EVENT:
                from_id = event.object.object.from_id
                peer_id = event.object.object.peer_id
            case _:
                return MiddlewareResult(True)
        if from_id != peer_id:
            chat, created = Chat.get_or_create(
                peer_id=peer_id
            )
            event['chat'] = chat
        else:
            event['chat'] = None
        return MiddlewareResult(True)
