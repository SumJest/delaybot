import logging

from aiogram.types import Update
from fastapi import APIRouter, Request

from bot.application import dp, bot

router = APIRouter(tags=["telegram"])


@router.post("/webhook")
async def updates_webhook(request: Request):
    logging.info("Received webhook request")
    update_data = await request.json()
    update = Update.model_validate(update_data)
    return await dp.feed_update(bot, update, session='asdasd')
