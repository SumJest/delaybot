from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.models import Chat


class ChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.type in ('group', 'supergroup'):
            chat, created = await Chat.get_or_create(
                id=event.chat.id
            )
            data['chat'] = chat
        return await handler(event, data)
