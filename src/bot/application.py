from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from dependency_injector.wiring import inject, Provide

from bot.handlers import callback_router
from bot.handlers import message_router
from bot.middlewares import UserMiddleware, ChatMiddleware
from containers.bot import BotContainer


@inject
async def setup(webhook_url,
                bot: Bot = Provide[BotContainer.bot],
                dp: Dispatcher = Provide[BotContainer.dispatcher]):
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
    group_commands = [
        BotCommand(command="queue", description="Добавить очередь в беседу (укажите название)"),
        BotCommand(command="queues", description="Список очередей беседы")
    ]

    private_commands = [
    ]

    await bot.set_my_commands(commands=group_commands, scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(commands=private_commands, scope=BotCommandScopeAllPrivateChats())
