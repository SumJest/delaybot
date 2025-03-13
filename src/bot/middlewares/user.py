from typing import Callable, Dict, Any, Awaitable

from aiogram import types
from dependency_injector.wiring import inject, Provide

from containers import ServicesContainer
from database.models import User

from aiogram import BaseMiddleware

from services.user_service import UserService


class UserMiddleware(BaseMiddleware):
    @inject
    async def upsert_user(self, user: types.User, user_service: UserService = Provide[ServicesContainer.user_service]) \
            -> User:
        user_model = await user_service.to_model(user)
        return await user_service.upsert(user_model, item_id=user.id, auto_commit=True)

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        user = await self.upsert_user(event.from_user)
        if user.is_blocked:
            return
        data['user'] = user
        return await handler(event, data)
