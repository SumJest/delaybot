import logging
from logging.handlers import RotatingFileHandler

from vkwave.bots import SimpleLongPollBot, FiniteStateMachine

import settings
from handlers.message import router as message_router
from handlers.callback import router as callback_router
from middlewares import UserMiddleware, ChatMiddleware
from containers import ServicesContainer

bot = SimpleLongPollBot(tokens=[settings.VK_TOKEN], group_id=settings.VK_GROUP_ID)
bot.add_middleware(UserMiddleware())
bot.add_middleware(ChatMiddleware())
bot.dispatcher.add_router(message_router)
bot.dispatcher.add_router(callback_router)


services_container = ServicesContainer(api_context=bot.api_context, fsm=FiniteStateMachine())
services_container.wire(['handlers.message',
                         'handlers.callback'])

bot.run_forever()
