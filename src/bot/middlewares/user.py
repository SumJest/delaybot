from typing import Callable, Dict, Any, Awaitable

from aiogram import types
from dependency_injector.wiring import inject, Provide

from containers import ServicesContainer
from database.models import User

from aiogram import BaseMiddleware

from services.user_service import UserService


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        services_container: ServicesContainer = data.get("services_container")
        user_service = services_container.user_service
        user_model = await user_service.to_model(event.from_user)
        user = await user_service.upsert(user_model, item_id=event.from_user.id, auto_commit=True, auto_refresh=True)
        if user.is_blocked:
            return
        data['user'] = user
        return await handler(event, data)
