from advanced_alchemy.extensions.fastapi import AdvancedAlchemy
from fastapi import FastAPI
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from database.connection import async_config
from settings import BASE_DIR

app = FastAPI(swagger_ui_parameters={"persistAuthorization": True})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
alchemy = AdvancedAlchemy(
    config=async_config,
    app=app
)

templates = Jinja2Templates(directory=BASE_DIR / 'api' / 'templates')

