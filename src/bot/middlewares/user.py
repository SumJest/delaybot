from typing import Callable, Dict, Any, Awaitable

from aiogram.types import Message

from database.models import User

from aiogram import BaseMiddleware


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user, created = User.update_or_create(user_id=event.from_user.id,
                                              defaults={
                                                  'username': event.from_user.username,
                                                  'first_name': event.from_user.first_name,
                                                  'last_name': event.from_user.last_name,
                                              })
        if user.is_blocked:
            return
        data['user'] = user
        return await handler(event, data)
