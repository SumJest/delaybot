from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, \
    InlineKeyboardButton

from containers import ServicesContainer
from database.models import User, Chat

router = Router()


@router.message(
    Command('start')
)
async def start_message_handler(event: Message,
                                user: User,
                                services_container: ServicesContainer):
    return "Hi"


@router.message(
    Command('queues')
)
async def list_queues_handler(event: Message,
                              command: CommandObject,
                              user: User,
                              chat: Chat,
                              services_container: ServicesContainer):
    await services_container.bot_queue_service.queue_list(event=event, user=user, chat=chat)


@router.message(
    Command('queue')
)
async def create_queue_handler(event: Message,
                               command: CommandObject,
                               user: User,
                               chat: Chat,
                               services_container: ServicesContainer):
    await services_container.bot_queue_service.create_queue_event(command.args, user, chat)


@router.message(
    Command('webapp')
)
async def get_webapp_handler(event: Message,
                             services_container: ServicesContainer):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Открыть WebApp",
                web_app=WebAppInfo(url="https://delaybot.home.romaaaka.ru/")
            )
        ]
    ])

    await services_container.bot.send_message(
        chat_id=event.chat.id,
        text="Нажмите кнопку ниже, чтобы открыть WebApp:",
        reply_markup=keyboard
    )
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
