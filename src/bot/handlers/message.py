from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from containers import ServicesContainer
from database.models import User, Chat
from bot.services import UserService, BotQueueService

router = Router()


@router.message(
    Command('start')
)
@inject
async def start_message_handler(event: Message,
                                user: User,
                                user_service: UserService = Provide[ServicesContainer.user_service]):
    await user_service.greet_user(event, user)


@router.message(
    Command('queues')
)
@inject
async def list_queues_handler(event: Message,
                              command: CommandObject,
                              user: User,
                              chat: Chat,
                              session=None,
                              queue_service: BotQueueService = Provide[ServicesContainer.bot_queue_service]):
    print(session)
    await queue_service.queue_list(event=event, user=user, chat=chat)


@router.message(
    Command('queue')
)
@inject
async def create_queue_handler(event: Message,
                               command: CommandObject,
                               user: User,
                               chat: Chat,
                               queue_service: BotQueueService = Provide[ServicesContainer.bot_queue_service]):
    await queue_service.create_queue_event(command.args, user, chat)

# @bots.simple_bot_handler(router,
#                          EventTypeFilter(BotEventType.MESSAGE_NEW),
#                          BotMentionedFilter(settings.VK_GROUP_ID),
#                          TextContainsFilter("очереди"),
#                          MessageFromConversationTypeFilter("from_chat"))
# @inject
# async def queue_list_handler(event: SimpleBotEvent,
#                              bot_queue_service: BotQueueService = Provide[ServicesContainer.bot_queue_service]):
#     await bot_queue_service.queue_list(event, event['user'], event['chat'])
#
#
# @bots.simple_bot_handler(router,
#                          EventTypeFilter(BotEventType.MESSAGE_NEW),
#                          BotMentionedFilter(settings.VK_GROUP_ID),
#                          TextContainsFilter("очередь"),
#                          MessageFromConversationTypeFilter("from_chat"))
# @inject
# async def queue_list_handler(event: SimpleBotEvent,
#                              bot_queue_service: BotQueueService = Provide[ServicesContainer.bot_queue_service]):
#     await bot_queue_service.create_queue_event(event, event['user'], event['chat'])
