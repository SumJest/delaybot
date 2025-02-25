import asyncio

from aiogram import Bot, Dispatcher

import settings
from containers import ServicesContainer
from handlers.callback import router as callback_router
from handlers.message import router as message_router
from middlewares import UserMiddleware, ChatMiddleware

bot = Bot(token=settings.TELEGRAM_TOKEN)

dp = Dispatcher()
dp.message.middleware(UserMiddleware())
dp.message.middleware(ChatMiddleware())
dp.callback_query.middleware(UserMiddleware())
dp.include_routers(message_router, callback_router)
# bot.dispatcher.add_router(message_router)
# bot.dispatcher.add_router(callback_router)

async def main():
    print(await bot.get_me())
    await dp.start_polling(bot)


services_container = ServicesContainer(bot=bot, fsm=object())
services_container.wire(['handlers.message',
                         'handlers.callback'])
if __name__ == '__main__':
    asyncio.run(main())
