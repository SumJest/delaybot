import asyncio

from aiogram import Bot, Dispatcher

import settings
from containers import ServicesContainer
from bot.handlers import callback_router
from bot.handlers import message_router
from bot.middlewares import UserMiddleware, ChatMiddleware

async def setup():
    bot = Bot(token=settings.TELEGRAM_TOKEN)

    dp = Dispatcher()
    dp.message.middleware(UserMiddleware())
    dp.message.middleware(ChatMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.include_routers(message_router, callback_router)


services_container = ServicesContainer(bot=bot, fsm=object())
services_container.wire(['handlers.message',
                         'handlers.callback'])

