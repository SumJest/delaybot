from api.routers import telegram_router, queue_router, html_router, queue_share_router, user_router
from containers.bot import BotContainer
from api.application import app
from bot.application import setup

from settings import BASE_URL, settings


@app.on_event('startup')
async def startup():
    bot_container = BotContainer()
    bot_container.config.telegram.token.from_value(settings.telegram.token)
    bot_container.wire(modules=[
        'containers.services',
        'bot.application'
    ])
    bot_info = await bot_container.bot().get_me()
    bot_container.config.telegram.username.from_value(bot_info.username)
    app.include_router(telegram_router, prefix='/telegram')
    app.include_router(queue_router, prefix='/queue')
    app.include_router(html_router, prefix='/html')
    app.include_router(queue_share_router, prefix='/queue-share')
    app.include_router(user_router, prefix='/user')
    await setup(BASE_URL + app.url_path_for('updates_webhook'))

