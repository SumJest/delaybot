from aiogram import Router
from aiogram.types import Message, CallbackQuery
from dependency_injector.wiring import inject, Provide

from containers import ServicesContainer
from keyboards.types.queue_action import QueueActionCallbackFactory
from services import QueueService

router = Router()


@router.callback_query(QueueActionCallbackFactory.filter())
@inject
async def queue_action_handler(callback: CallbackQuery,
                               callback_data: QueueActionCallbackFactory,
                               user,
                               queue_service: QueueService = Provide[ServicesContainer.queue_service]):
    await queue_service.queue_action_event(callback, callback_data, user)
