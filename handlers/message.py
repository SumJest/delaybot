from dependency_injector.wiring import Provide, inject
from vkwave import bots
from vkwave.bots import (DefaultRouter, PayloadFilter, MessageFromConversationTypeFilter, SimpleBotEvent,
                         EventTypeFilter, TextContainsFilter)
from vkwave.types.bot_events import BotEventType

import settings
from containers import ServicesContainer
from filters import BotMentionedFilter
from services import UserService, QueueService

router = DefaultRouter()


@bots.simple_bot_handler(router,
                         EventTypeFilter(BotEventType.MESSAGE_NEW),
                         PayloadFilter({'command': 'start'}),
                         MessageFromConversationTypeFilter("from_pm"))
@inject
async def start_message_handler(event: SimpleBotEvent,
                                user_service: UserService = Provide[ServicesContainer.user_service]):
    await user_service.greet_user(event, event['user'])


@bots.simple_bot_handler(router,
                         EventTypeFilter(BotEventType.MESSAGE_NEW),
                         BotMentionedFilter(settings.VK_GROUP_ID),
                         TextContainsFilter("очереди"),
                         MessageFromConversationTypeFilter("from_chat"))
@inject
async def queue_list_handler(event: SimpleBotEvent,
                             queue_service: QueueService = Provide[ServicesContainer.queue_service]):
    await queue_service.queue_list(event, event['user'], event['chat'])
