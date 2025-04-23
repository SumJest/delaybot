from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, types
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from containers import ServicesContainer
from services.chat_service import ChatService


class ChatMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        services_container: ServicesContainer = data.get("services_container")
        chat_service = services_container.chat_service
        if event.chat.type in ('group', 'supergroup'):
            chat_model = await chat_service.to_model(event.chat)
            chat = await chat_service.upsert(chat_model, item_id=event.chat.id, auto_commit=True, auto_refresh=True)
            data['chat'] = chat
        return await handler(event, data)
