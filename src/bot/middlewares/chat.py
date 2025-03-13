from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, types
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from containers import ServicesContainer
from services.chat_service import ChatService


class ChatMiddleware(BaseMiddleware):
    @inject
    async def upsert_chat(self, chat: types.Chat,
                          chat_service: ChatService = Provide[ServicesContainer.chat_service]):
        chat_model = await chat_service.to_model(chat)
        print(chat)
        return await chat_service.upsert(chat_model, chat.id, auto_commit=True)


    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.type in ('group', 'supergroup'):
            chat = await self.upsert_chat(event.chat)
            data['chat'] = chat
        return await handler(event, data)
