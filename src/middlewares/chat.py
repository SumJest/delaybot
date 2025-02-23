from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from models import Chat


class ChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.type not in ('group', 'supergroup'):
            return
        chat, created = Chat.get_or_create(
            peer_id=event.chat.id
        )
        data['chat'] = chat
        return await handler(event, data)
