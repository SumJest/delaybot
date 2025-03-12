import asyncio

from aiogram import Bot, Dispatcher

import settings
from containers import ServicesContainer
from bot.handlers import callback_router
from bot.handlers import message_router
from bot.middlewares import UserMiddleware, ChatMiddleware

bot = Bot(token=settings.TELEGRAM_TOKEN)

dp = Dispatcher()


async def setup(webhook_url):
    dp.message.middleware(UserMiddleware())
    dp.message.middleware(ChatMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.include_routers(message_router, callback_router)
    await bot.delete_webhook()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )


services_container = ServicesContainer(bot=bot, fsm=object())
services_container.wire(['bot.handlers.message',
                         'bot.handlers.callback',
                         'bot.events',
                         'bot.middlewares.chat',
                         'bot.middlewares.user',])
