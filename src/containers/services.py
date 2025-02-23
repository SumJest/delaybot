from dependency_injector import containers, providers
from vkwave.api import APIOptionsRequestContext
from vkwave.bots import FiniteStateMachine

from services import QueueService, UserService, ChatService


class ServicesContainer(containers.DeclarativeContainer):
    bot = providers.Dependency()
    fsm = providers.Dependency()
    queue_service = providers.Factory(
        QueueService,
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
