from dependency_injector import containers, providers
from bot.services import BotQueueService, UserService, ChatService


class ServicesContainer(containers.DeclarativeContainer):
    bot = providers.Dependency()
    fsm = providers.Dependency()
    queue_service = providers.Factory(
        BotQueueService,
        bot=bot
    )
    user_service = providers.Factory(
        UserService,
        bot=bot
    )
    chat_service = providers.Factory(
        ChatService,
        bot=bot,
        fsm=fsm
    )
