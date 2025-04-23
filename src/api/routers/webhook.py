import logging

from aiogram.types import Update
from fastapi import APIRouter, Request, Depends

from api.dependencies import get_services
from containers import ServicesContainer

router = APIRouter(tags=["telegram"])


@router.post("/webhook")
async def updates_webhook(request: Request, services_container: ServicesContainer = Depends(get_services)):
    logging.info("Received webhook request")
    dp = services_container.dp
    bot = services_container.bot
    update_data = await request.json()
    update = Update.model_validate(update_data)
    return await dp.feed_update(bot, update, services_container=services_container)
