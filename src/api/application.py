from advanced_alchemy.extensions.fastapi import AdvancedAlchemy
from fastapi import FastAPI
from starlette.templating import Jinja2Templates

from database.connection import async_config
from settings import BASE_DIR

app = FastAPI()

alchemy = AdvancedAlchemy(
    config=async_config,
    app=app
)

templates = Jinja2Templates(directory=BASE_DIR / 'api' / 'templates')

