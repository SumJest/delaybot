from aiogram import Bot, Dispatcher
from vkwave.bots import SimpleLongPollBot, FiniteStateMachine

import settings
from containers import ServicesContainer
from handlers.callback import router as callback_router
from handlers.message import router as message_router
from middlewares import UserMiddleware, ChatMiddleware

bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()
dp.message.middleware(UserMiddleware())
dp.message.middleware(ChatMiddleware())
# bot.dispatcher.add_router(message_router)
# bot.dispatcher.add_router(callback_router)


services_container = ServicesContainer(bot=bot, fsm=FiniteStateMachine())
services_container.wire(['handlers.message',
                         'handlers.callback'])

bot.run_forever()
