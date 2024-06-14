from vkwave.bots import BaseMiddleware, BotEvent, MiddlewareResult
from vkwave.types.bot_events import BotEventType

from models import User


class UserMiddleware(BaseMiddleware):
    async def pre_process_event(self, event: BotEvent) -> MiddlewareResult:

        match event.object.type:
            case BotEventType.MESSAGE_NEW:
                user_id = event.object.object.message.from_id
            case BotEventType.MESSAGE_EVENT:
                user_id = event.object.object.user_id
            case _:
                return MiddlewareResult(True)
        user, created = User.get_or_create(user_id=user_id)
        event['user'] = user
        return MiddlewareResult(not user.is_blocked)
