from fastapi import FastAPI
from api.routers import telegram_router

app = FastAPI()

app.include_router(telegram_router, prefix='/telegram')
