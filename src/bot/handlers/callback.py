from aiogram import Router
from aiogram.types import CallbackQuery
from dependency_injector.wiring import inject, Provide

from containers import ServicesContainer
from bot.keyboards.types.queue_action import QueueActionCallbackFactory
from bot.services import BotQueueService

router = Router()


@router.callback_query(QueueActionCallbackFactory.filter())
async def queue_action_handler(callback: CallbackQuery,
                               callback_data: QueueActionCallbackFactory,
                               user,
                               services_container: ServicesContainer):
    await services_container.bot_queue_service.queue_action_event(callback, callback_data, user)
