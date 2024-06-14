from dependency_injector.wiring import inject, Provide
from vkwave import bots
from vkwave.bots import DefaultRouter, SimpleBotEvent

from containers import ServicesContainer
from filters import CallbackKeysFilter
from services import QueueService

router = DefaultRouter()


@bots.simple_bot_handler(
    router,
    CallbackKeysFilter(['command', 'id'])
)
@inject
async def queue_action_handler(event: SimpleBotEvent,
                               queue_service: QueueService = Provide[ServicesContainer.queue_service]):
    await queue_service.queue_action_event(event, event['user'])
