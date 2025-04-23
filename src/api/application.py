from advanced_alchemy.extensions.fastapi import AdvancedAlchemy
from fastapi import FastAPI

from database.connection import async_config

app = FastAPI()

alchemy = AdvancedAlchemy(
    config=async_config,
    app=app
)


