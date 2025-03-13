from api.application import app
from bot.application import setup

from settings import BASE_URL


@app.on_event('startup')
async def startup():
    await setup(BASE_URL + app.url_path_for('updates_webhook'))