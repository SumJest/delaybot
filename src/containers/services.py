from dependency_injector import containers, providers
from vkwave.api import APIOptionsRequestContext

from services import QueueService, UserService, ChatService


class ServicesContainer(containers.DeclarativeContainer):
    api_context = providers.Dependency(instance_of=APIOptionsRequestContext)
    queue_service = providers.Factory(
        QueueService,
        api_context=api_context
    )
    user_service = providers.Factory(
        UserService,
        api_context=api_context
    )
    chat_service = providers.Factory(
        ChatService,
        api_context=api_context
    )
