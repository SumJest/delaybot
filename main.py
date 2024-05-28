import logging

from vkwave.bots import SimpleLongPollBot

import settings
from handlers.message import router as message_router
from handlers.callback import router as callback_router
from middlewares import UserMiddleware, ChatMiddleware
from containers import ServicesContainer

logging.basicConfig(level="DEBUG")

bot = SimpleLongPollBot(tokens=[settings.VK_TOKEN], group_id=settings.VK_GROUP_ID)
bot.add_middleware(UserMiddleware())
bot.add_middleware(ChatMiddleware())
bot.dispatcher.add_router(message_router)
bot.dispatcher.add_router(callback_router)
#
# @bot.message_handler()
# async def simple_handler(event: SimpleBotEvent):
#     user: User = event['user']
#     print(user.user_id, user.is_blocked, user.is_admin)
#     print(event.object.object.message.text)
#
#
# @bot.handler()
# async def simple_callback_handler(event: SimpleBotEvent):
#     user: User = event['user']
#     print(user.user_id, user.is_blocked, user.is_admin)

services_container = ServicesContainer(api_context=bot.api_context)
services_container.wire(['handlers.message',
                         'handlers.callback'])

bot.run_forever()
